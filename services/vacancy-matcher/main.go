package main

import (
    "encoding/json"
    "log"
    "net/http"
    "os"
    "sort"
    "strconv"
    "strings"
    "time"

    "gorm.io/driver/postgres"
    "gorm.io/gorm"
)

// GORM models mapped to existing tables
type Vacancy struct {
    ID           int        `gorm:"column:id;primaryKey" json:"id"`
    Source       string     `gorm:"column:source" json:"source"`
    PublishedAt  time.Time  `gorm:"column:published_at" json:"published_at"`
    ProfessionID *int       `gorm:"column:profession_id" json:"profession_id"`
    Profession   Profession `gorm:"foreignKey:ProfessionID" json:"profession"`
    Skills       []Skill    `gorm:"many2many:vacancy_skills" json:"skills"`
    Grades       []Grade    `gorm:"many2many:vacancy_grades" json:"grades"`
    WorkFormats  []WorkFormat `gorm:"many2many:vacancy_work_formats" json:"work_formats"`
}

func (Vacancy) TableName() string { return "vacancies" }

type Profession struct {
    ID   int    `gorm:"column:id;primaryKey" json:"id"`
    Name string `gorm:"column:name" json:"name"`
}

func (Profession) TableName() string { return "professions" }

type Grade struct {
    ID   int    `gorm:"column:id;primaryKey" json:"id"`
    Name string `gorm:"column:name" json:"name"`
}

func (Grade) TableName() string { return "grades" }

type WorkFormat struct {
    ID   int    `gorm:"column:id;primaryKey" json:"id"`
    Name string `gorm:"column:name" json:"name"`
}

func (WorkFormat) TableName() string { return "work_formats" }

type Skill struct {
    ID   int    `gorm:"column:id;primaryKey" json:"id"`
    Name string `gorm:"column:name" json:"name"`
}

func (Skill) TableName() string { return "skills" }

// Request/Response payloads
type matchRequest struct {
    Professions []string `json:"professions"`
    Grades      []string `json:"grades"`
    WorkFormats []string `json:"work_formats"`
    Skills      []string `json:"skills"`
    Sources     []string `json:"sources"`
}

type matchResponse struct {
    VacancyIDs []int `json:"vacancy_ids"`
}

// Constants matching Python repository
const (
    minSimilarityPercent = 60
    minSkillsCount       = 3
    bonusMinSkill        = 3
    daysInterval         = 21
    daysRelevanceBonus   = 5
)

type server struct {
    db *gorm.DB
}

func main() {
    db := mustInitDB()
    srv := &server{db: db}

    mux := http.NewServeMux()
    mux.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
        writeJSON(w, http.StatusOK, map[string]string{"status": "Healthy"})
    })
    mux.HandleFunc("/api/v1/match", srv.handleMatch)

    host := getenvDefault("ENV_SERVICE_INTERNAL_HOST", "0.0.0.0")
    port := getenvDefault("ENV_SERVICE_INTERNAL_PORT", "8080")
    addr := host + ":" + port

    log.Printf("vacancy-matcher listening on %s", addr)
    if err := http.ListenAndServe(addr, logRequests(mux)); err != nil {
        log.Fatalf("server error: %v", err)
    }
}

