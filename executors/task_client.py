from typing import Optional,List,Type,TypeVar,Union,Dict,Tuple
import json

from ..registry.client_factory import Factory
from ..registry.templates.connection_temp import ConnectionTemplate
from ..registry.templates.action_temp import ActionTemplate
from ..registry.templates.task_client_temp import TaskClientTemplate
from ..registry.templates.task_node_temp import TaskContainerTemplate
from ..registry.templates.decision_temp import DecisionTemplate
from ..registry.templates.recognizer_temp import RecognizerTemplate
from ..messages.task_msg import TaskMsg
from ..utils.logging import get_logger

T = TypeVar('T')
class BaseTaskClient(TaskClientTemplate):
    
    """基础任务客户端类"""
    def __init__(self) -> None:
        self.action_handler : Optional[ActionTemplate] = None
        self.decision_maker : Optional[DecisionTemplate] = None
        self.supported_task_container_types : List[Type[TaskContainerTemplate]] = []
        self.setup()

        self.logger = get_logger("framework.{self.__class__.__name__}")

    def setup(self):
        self.decision_maker = Factory.generate('decision')()
        registered_recognizers_classes = Factory.get_all_registed()['recognizer']
        recognizers = [ins() for ins in registered_recognizers_classes]
        connection = Factory.generate('connection')()
        self.action_handler = Factory.generate('action')().setup(connection,recognizers)
        self.supported_task_container_types = Factory.get_all_registed()['task_container']
        return self
    
    def generate_container(self,type_str:Optional[str]=None):
        if self.supported_task_container_types is None or len(self.supported_task_container_types) == 0:
            raise ValueError("No supported task container types")
        if type_str is None:
            return self.supported_task_container_types[0]()
        else:
            class_ = None
            for cls in self.supported_task_container_types:
                if cls.__name__ == type_str:
                    class_ = cls
                    break
            if class_ is None:
                raise ValueError(f"No supported task container type: {type_str}")
            return class_()
        
    def run_node(self,container:TaskContainerTemplate,
                 node:Optional[TaskContainerTemplate.TaskNode],
                 actions_msgs:List[TaskMsg]=[])->Optional[List[TaskMsg]]:
        """
        运行流程 (不包含container的初始化)：
            1.获取container的初始node
            2.判断当前node是action(action列表)还是subtask
            3.如果是action，则使用action_handler执行action
            4.如果是subtask，则临时复制一个task node，设置好临时参数后运行
            5.维护stack设置下一个node
            6.回到2直到node为空
        """
        if node is None:
            return None
        action_list = node.all_actions
        exe_mode = node.mode
        if exe_mode == 'Sequential':
            for action in action_list:
                if action.is_action:
                    result = self.action_handler.run(action.action,action.args,action.kwargs)
                    actions_msgs.append(result)
                else:
                    # is subtask
                    tmp_node = container.get_node_by_name(action.action).modify(action.args,action.kwargs)
                    result = self.run_node(container,tmp_node,actions_msgs)
                    actions_msgs.extend(result)
                self.logger.info(f"Action {action.action}[{'action' if action.is_action else 'subtask'}] executed")
                
            next_nodes = self.decision_maker.next2run(container,node,actions_msgs)#container.next_nodes(node,actions_msgs)
            # 如果next_node为空，则代表任务完成
            if next_nodes is not None:
                for next_node in next_nodes:
                    next_msgs = self.run_node(container,next_node,actions_msgs)
                    actions_msgs.extend(next_msgs)
            return actions_msgs
        elif exe_mode == 'Parallel':
            raise NotImplementedError("Parallel mode is not implemented")
        else:
            raise ValueError(f"Invalid mode: {exe_mode}")

    def run_container(self,container:TaskContainerTemplate)->Optional[List[TaskMsg]]:
        """运行任务容器"""
        node = container.get_initial_node()
        result = self.run_node(container,node)
        return result
    
    def run_task(self,task_file:str,container_type:Optional[TaskContainerTemplate])->Optional[List[TaskMsg]]:
        """运行任务"""
        container = self.generate_container(container_type).setup(self).load_task(task_file)
        result = self.run_container(container)
        return result
