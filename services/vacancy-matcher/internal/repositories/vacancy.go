package repositories

import (
	"context"
	"vacancy-matcher/internal/domain"
	"vacancy-matcher/internal/dto"

	"gorm.io/gorm"
)

type VacancyRepository interface {
	List(ctx context.Context, filter dto.VacancyFilter) ([]domain.Vacancy, error)
}

type vacancyRepository struct {
	db *gorm.DB
}

func NewVacancyRepository(db *gorm.DB) VacancyRepository {
	return &vacancyRepository{db: db}
}

func (r *vacancyRepository) List(ctx context.Context, f dto.VacancyFilter) ([]domain.Vacancy, error) {
	var vacancies []domain.Vacancy

	query := r.db.WithContext(ctx).Preload("Profession").Preload("Grades").
		Preload("WorkFormats").Preload("Skills").Order("published_at desc")

	if f.Limit != nil {
		query = query.Limit(*f.Limit)
	} else {
		query = query.Limit(100)
	}
	if len(f.Professions) > 0 {
		query = query.Joins("JOIN professions p ON p.id = vacancies.profession_id").
			Where("p.name IN ?", f.Professions)
	}
	if len(f.Grades) > 0 {
		query = query.Joins("JOIN grades g ON g.id = vacancies.grade_id").
			Where("g.name IN ?", f.Grades)
	}
	if len(f.WorkFormats) > 0 {
		query = query.Joins("JOIN work_formats wf ON wf.id = vacancies.work_format_id").
			Where("wf.name IN ?", f.WorkFormats)
	}
	if len(f.Sources) > 0 {
		query = query.Where("source IN ?", f.Sources)
	}

	err := query.Find(&vacancies).Error
	return vacancies, err
}