func (s *server) handleMatch(w http.ResponseWriter, r *http.Request) {
    if r.Method != http.MethodPost {
        http.Error(w, http.StatusText(http.StatusMethodNotAllowed), http.StatusMethodNotAllowed)
        return
    }

    var req matchRequest
    if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
        http.Error(w, "invalid JSON", http.StatusBadRequest)
        return
    }

    // Early exit if no skills
    if len(req.Skills) == 0 {
        writeJSON(w, http.StatusOK, matchResponse{VacancyIDs: []int{}})
        return
    }

    // Base query: recent vacancies with preloads
    cutoff := time.Now().UTC().Add(-daysInterval * 24 * time.Hour)
    q := s.db.Model(&Vacancy{}).
        Select("distinct vacancies.*").
        Where("vacancies.published_at >= ?", cutoff).
        Preload("Profession").
        Preload("Grades").
        Preload("WorkFormats").
        Preload("Skills")

    if len(req.Professions) > 0 {
        q = q.Joins("JOIN professions ON professions.id = vacancies.profession_id").
            Where("professions.name IN ?", req.Professions)
    }

    if len(req.Grades) > 0 {
        q = q.Joins("JOIN vacancy_grades vg ON vg.vacancy_id = vacancies.id").
            Joins("JOIN grades ON grades.id = vg.grade_id").
            Where("grades.name IN ?", req.Grades)
    }

    if len(req.WorkFormats) > 0 {
        q = q.Joins("JOIN vacancy_work_formats vw ON vw.vacancy_id = vacancies.id").
            Joins("JOIN work_formats ON work_formats.id = vw.work_format_id").
            Where("work_formats.name IN ?", req.WorkFormats)
    }

    if len(req.Sources) > 0 {
        q = q.Where("vacancies.source IN ?", req.Sources)
    }

    var vacancies []Vacancy
    if err := q.Order("vacancies.id").Find(&vacancies).Error; err != nil {
        log.Printf("db query failed: %v", err)
        http.Error(w, "db query failed", http.StatusInternalServerError)
        return
    }

    userSkills := toLowerSet(req.Skills)

    type scored struct {
        score   float64
        vacancyID int
    }
    results := make([]scored, 0, len(vacancies))

    now := time.Now().UTC()
    for _, v := range vacancies {
        if len(v.Skills) == 0 {
            continue
        }

        vacancySkills := make(map[string]struct{}, len(v.Skills))
        for _, s := range v.Skills {
            vacancySkills[strings.ToLower(s.Name)] = struct{}{}
        }

        // Intersection
        commonCount := 0
        for skill := range userSkills {
            if _, ok := vacancySkills[skill]; ok {
                commonCount++
            }
        }
        if commonCount == 0 {
            continue
        }

        similarity := (float64(commonCount) / float64(len(vacancySkills))) * 100.0
        if similarity < minSimilarityPercent {
            continue
        }

        if commonCount > minSkillsCount {
            similarity += float64((commonCount - minSkillsCount) * bonusMinSkill)
        }

        // Perfect subset bonus
        isSubset := true
        for us := range userSkills {
            if _, ok := vacancySkills[us]; !ok {
                isSubset = false
                break
            }
        }
        if isSubset {
            similarity += 20
        }

        // Recency bonus
        daysSince := int(now.Sub(v.PublishedAt).Hours() / 24)
        if bonus := (7 - daysSince) * daysRelevanceBonus; bonus > 0 {
            similarity += float64(bonus)
        }

        if similarity >= minSimilarityPercent {
            results = append(results, scored{score: similarity, vacancyID: v.ID})
        }
    }

    sort.Slice(results, func(i, j int) bool { return results[i].score > results[j].score })
    if len(results) > 50 {
        results = results[:50]
    }

    ids := make([]int, 0, len(results))
    for _, r := range results {
        ids = append(ids, r.vacancyID)
    }

    writeJSON(w, http.StatusOK, matchResponse{VacancyIDs: ids})
}

func mustInitDB() *gorm.DB {
    host := mustGetenv("DATABASE_HOST")
    port := mustGetenv("DATABASE_PORT")
    dbname := mustGetenv("DATABASE_DB")
    user := mustGetenv("DATABASE_USER")
    pass := mustGetenv("DATABASE_PASSWORD")

    // postgres DSN for gorm
    dsn := "host=" + host + " user=" + user + " password=" + pass + " dbname=" + dbname + " port=" + port + " sslmode=disable TimeZone=UTC"
    db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{})
    if err != nil {
        log.Fatalf("failed to connect database: %v", err)
    }

    // Verify connection
    sqlDB, err := db.DB()
    if err != nil {
        log.Fatalf("failed to get sql.DB: %v", err)
    }
    sqlDB.SetMaxOpenConns(25)
    sqlDB.SetMaxIdleConns(25)
    sqlDB.SetConnMaxLifetime(5 * time.Minute)
    if err := sqlDB.Ping(); err != nil {
        log.Fatalf("database ping failed: %v", err)
    }

    return db
}

func writeJSON(w http.ResponseWriter, status int, v any) {
    w.Header().Set("Content-Type", "application/json")
    w.WriteHeader(status)
    _ = json.NewEncoder(w).Encode(v)
}

func getenvDefault(key, def string) string {
    if v := os.Getenv(key); v != "" {
        return v
    }
    return def
}

func mustGetenv(key string) string {
    v := os.Getenv(key)
    if v == "" {
        log.Fatalf("missing required env var %s", key)
    }
    return v
}

func logRequests(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        start := time.Now()
        next.ServeHTTP(w, r)
        dur := time.Since(start)
        log.Printf("%s %s %s %s", r.RemoteAddr, r.Method, r.URL.Path, dur.String())
    })
}

func atoiDefault(s string, def int) int {
    n, err := strconv.Atoi(s)
    if err != nil {
        return def
    }
    return n
}

func toLowerSet(items []string) map[string]struct{} {
    set := make(map[string]struct{}, len(items))
    for _, it := range items {
        if it == "" {
            continue
        }
        set[strings.ToLower(it)] = struct{}{}
    }
    return set
}

