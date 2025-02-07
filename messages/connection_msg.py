import enum

class ConnectionMsg:
    class State(enum.Enum):
        SUCCESS = enum.auto()
        ERROR = enum.auto()

    def __init__(self, stdout: str, stderr: str, state_code: int) -> None:
        self.stdout = stdout
        self.stderr = stderr
        self.set_state(state_code)

    def set_state(self, state_code: int) -> None:
        if state_code == 0:
            self.state = ConnectionMsg.State.SUCCESS
        elif state_code == 1:
            self.state = ConnectionMsg.State.ERROR
        else:
            raise ValueError(f"Invalid state code: {state_code}")

    @property
    def is_success(self) -> bool:
        return self.state.value == ConnectionMsg.State.SUCCESS.value
    
    @property
    def is_error(self) -> bool:
        return self.state.value == ConnectionMsg.State.ERROR.value
    