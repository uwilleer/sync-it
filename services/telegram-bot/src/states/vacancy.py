from aiogram.fsm.state import State, StatesGroup


__all__ = ["VacancyState"]


class VacancyState(StatesGroup):
    waiting_for_skills = State()
