package repositories

import (
	"context"
	"fmt"
	"time"
	"vacancy-matcher/internal/domain"
	"vacancy-matcher/internal/dto"

	"gorm.io/gorm"
)

type VacancyRepository interface {
	GetRelevant(ctx context.Context, filter dto.RelevantVacancyFilter) ([]dto.VacancyWithScore, error)
}

type vacancyRepository struct {
	db *gorm.DB
}

func NewVacancyRepository(db *gorm.DB) VacancyRepository {
	return &vacancyRepository{db: db}
}

func (r *vacancyRepository) GetRelevant(ctx context.Context, f dto.RelevantVacancyFilter) ([]dto.VacancyWithScore, error) {
	if len(f.Skills) == 0 {
		return []dto.VacancyWithScore{}, nil
	}

	sinceDT := time.Now().Add(-time.Duration(dto.DaysInterval) * 24 * time.Hour)

	sqlQuery := `
		SELECT 
			v.id,
			v.source,
			v.hash,
			v.link,
			v.company_name,
			v.salary,
			v.workplace_description,
			v.responsibilities,
			v.requirements,
			v.conditions,
			v.published_at,
			v.profession_id,
			skill_counts.total_skills_count,
			skill_counts.common_skills_count,
			common_skills_count * 100.0 / NULLIF(total_skills_count, 0) as base_similarity
		FROM (
			SELECT 
				vs.vacancy_id,
				COUNT(*) as total_skills_count,
				COUNT(CASE WHEN s.name = ANY($1::text[]) THEN 1 END) as common_skills_count
			FROM vacancy_processor.vacancy_skills vs
			JOIN vacancy_processor.skills s ON s.id = vs.skill_id
			GROUP BY vs.vacancy_id
		) skill_counts
		JOIN vacancy_processor.vacancies v ON v.id = skill_counts.vacancy_id
		WHERE 
			v.published_at >= $2
			AND skill_counts.total_skills_count > 0
			AND skill_counts.common_skills_count > 0
	`

	params := []interface{}{f.Skills, sinceDT}
	paramIdx := 3

	// Add WHERE clauses for filters
	if len(f.Sources) > 0 {
		sqlQuery += fmt.Sprintf(" AND v.source = ANY($%d::text[])", paramIdx)
		params = append(params, f.Sources)
		paramIdx++
	}

	if len(f.Professions) > 0 {
		sqlQuery += fmt.Sprintf(" AND EXISTS (SELECT 1 FROM vacancy_processor.professions p WHERE p.id = v.profession_id AND p.name = ANY($%d::text[]))", paramIdx)
		params = append(params, f.Professions)
		paramIdx++
	}

	if len(f.Grades) > 0 {
		sqlQuery += fmt.Sprintf(" AND EXISTS (SELECT 1 FROM vacancy_processor.vacancy_grades vg JOIN vacancy_processor.grades g ON g.id = vg.grade_id WHERE vg.vacancy_id = v.id AND g.name = ANY($%d::text[]))", paramIdx)
		params = append(params, f.Grades)
		paramIdx++
	}

	if len(f.WorkFormats) > 0 {
		sqlQuery += fmt.Sprintf(" AND EXISTS (SELECT 1 FROM vacancy_processor.vacancy_work_formats vwf JOIN vacancy_processor.work_formats wf ON wf.id = vwf.work_format_id WHERE vwf.vacancy_id = v.id AND wf.name = ANY($%d::text[]))", paramIdx)
		params = append(params, f.WorkFormats)
		paramIdx++
	}

	// Add minimum similarity filter
	sqlQuery += fmt.Sprintf(" AND (common_skills_count * 100.0 / NULLIF(total_skills_count, 0)) >= $%d", paramIdx)
	params = append(params, dto.MinSimilarityPercent)

	var results []struct {
		ID                   uint      `gorm:"column:id"`
		Source               string    `gorm:"column:source"`
		Hash                 string    `gorm:"column:hash"`
		Link                 string    `gorm:"column:link"`
		CompanyName          *string   `gorm:"column:company_name"`
		Salary               *string   `gorm:"column:salary"`
		WorkplaceDescription *string   `gorm:"column:workplace_description"`
		Responsibilities     *string   `gorm:"column:responsibilities"`
		Requirements         *string   `gorm:"column:requirements"`
		Conditions           *string   `gorm:"column:conditions"`
		PublishedAt          time.Time `gorm:"column:published_at"`
		ProfessionID         uint      `gorm:"column:profession_id"`
		TotalSkillsCount     int       `gorm:"column:total_skills_count"`
		CommonSkillsCount    int       `gorm:"column:common_skills_count"`
		BaseSimilarity       float64   `gorm:"column:base_similarity"`
	}

	err := r.db.WithContext(ctx).Raw(sqlQuery, params...).Scan(&results).Error
	if err != nil {
		return nil, err
	}

	// Calculate scores in Go and sort by score
	scores := make(map[uint]float64)
	vacancyIDs := make([]uint, 0, len(results))
	for _, r := range results {
		vacancyIDs = append(vacancyIDs, r.ID)

		// Calculate score components
		baseSimilarity := r.BaseSimilarity

		// Bonus for exceeding minimum skills count
		bonusMinSkills := float64(0)
		if r.CommonSkillsCount > dto.MinSkillsCount {
			bonusMinSkills = float64(r.CommonSkillsCount-dto.MinSkillsCount) * float64(dto.BonusMinSkill)
		}

		// Bonus for perfect match (all user skills in vacancy)
		subsetBonus := float64(0)
		if r.CommonSkillsCount == len(f.Skills) {
			subsetBonus = float64(dto.BestSkillsCountBonus)
		}

		// Bonus for vacancy relevance (recent vacancies)
		daysSincePublished := time.Since(r.PublishedAt).Hours() / 24
		relevanceBonus := float64(0)
		if daysSincePublished <= 7 {
			relevanceBonus = (7 - daysSincePublished) * float64(dto.DaysRelevanceBonus)
		}

		// Penalty for missing skills
		missingSkillsPenalty := float64(0)
		if len(f.Skills) > r.CommonSkillsCount {
			missingSkillsPenalty = float64(len(f.Skills)-r.CommonSkillsCount) * float64(dto.PenaltyMissingSkill)
		}

		// Total score
		totalScore := baseSimilarity + bonusMinSkills + subsetBonus + relevanceBonus - missingSkillsPenalty
		scores[r.ID] = totalScore
	}

	// Preload all vacancies with relations
	vacancyWithScores := make([]dto.VacancyWithScore, 0, len(vacancyIDs))
	if len(vacancyIDs) > 0 {
		var vacancies []domain.Vacancy
		err = r.db.WithContext(ctx).
			Preload("Profession").
			Preload("Grades").
			Preload("WorkFormats").
			Preload("Skills").
			Where("id IN ?", vacancyIDs).
			Find(&vacancies).Error
		if err != nil {
			return nil, err
		}

		// Combine vacancies with scores and sort by score
		for _, v := range vacancies {
			vacancyWithScores = append(vacancyWithScores, dto.VacancyWithScore{
				Vacancy: v,
				Score:   scores[v.ID],
			})
		}

		// Sort by score descending
		for i := 0; i < len(vacancyWithScores)-1; i++ {
			for j := i + 1; j < len(vacancyWithScores); j++ {
				if vacancyWithScores[i].Score < vacancyWithScores[j].Score {
					vacancyWithScores[i], vacancyWithScores[j] = vacancyWithScores[j], vacancyWithScores[i]
				}
			}
		}

		// Limit to top 50
		if len(vacancyWithScores) > 50 {
			vacancyWithScores = vacancyWithScores[:50]
		}
	}

	return vacancyWithScores, nil
}
