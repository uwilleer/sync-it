package handlers

import (
	"encoding/json"
	"net/http"
	"strconv"
	"vacancy-matcher/internal/dto"

	"vacancy-matcher/internal/services"
)

type VacancyHandler struct {
	service services.VacancyService
}

func NewVacancyHandler(svc services.VacancyService) *VacancyHandler {
	return &VacancyHandler{service: svc}
}

// GET /api/vacancies?source=xxx&limit=10... (параметры фильтра из query)
func (h *VacancyHandler) ListVacancies(w http.ResponseWriter, r *http.Request) {
	query := r.URL.Query()
	filter := dto.VacancyFilter{}

	if limitStr := query.Get("limit"); limitStr != "" {
		limit, err := strconv.Atoi(limitStr)
		if err != nil || limit <= 0 {
			http.Error(w, "limit must be positive integer", http.StatusBadRequest)
			return
		}
		filter.Limit = &limit
	}

	result, err := h.service.ListVacancies(r.Context(), filter)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(result)
}

// FIXME https://www.perplexity.ai/search/privedi-primer-best-practices-FIpyNHdASXKJQhseSeng.g
