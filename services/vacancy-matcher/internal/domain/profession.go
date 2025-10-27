package domain

type Profession struct {
	ID   uint   `json:"id"`
	Name string `json:"name"`
}

func (Profession) TableName() string {
	return "vacancy_processor.professions"
}
