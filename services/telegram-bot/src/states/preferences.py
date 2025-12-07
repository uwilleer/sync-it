from aiogram.fsm.state import State, StatesGroup


class PreferencesState(StatesGroup):
    waiting_for_data = State()
    waiting_toggle_skills = State()
