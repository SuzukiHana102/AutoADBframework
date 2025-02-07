from typing import Type, TypeVar, List, Dict, Union, Optional,Any

from ..configs import Config
from ..utils.logging import get_logger
from .templates.connection_temp import ConnectionTemplate
from .templates.action_temp import ActionTemplate
from .templates.task_client_temp import TaskClientTemplate
from .templates.task_node_temp import TaskContainerTemplate
from .templates.decision_temp import DecisionTemplate
from .templates.recognizer_temp import RecognizerTemplate

T = TypeVar('T')
class Factory:
    """工厂类，用于管理和创建各种模板类的实例"""
    logger = get_logger('framework.factory')

    VALID_CLASS_NAME = ['connection', 'action', 'task_client', 'task_container', 'decision', 'recognizer']
    # 已注册的各类模板类列表
    REGISTERED_CONNECTION_CLASS = [ConnectionTemplate]
    REGISTERED_ACTION_CLASS = [ActionTemplate]
    REGISTERED_TASK_CLIENT_CLASS = [TaskClientTemplate]
    REGISTERED_TASK_CONTAINER_CLASS = [TaskContainerTemplate]
    REGISTERED_DECISION_CLASS = [DecisionTemplate]
    REGISTERED_RECOGNIZER_CLASS = [RecognizerTemplate]

    @staticmethod
    def register_class(list2register, class_: Type[T], mode='append') -> None:
        """注册新的模板类
        
        Args:
            list2register: 要注册的目标列表
            class_: 要注册的类
            mode: 注册模式
                - 'append': 在列表末尾添加
                - 'prepend': 在列表开头添加
                - 'replace': 替换整个列表
        """
        if mode == 'append':
            list2register.append(class_)
        elif mode == 'prepend':
            list2register.insert(0, class_)
        elif mode == 'replace':
            list2register = [class_]
        else:
            raise ValueError(f"Invalid mode: {mode}")

    @staticmethod
    def register() -> None:
        """注册装饰器，用于注册新的模板类
        
        Args:
            append_mode: 添加模式，'replace'表示替换当前类，'ignore'表示在当前类为空时才设置
        """
        def wrapper(class_: Type[T]) -> None:
            if issubclass(class_, ConnectionTemplate):
                Factory.register_class(Factory.REGISTERED_CONNECTION_CLASS, class_)
            elif issubclass(class_, ActionTemplate):
                Factory.register_class(Factory.REGISTERED_ACTION_CLASS, class_)
            elif issubclass(class_, TaskClientTemplate):
                Factory.register_class(Factory.REGISTERED_TASK_CLIENT_CLASS, class_)
            elif issubclass(class_, TaskContainerTemplate):
                Factory.register_class(Factory.REGISTERED_TASK_CONTAINER_CLASS, class_)
            elif issubclass(class_, DecisionTemplate):
                Factory.register_class(Factory.REGISTERED_DECISION_CLASS, class_)
            elif issubclass(class_, RecognizerTemplate):
                Factory.register_class(Factory.REGISTERED_RECOGNIZER_CLASS, class_)
            else:
                raise ValueError(f"{class_} is not a subclass of ConnectionTemplate, ActionTemplate, TaskClientTemplate, TaskContainerTemplate, or DecisionTemplate")
        return wrapper
    
    @staticmethod
    def get_all_registed() -> Dict[str, List[Type[T]]]:
        """获取所有已注册的模板类"""
        return {
            'connection': Factory.REGISTERED_CONNECTION_CLASS,
            'action': Factory.REGISTERED_ACTION_CLASS,
            'task_client': Factory.REGISTERED_TASK_CLIENT_CLASS,
            'task_container': Factory.REGISTERED_TASK_CONTAINER_CLASS,
            'decision': Factory.REGISTERED_DECISION_CLASS,
            'recognizer': Factory.REGISTERED_RECOGNIZER_CLASS
        }
    
    @staticmethod
    def current_classes() -> Dict[str, Type[T]]:
        """获取当前使用的类"""
        return {
            'connection': Factory.CURRENT_CONNECTION_CLASS,
            'action': Factory.CURRENT_ACTION_CLASS,
            'task_client': Factory.CURRENT_TASK_CLIENT_CLASS,
            'task_container': Factory.CURRENT_TASK_CONTAINER_CLASS,
            'decision': Factory.CURRENT_DECISION_CLASS,
            'recognizer': Factory.REGISTERED_RECOGNIZER_CLASS
        }

    @staticmethod
    def generate_form_registed(registed:List[Type[T]], class_idx: Optional[Union[int,str]] = None, **kwargs) -> T:
        if len(registed) <= 0:
            raise ValueError("No registered classes")
        
        if class_idx is None:
            class_ = registed[-1]
        elif isinstance(class_idx, int):
            class_ = registed[class_idx]
        elif isinstance(class_idx, str):
            class_ = None
            for class_ in registed:
                if class_idx in class_.__name__:
                    class_ = class_
                    break
            if class_ is None:
                raise ValueError(f"Invalid class index: {class_idx}")
            
    @staticmethod
    def generate(type_name: str,class_idx: Optional[Union[int,str]] = None, **kwargs) -> T:
        assert type_name in Factory.VALID_CLASS_NAME, f"Invalid type name: {type_name}"
        if type_name == 'connection':
            class_ = Factory.generate_form_registed(Factory.REGISTERED_CONNECTION_CLASS, class_idx, **kwargs)
        elif type_name == 'action':
            class_ = Factory.generate_form_registed(Factory.REGISTERED_ACTION_CLASS, class_idx, **kwargs)
        elif type_name == 'task_client':
            class_ = Factory.generate_form_registed(Factory.REGISTERED_TASK_CLIENT_CLASS, class_idx, **kwargs)
        elif type_name == 'task_container':
            class_ = Factory.generate_form_registed(Factory.REGISTERED_TASK_CONTAINER_CLASS, class_idx, **kwargs)
        elif type_name == 'decision':
            class_ = Factory.generate_form_registed(Factory.REGISTERED_DECISION_CLASS, class_idx, **kwargs)
        elif type_name == 'recognizer':
            class_ = Factory.generate_form_registed(Factory.REGISTERED_RECOGNIZER_CLASS, class_idx, **kwargs)
        else:
            raise ValueError(f"Invalid type name: {type_name}")
                
        return class_
