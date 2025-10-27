package handlers

import (
	"encoding/json"
	"net/http"
	"vacancy-matcher/internal/dto"

	"vacancy-matcher/internal/services"
)

type VacancyHandler struct {
	service services.VacancyService
}

func NewVacancyHandler(svc services.VacancyService) *VacancyHandler {
	return &VacancyHandler{service: svc}
}

func (h *VacancyHandler) GetRelevant(w http.ResponseWriter, r *http.Request) {
	var filter dto.RelevantVacancyFilter

	if err := json.NewDecoder(r.Body).Decode(&filter); err != nil {
		http.Error(w, "invalid request body", http.StatusBadRequest)
		return
	}

	result, err := h.service.GetRelevant(r.Context(), filter)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	response := dto.VacancyWithNeighborsResponse{
		Result: result,
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}
