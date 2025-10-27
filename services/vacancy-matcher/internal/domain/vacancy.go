package domain

import (
	"time"
)

type Vacancy struct {
	ID               uint
	Source           string
	Hash             string
	Link             string
	CompanyName      *string
	Salary           *string
	Workplace        *string
	Responsibilities *string
	Requirements     *string
	Conditions       *string
	PublishedAt      time.Time

	ProfessionID uint
	Profession   *Profession
	Grades       []*Grade      `gorm:"many2many:vacancy_processor.vacancy_grades"`
	WorkFormats  []*WorkFormat `gorm:"many2many:vacancy_processor.vacancy_work_formats"`
	Skills       []*Skill      `gorm:"many2many:vacancy_processor.vacancy_skills"`
}

func (Vacancy) TableName() string {
	return "vacancy_processor.vacancies"
}
