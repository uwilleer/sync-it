package main

import (
	"log"
	"net/http"
	"os"
	"vacancy-matcher/internal/handlers"
	"vacancy-matcher/internal/repositories"
	"vacancy-matcher/internal/services"
	"vacancy-matcher/pkg/db"
)

func main() {
	dbConn := db.MustInit()
	repo := repositories.NewVacancyRepository(dbConn)
	svc := services.NewVacancyService(repo)
	h := handlers.NewVacancyHandler(svc)

	http.HandleFunc("/health", handlers.Healthcheck)
	http.HandleFunc("/api/v1/vacancies/match", h.GetRelevant)

	port := os.Getenv("ENV_SERVICE_INTERNAL_PORT")
	if port == "" {
		log.Fatal("ENV_SERVICE_INTERNAL_PORT env variable must be set")
	}

	addr := ":" + port
	log.Printf("Starting server on %s...\n", addr)
	log.Fatal(http.ListenAndServe(addr, nil))
}
