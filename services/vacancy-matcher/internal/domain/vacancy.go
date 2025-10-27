package domain

import (
	"time"
)

type Vacancy struct {
	ID                   uint      `json:"id"`
	Source               string    `json:"source"`
	Hash                 string    `json:"hash"`
	Link                 string    `json:"link"`
	CompanyName          *string   `json:"company_name"`
	Salary               *string   `json:"salary"`
	WorkplaceDescription *string   `gorm:"column:workplace_description" json:"workplace_description"`
	Responsibilities     *string   `json:"responsibilities"`
	Requirements         *string   `json:"requirements"`
	Conditions           *string   `json:"conditions"`
	PublishedAt          time.Time `json:"published_at"`

	ProfessionID uint          `json:"-"`
	Profession   *Profession   `json:"profession"`
	Grades       []*Grade      `gorm:"many2many:vacancy_processor.vacancy_grades" json:"grades"`
	WorkFormats  []*WorkFormat `gorm:"many2many:vacancy_processor.vacancy_work_formats" json:"work_formats"`
	Skills       []*Skill      `gorm:"many2many:vacancy_processor.vacancy_skills" json:"skills"`
}

func (Vacancy) TableName() string {
	return "vacancy_processor.vacancies"
}
