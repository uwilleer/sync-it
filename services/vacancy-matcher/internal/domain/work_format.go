package domain

type WorkFormat struct {
	ID   uint   `json:"id"`
	Name string `json:"name"`
}

func (WorkFormat) TableName() string {
	return "vacancy_processor.work_formats"
}
