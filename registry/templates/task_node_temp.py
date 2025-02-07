from typing import List,Optional,Dict
import enum
from dataclasses import dataclass

from ...messages.task_msg import TaskMsg
class TaskContainerTemplate:
    
    class TaskNode:
        @dataclass
        class TaskAction:
            action:Optional[str] = None
            args:Optional[List] = None
            kwargs:Optional[Dict] = None
            is_action:bool = True
        
        name:Optional[str] = None
        mode:str = 'Sequential'
        next_node_names:Optional[List[str]] = None
        action_list:List[TaskAction] = []

        @property
        def all_actions(self) -> List[TaskAction]:
            return self.action_list

        def add_action(self,action:TaskAction):
            self.action_list.append(action)
        
        def modify(self,args:Optional[List]=None,kwargs:Optional[Dict]=None):
            pass

    def next_nodes(self,node:TaskNode,action_msgs:List[TaskMsg]):
        pass

    def get_initial_node(self)->TaskNode:
        pass
    
    def get_node_by_name(self,name:str)->TaskNode:
        pass
