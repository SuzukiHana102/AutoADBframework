from typing import Optional, Union, Dict, List, Tuple
import json
import os
import copy
from ..registry.client_factory import Factory
from ..registry.templates.action_temp import ActionTemplate
from ..registry.templates.decision_temp import DecisionTemplate
from ..registry.templates.task_node_temp import TaskContainerTemplate
from ..registry.templates.task_client_temp import TaskClientTemplate
from ..configs.config import Config, AssertConfig, SimulatorConfig
from ..utils.logging import get_logger
from ..messages.task_msg import TaskMsg

@Factory.register()
class BaseTaskContainer(TaskContainerTemplate):
    """基础任务容器类"""
    class TaskNode(TaskContainerTemplate.TaskNode):
        def modify(self,args:Optional[List]=None,kwargs:Optional[Dict]=None):
            new_node = copy.deepcopy(self)
            new_args = new_node.args
            for i,arg in enumerate(args):
                new_args[i] = arg
            new_kwargs = new_node.kwargs
            for key,value in kwargs.items():
                new_kwargs[key] = value
            new_node.args = new_args
            new_node.kwargs = new_kwargs
            return new_node
    def __init__(self) -> None:
        super().__init__()
        self.nodes:Dict[str,TaskContainerTemplate.TaskNode] = {}
        self.starting_point:str = None
        self.container_discription:str = 'null'
        self.node_metas:Dict={}

    def setup(self,task_client:TaskClientTemplate)->'BaseTaskContainer':
        self.client = task_client
    
    def get_initial_node(self)->TaskContainerTemplate.TaskNode:
        if self.starting_point is None or self.starting_point not in self.nodes:
            raise ValueError(f"Starting point {self.starting_point} not found in nodes")
        return self.nodes[self.starting_point]
    
    def get_node_by_name(self, name: str) -> TaskContainerTemplate.TaskNode:
        if name not in self.nodes:
            raise ValueError(f"Node {name} not found in nodes")
        return self.nodes[name]

    def __str__(self) -> str:
        return f"{self.__class__.__name__}: {self.container_discription}"


@Factory.register()
class JsonTaskContainer(BaseTaskContainer):
    """JSON格式任务容器类"""

    def __init__(self) -> None:
        super().__init__()
        self.task_json_path:str = None

    @property
    def all_node_names(self)->List[str]:
        return list(self.node_dict.keys())
    
    def import_nodes(self,import_nodes_path:str)->'JsonTaskContainer':
        with open(import_nodes_path,'r') as f:
            import_nodes_dict = json.load(f)
        imported_nodes = import_nodes_dict['nodes']
        self.nodes.update(imported_nodes)
        if 'import' in import_nodes_dict:
            for import_path in import_nodes_dict['import']:
                self.import_nodes(import_path)
        return self

    def load_from_task_json(self,task_json_path:str)->'JsonTaskContainer':
        # 加载任务json
        with open(task_json_path,'r') as f:
            task_dict = json.load(f)
        if 'description' in task_dict:
            self.container_discription = task_dict['description']
        if 'import' in task_dict:
            self.import_nodes(task_dict['import'])
        if 'nodes' in task_dict:
            self.node_metas = task_dict['nodes']
        if 'starting_point' in task_dict:
            self.starting_point = task_dict['starting_point']
        else:
            self.starting_point = list(self.node_metas.keys())[0]
        # 依据读入创建节点
        for node_name,node_meta in self.node_metas.items():
            new_node = JsonTaskContainer.TaskNode()
            new_node.name = node_name
            new_node.mode = node_meta['mode'] if 'mode' in node_meta else 'Sequential'
            new_node.next_node_names = node_meta['next'] if 'next' in node_meta else None
            new_node.action_list = node_meta['actions'] if 'actions' in node_meta else None
            self.nodes[node_name] = new_node
        self.logger.info(f"Task {self.task_name} loaded from {task_json_path}")
        return self
    
    def next_nodes(self,node: TaskContainerTemplate.TaskNode, action_msgs: List[TaskMsg]):
        if node.next_node_names is None:
            return None
        next_nodes = []
        for next_node_name in node.next_node_names:
            next_nodes.append(self.nodes[next_node_name])
        return next_nodes,node.mode
    
# @Factory.register()
# class DecisionTaskContainer(BaseTaskContainer):
#     """决策任务容器类（需要decision maker进行决策）
#     实际上，这个类还没有实现：因为目前没有使用这种类型的任务容器
#     我只是认为这是一个好主意，也许将来会用到
#     """

#     def next_nodes(self,cur_node:'TaskContainerTemplate.TaskNode',cur_node_result:TaskMsg) -> Tuple[List['TaskContainerTemplate.TaskNode'],str]:
#         """获取下一个要执行的节点列表和执行模式
        
#         Args:
#             cur_node: 当前节点
#             cur_node_result: 当前节点的执行结果
            
#         Returns:
#             (下一个节点列表, 执行模式)的元组
#         """
#         assert self.decision_maker is not None, "Decision maker is not set"
#         decision_result : Tuple[List[TaskContainerTemplate.TaskNode],str] = self.decision_maker.decide(self,cur_node,cur_node_result)
#         return decision_result

# @Factory.register()
# class TickTaskContainer(BaseTaskContainer):
#     """动作任务容器类（需要action executor执行动作）
#     实际上，这个类还没有实现：因为目前没有使用这种类型的任务容器
#     我只是认为这是一个好主意，也许将来会用到
#     """

