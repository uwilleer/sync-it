package domain

type Grade struct {
	ID   uint
	Name string
}

func (Grade) TableName() string {
	return "vacancy_processor.grades"
}
