from typing import Optional
from ..messages.task_msg import TaskMsg
from ..registry.templates.task_node_temp import TaskContainerTemplate

class BaseDecisionMaker:
    def next2run(self,container:TaskContainerTemplate,
                 node:TaskContainerTemplate.TaskNode,
                 task_msg:TaskMsg)->Optional[TaskContainerTemplate.TaskNode]:
        return container.next_nodes(node,task_msg)

