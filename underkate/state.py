from typing import Dict, Any


State = Dict[str, Any]
_state: State = {}


def get_state() -> State:
    global _state
    return _state


def set_state(state: State):
    global _state
    _state = state
