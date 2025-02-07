from ...messages.task_msg import TaskMsg

class ActionTemplate:
    SUPPORTED_ACTIONS = []

    @classmethod
    def register_support(cls,func):
        cls.SUPPORTED_ACTIONS.append(func.__name__)
        return func
    
    def apply(self, action_name: str, *action_args, **action_kwargs) -> TaskMsg:
        if action_name.startswith('_'):
            raise ValueError(f"Action {action_name} is not allowed to be applied")
        if action_name not in self.SUPPORTED_ACTIONS:
            raise ValueError(f"Action {action_name} is not supported")
        function = getattr(self, action_name)
        result = function(*action_args, **action_kwargs)
        self.logger.info(f'Action {action_name} is applied with {action_args} and {action_kwargs}')
        return result
