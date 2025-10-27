package dto

type VacancyFilter struct {
	Limit       *int
	Professions []string
	Grades      []string
	WorkFormats []string
	Sources     []string
}
