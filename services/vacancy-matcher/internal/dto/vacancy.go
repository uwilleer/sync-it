package dto

import "vacancy-matcher/internal/domain"

type VacancyFilter struct {
	Limit       *int
	Professions []string
	Grades      []string
	WorkFormats []string
	Sources     []string
}

type RelevantVacancyFilter struct {
	CurrentVacancyID *int     `json:"current_vacancy_id"`
	Professions      []string `json:"professions"`
	Grades           []string `json:"grades"`
	WorkFormats      []string `json:"work_formats"`
	Sources          []string `json:"sources"`
	Skills           []string `json:"skills"`
}

type VacancyWithScore struct {
	Vacancy domain.Vacancy
	Score   float64
}

type VacancyWithNeighbors struct {
	PrevID  *int            `json:"prev_id"`
	NextID  *int            `json:"next_id"`
	Vacancy *domain.Vacancy `json:"vacancy"`
}

type VacancyWithNeighborsResponse struct {
	Result VacancyWithNeighbors `json:"result"`
}

// Constants for relevance calculation
const (
	MinSimilarityPercent = 60 // Минимальное соотношение совпадающих навыков
	MinSkillsCount       = 5
	BonusMinSkill        = 7 // Бонус за каждый навык сверх MIN_SKILLS_COUNT
	PenaltyMissingSkill  = 5 // Штраф за каждый отсутствующий навык
	BestSkillsCountBonus = 15
	DaysInterval         = 21
	DaysRelevanceBonus   = 15
)
