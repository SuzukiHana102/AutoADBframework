from typing import Optional, Dict, Tuple, Union, Any, Callable, Type, List
import time
import numpy as np
import cv2

from ..registry.templates.recognizer_temp import RecognizerTemplate
from ..registry.client_factory import Factory
from ..registry.templates.action_temp import ActionTemplate
from ..messages.task_msg import TaskMsg
from ..messages.connection_msg import ConnectionMsg
from ..utils.logging import get_logger
from ..configs.config import Config, AssertConfig, SimulatorConfig
from .connection import Connection

@Factory.register()
class BaseActionExecutor(ActionTemplate):
    """基础动作执行器类,继承自ActionTemplate
    
    负责执行基本的点击、滑动、图像识别等操作
    """
    def __init__(self) -> None:
        """初始化基础动作执行器
        
        初始化连接、识别器、配置等属性
        """
        self.connection :Optional[Connection] = None
        self.recognizer_matcher: Optional[Dict[str, str]] = None
        self.recognizers: Dict[str,Union[Type[RecognizerTemplate],RecognizerTemplate]] = dict()
        self.assert_config : Optional[AssertConfig] = None
        self.simulator_config : Optional[SimulatorConfig] = None
        self.resource_pools: Dict[str,Any] = dict()
        self.logger = get_logger("framework.{self.__class__.__name__}")
    
    def setup(self,connection:Connection,recognizers:List[RecognizerTemplate]):
        self.connection = connection
        self._register_all_recognizer(recognizers)
        return self

    def _register_all_recognizer(self, recognizers:List[RecognizerTemplate]) -> 'BaseActionExecutor':
        """注册所有识别器"""
        for recognizer in recognizers:
            for method in recognizer.SUPPORTED_RECOGNIZE_METHODS:
                self.recognize_method_matcher[method] = recognizer.__name__
                self.recognizers[recognizer.__name__] = recognizer
        return self

    def _update_resource_pools(self, image_path: str) -> None:
        """更新资源池中的图像
        
        Args:
            image_path: 图像路径
            
        Returns:
            加载的图像
        """
        image = cv2.imread(image_path)
        self.resource_pools[image_path] = image
        if self.config.assert_config.max_resource_size != -1 and\
                len(self.resource_pools) > self.config.assert_config.max_resource_size:
            self.logger.debug(f"Resource pools is full, remove the oldest image")
            self.resource_pools.pop(next(iter(self.resource_pools)))
        return image

    def _io_image(self, image_path: str) -> np.ndarray:
        """从资源池获取或加载图像
        
        Args:
            image_path: 图像路径
            
        Returns:
            图像数据
        """
        if image_path not in self.resource_pools:
            image = self._update_resource_pools(image_path)
            self.logger.debug(f"Image {image_path} not found in ressource pools, load it")
        else:
            image = self.resource_pools[image_path]
            self.logger.debug(f"Get image {image_path} from resource pools")
        return image

    def _do_recognize(self,method:str,pattern:np.ndarray,**kwargs) -> Optional[Tuple[int,int]]:
        """执行图像识别
        
        Args:
            method: 识别方法名
            pattern: 要识别的图案
            **kwargs: 其他参数
            
        Returns:
            识别到的坐标,未识别到则返回None
        """
        recognize_method = self._recognize_match(method)
        return recognize_method(pattern, **kwargs)

    def _recognize_match(self,method:str) -> Callable[...,Optional[Tuple[int,int]]]:
        """执行图像识别匹配
        """
        recognizer_str = self.recognizer_matcher[method]
        recognizer = self.recognizers[recognizer_str]
        if isinstance(recognizer,RecognizerTemplate):
            return getattr(recognizer,method)
        elif isinstance(recognizer,Type[RecognizerTemplate]):
            new_recognizer = recognizer()
            self.recognizers[recognizer_str] = new_recognizer
            return getattr(new_recognizer,method)
        else:
            raise ValueError(f"Unknown recognizer type: {recognizer_str}")

    @ActionTemplate.register_support
    def click(self, x: int, y: int, wait_time: Optional[float] = 0.5, wait_before=True) -> TaskMsg:
        """执行点击操作
        
        Args:
            x: 点击的x坐标
            y: 点击的y坐标
            wait_time: 等待时间
            wait_before: 是否在点击前等待
            
        Returns:
            任务执行结果
        """
        if wait_before and wait_time is not None and wait_time != 0:
            time.sleep(wait_time)
        
        connection_result: ConnectionMsg = self.connection.click(x, y)
        result = TaskMsg(
                result=connection_result.is_success(),
                stderr=connection_result.stderr,
                state_code=0 if connection_result.is_success() else 1,
            )
        if not wait_before and wait_time is not None and wait_time != 0:
            time.sleep(wait_time)
        return result
    
    @ActionTemplate.register_support
    def swipe(self, from_x: int, from_y: int, to_x: int, to_y: int, wait_time: Optional[float] = 0.5, wait_before=True) -> TaskMsg:
        """执行滑动操作
        
        Args:
            from_x: 起始x坐标
            from_y: 起始y坐标
            to_x: 终点x坐标
            to_y: 终点y坐标
            wait_time: 等待时间
            wait_before: 是否在滑动前等待
            
        Returns:
            任务执行结果
        """
        if wait_before and wait_time is not None and wait_time != 0:
            time.sleep(wait_time)
        
        connection_result: ConnectionMsg = self.connection.swipe(from_x, from_y, to_x, to_y)
        result = TaskMsg(
                result=connection_result.is_success(),
                stderr=connection_result.stderr,
                state_code=0 if connection_result.is_success() else 1,
            )
        
        if not wait_before and wait_time is not None and wait_time != 0:
            time.sleep(wait_time)
        return result

    @ActionTemplate.register_support
    def recognize(self, pattern: Union[np.ndarray, str],
                  crop_range: Optional[Tuple[float, float, float, float]] = None,
                  method: str = 'TM_CCOEFF_NORMED',
                  recognize_threshold: float = 0.9,
                  wait_time: Optional[float] = 0.5,
                  wait_before=True,
                  **kwargs) -> TaskMsg:
        """执行图像识别操作
        
        Args:
            pattern: 要识别的图案,可以是图像数据或图像路径
            crop_range: 裁剪范围,格式为(min_x, max_x, min_y, max_y)的比例值
            method: 识别方法
            recognize_threshold: 识别阈值
            wait_time: 等待时间
            wait_before: 是否在识别前等待
            **kwargs: 其他参数
            
        Returns:
            任务执行结果,成功时result为识别到的坐标
        """
        if wait_before and wait_time is not None and wait_time != 0:
            time.sleep(wait_time)

        if isinstance(pattern, str):
            pattern = self._io_image(pattern)
        
        screencap_result: ConnectionMsg = self.connection.screencap()
        if not screencap_result.is_success():
            self.logger.error(f"Failed to get screencap: {screencap_result.stderr}")
            return TaskMsg(False, screencap_result.stderr, 1)

        screen_image = screencap_result.stdout

        offset_min_x, offset_min_y, offset_max_x, offset_max_y = 0, 0, screen_image.shape[0], screen_image.shape[1]
        if crop_range is not None:
            offset_min_x = int(screen_image.shape[0] * crop_range[0])
            offset_min_y = int(screen_image.shape[1] * crop_range[2])
            offset_max_x = int(screen_image.shape[0] * crop_range[1])
            offset_max_y = int(screen_image.shape[1] * crop_range[3])
            screen_image = screen_image[offset_min_x:offset_max_x, offset_min_y:offset_max_y]
        
        rec_result = self._do_recognize(method, pattern, recognize_threshold=recognize_threshold, **kwargs)
        if rec_result is None:
            result=TaskMsg(False,f'Failed to recognize pattern {pattern}', 2)
        else:
            rec_x, rec_y = rec_result[0] + offset_min_x, rec_result[1] + offset_min_y
            result = TaskMsg(
                result=(rec_x, rec_y),
                stderr=f'Recognize pattern {pattern} successfully',
                state_code=0,
            )
        
        if not wait_before and wait_time is not None and wait_time != 0:
            time.sleep(wait_time)
        return result
