from typing import Optional

from ...messages.task_msg import TaskMsg
from .task_node_temp import TaskContainerTemplate

class DecisionTemplate:
    def next2run(self,container:TaskContainerTemplate,
                 node:TaskContainerTemplate.TaskNode,
                 task_msg:TaskMsg)->Optional[TaskMsg]:
        pass    
