package domain

type Profession struct {
	ID   uint
	Name string
}

func (Profession) TableName() string {
	return "vacancy_processor.professions"
}
