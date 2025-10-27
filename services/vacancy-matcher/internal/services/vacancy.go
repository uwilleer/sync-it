package services

import (
	"context"
	"vacancy-matcher/internal/domain"
	"vacancy-matcher/internal/dto"
	"vacancy-matcher/internal/repositories"
)

type VacancyService interface {
	ListVacancies(ctx context.Context, filter dto.VacancyFilter) ([]domain.Vacancy, error)
}

type vacancyService struct {
	repo repositories.VacancyRepository
}

func NewVacancyService(repo repositories.VacancyRepository) VacancyService {
	return &vacancyService{repo: repo}
}

func (s *vacancyService) ListVacancies(ctx context.Context, filter dto.VacancyFilter) ([]domain.Vacancy, error) {
	return s.repo.List(ctx, filter)
}
