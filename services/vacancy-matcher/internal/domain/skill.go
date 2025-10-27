package domain

type Skill struct {
	ID   uint
	Name string
}

func (Skill) TableName() string {
	return "vacancy_processor.skills"

}
