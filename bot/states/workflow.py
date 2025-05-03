from aiogram.fsm.state import State, StatesGroup

class WorkStates(StatesGroup):
    waiting_for_selfie = State()
    waiting_for_location = State()
