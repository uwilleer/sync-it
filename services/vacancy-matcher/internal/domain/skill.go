package domain

type Skill struct {
	ID   uint   `json:"id"`
	Name string `json:"name"`
}

func (Skill) TableName() string {
	return "vacancy_processor.skills"

}