#     def _tick(self,cur_node:'TaskContainerTemplate.TaskNode',cur_node_result:TaskMsg) -> 'TickTaskContainer':
#         """执行当前节点的动作
        
#         Args:
#             cur_node: 当前节点
#             cur_node_result: 当前节点的执行结果
            
#         Returns:
#             self
#         """
#         assert self.decision_maker is not None, "Decision maker is not set"
#         decision_result : Tuple[List[TaskContainerTemplate.TaskNode],str] = self.decision_maker.decide(self,cur_node,cur_node_result)
#         self._next = decision_result
#         return self

#     def next_nodes(self,cur_node:'TaskContainerTemplate.TaskNode',cur_node_result:TaskMsg) -> Tuple[List['TaskContainerTemplate.TaskNode'],str]:
#         """获取下一个要执行的节点列表和执行模式
        
#         Args:
#             cur_node: 当前节点
#             cur_node_result: 当前节点的执行结果
            
#         Returns:
#             (下一个节点列表, 执行模式)的元组
#         """
#         return self._next

# @Factory.register()
# class JsonTaskContainer(BaseTaskContainer):
#     """JSON格式任务容器类"""
    
#     def __init__(self) -> None:
#         """初始化JSON任务容器"""
#         super().__init__()
#         self.assert_config: Optional[AssertConfig] = None  # 断言配置
#         self.simulator_config: Optional[SimulatorConfig] = None  # 模拟器配置

#         self.summary : Optional[str] = None  # 任务描述
#         self.task_name : Optional[str] = None  # 任务名称
#         self.nodes : Optional[Dict[str,TaskContainerTemplate.TaskNode]] = None  # 节点字典
#         self.node_names : List[str] = []  # 节点名称列表
#         self.starting_point : Optional[str] = None  # 起始节点

#         self.logger = get_logger("framework.{self.__class__.__name__}")

#     def redirect(self, kv_pair: Dict[str, Union[str, Dict, List[Union[str, Dict]]]], node_dict: dict) -> None:
#         """重定向节点配置中的值
        
#         Args:
#             kv_pair: 键值对字典
#             node_dict: 节点配置字典
            
#         Returns:
#             重定向后的节点配置字典
#         """
#         for node_key, node_value in node_dict.items():
#             if node_value == kv_pair['key'] :
#                 node_dict[node_key] = kv_pair['value']  
#             elif isinstance(node_value, dict):
#                 node_dict[node_key] = self.redirect(kv_pair, node_value)
#             elif isinstance(node_value, list):
#                 for i, item in enumerate(node_value):
#                     if isinstance(item, str):
#                         if item == kv_pair['key']:
#                             node_dict[node_key][i] = kv_pair['value']
#                     elif isinstance(item, dict):
#                         node_dict[node_key][i] = self.redirect(kv_pair, item)   
#         return node_dict

#     def load_from_task_json(self, task_json_path: str) -> None:
#         """从JSON文件加载任务配置
        
#         Args:
#             task_json_path: JSON文件路径
            
#         Returns:
#             self
#         """
#         with open(task_json_path, 'r') as f:
#             task_dict = json.load(f)

#         # 加载基本信息
#         self.summary = task_dict['description'] if 'description' in task_dict else None
#         self.task_name = task_dict['task_name'] if 'task_name' in task_dict else os.path.basename(task_json_path).split('.')[0]
        
#         # 加载导入的节点
#         imported_nodes_path = task_dict['import_actions'] if 'import_actions' in task_dict else []
#         for imported_nodes_path in imported_nodes_path:
#             with open(imported_nodes_path, 'r') as f:
#                 imported_nodes_dict = json.load(f)
#                 task_dict['nodes'].update(imported_nodes_dict['nodes'])
                
#         # 处理节点配置
#         nodes = task_dict['nodes']
#         if 'redirect' in task_dict:
#             nodes = self.redirect(task_dict['redirect'], nodes)
#         self.starting_point_node_name = task_dict['starting_point'] if 'starting_point' in task_dict else list(nodes.keys())[0]
        
#         # 创建节点对象
#         for node_name, node_dict in nodes.items():
#             self.node_names.append(node_name)
#             self.nodes[node_name] = JsonTaskContainer.TaskNode(node_dict)
            
#         self.logger.info(f"Task {self.task_name} loaded from {task_json_path}")
#         return self
        
#     def next_nodes(self,cur_node:'TaskContainerTemplate.TaskNode',cur_node_result:TaskMsg) -> 'TaskContainerTemplate.TaskStackNode':
#         """获取下一个要执行的节点列表和执行模式
        
#         Args:
#             cur_node: 当前节点
#             cur_node_result: 当前节点的执行结果
            
#         Returns:
#             (下一个节点列表, 执行模式)的元组
#         """
#         if isinstance(cur_node_result.result,TaskMsg.SwitchableResult):
#             return self.TaskStackNode(  
#                 next=[self.nodes[cur_node.next[cur_node_result.result.switch_to]]],
#                 next_mode=cur_node.next_execution_mode
#             )
#         else:
#             return self.TaskStackNode(
#                 next=[self.nodes[next_node_name] for next_node_name in cur_node.next],
#                 next_mode=cur_node.next_execution_mode
#             )