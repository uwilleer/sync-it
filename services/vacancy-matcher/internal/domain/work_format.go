package domain

type WorkFormat struct {
	ID   uint
	Name string
}

func (WorkFormat) TableName() string {
	return "vacancy_processor.work_formats"
}
