from typing import Optional, Any
import enum

class TaskMsg:
    class TaskResult:
        def __init__(self, result: Optional[Any], stderr: Optional[str]) -> None:
            self.result = result
            self.stderr = stderr
    
    class SwitchableResult(TaskResult):
        def __init__(self, result: Optional[Any], stderr: Optional[str], switch_to: int) -> None:
            self.result = result
            self.stderr = stderr
            self.switch_to = switch_to

    class State(enum.Enum):
        SUCCESS = enum.auto()
        ERROR = enum.auto()
        FAILURE = enum.auto()

    def __init__(self, result: Optional[Any], stderr: Optional[str], state_code: int, switch_to: Optional[int] = None) -> None:
        self.result = TaskMsg.TaskResult(result, stderr) if switch_to is None else TaskMsg.SwitchableResult(result, stderr, switch_to)
        self.set_state(state_code)

    def set_state(self, state_code: int) -> 'TaskMsg':
        if state_code == 0:
            self.state = TaskMsg.State.SUCCESS
        elif state_code == 1:
            self.state = TaskMsg.State.ERROR
        elif state_code == 2:
            self.state = TaskMsg.State.FAILURE
        else:
            raise ValueError(f"Invalid state code: {state_code}")
        return self

    @property
    def is_success(self) -> bool:
        return self.state.value == TaskMsg.State.SUCCESS.value
    
    @property
    def is_error(self) -> bool:
        return self.state.value == TaskMsg.State.ERROR.value
    
    @property
    def is_failure(self) -> bool:
        return self.state.value == TaskMsg.State.FAILURE.value
    
    @property
    def switchable(self) -> bool:
        return isinstance(self.result, TaskMsg.SwitchableResult)
    
    @property
    def switch_to(self) -> int:
        return self.result.switch_to
