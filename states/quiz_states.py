from aiogram.dispatcher.filters.state import State, StatesGroup

class QuizState(StatesGroup):
    choose_direction = State()
    choose_technology = State()
    choose_question_count = State()
    answering = State()