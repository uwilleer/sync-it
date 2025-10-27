package domain

type Grade struct {
	ID   uint   `json:"id"`
	Name string `json:"name"`
}

func (Grade) TableName() string {
	return "vacancy_processor.grades"
}
