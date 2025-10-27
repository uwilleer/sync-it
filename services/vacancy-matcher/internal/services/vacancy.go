package services

import (
	"context"
	"vacancy-matcher/internal/domain"
	"vacancy-matcher/internal/dto"
	"vacancy-matcher/internal/repositories"
)

type VacancyService interface {
	GetRelevant(ctx context.Context, filter dto.RelevantVacancyFilter) (dto.VacancyWithNeighbors, error)
}

type vacancyService struct {
	repo repositories.VacancyRepository
}

func NewVacancyService(repo repositories.VacancyRepository) VacancyService {
	return &vacancyService{repo: repo}
}

func (s *vacancyService) GetRelevant(ctx context.Context, filter dto.RelevantVacancyFilter) (dto.VacancyWithNeighbors, error) {
	vacanciesWithScores, err := s.repo.GetRelevant(ctx, filter)
	if err != nil {
		return dto.VacancyWithNeighbors{}, err
	}

	// Convert to domain.Vacancy slice for processing
	vacancies := make([]domain.Vacancy, len(vacanciesWithScores))
	for i, vws := range vacanciesWithScores {
		vacancies[i] = vws.Vacancy
	}

	// Find current vacancy and neighbors
	var currentIndex int = -1
	var currentVacancy *domain.Vacancy
	var prevID, nextID *int

	if filter.CurrentVacancyID != nil && len(vacancies) > 0 {
		// Find current vacancy index
		for i, v := range vacancies {
			if v.ID == uint(*filter.CurrentVacancyID) {
				currentIndex = i
				break
			}
		}

		if currentIndex >= 0 {
			// Get current vacancy
			currentVacancy = &vacancies[currentIndex]

			// Get previous ID
			if currentIndex > 0 {
				prev := int(vacancies[currentIndex-1].ID)
				prevID = &prev
			}

			// Get next ID
			if currentIndex < len(vacancies)-1 {
				next := int(vacancies[currentIndex+1].ID)
				nextID = &next
			}
		}
	} else if len(vacancies) > 0 {
		// If no current vacancy specified, return first one
		currentVacancy = &vacancies[0]
		if len(vacancies) > 1 {
			next := int(vacancies[1].ID)
			nextID = &next
		}
	}

	return dto.VacancyWithNeighbors{
		PrevID:  prevID,
		NextID:  nextID,
		Vacancy: currentVacancy,
	}, nil
}
