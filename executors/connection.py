from typing import Optional
import os 
import subprocess

import numpy as np

from ..configs.config import Config
from ..messages.connection_msg import ConnectionMsg
from ..utils.logging import get_logger

class Connection:
    def __init__(self) -> None:
        self.config: Optional[Config] = None
        self.simulator_cfg: Optional[Config.SimulatorConfig] = None
        self.assert_cfg: Optional[Config.AssertConfig] = None
        self.logger = get_logger("framework.connection")

    def setup(self,config:Config):
        self.config = config
        self.simulator_cfg = config.simulator_config
        self.assert_cfg = config.assert_config
        return self

    def make_cmd(self, param_list: list[str]) -> list[str]:
        return [self.simulator_cfg.adb_path, '-s', self.simulator_cfg.device_addr] + param_list

    def run_cmd(self, param_list: list[str]) -> None:
        cmd = self.make_cmd(param_list)
        try:
            result = subprocess.run(cmd, check=True,check=True,capture_output=True)
            return ConnectionMsg(result.stdout, result.stderr, 0)
        except :
            self.logger.error(f"run cmd {cmd} failed")
            return ConnectionMsg(result.stdout, result.stderr, 1)
    
    def click(self, x: int, y: int) -> ConnectionMsg:
        result_msg = self.run_cmd(['exec-out', 'input', 'tap', str(x), str(y)])
        if result_msg.is_error():
            self.logger.error(f"click failed: {result_msg.stderr}")
        self.logger.debug(f"click: {result_msg.stdout}")
        return result_msg
    
    def swipe(self, from_x: int, from_y: int, to_x: int, to_y: int) -> ConnectionMsg:
        result_msg = self.run_cmd(['exec-out', 'input', 'swipe', str(from_x), str(from_y), str(to_x), str(to_y)])
        if result_msg.is_error():
            self.logger.error(f"swipe failed: {result_msg.stderr}")
        self.logger.debug(f"swipe: {result_msg.stdout}")
        return result_msg
    
    def screencap(self,channels=3) -> ConnectionMsg:
        result_msg = self.run_cmd(['exec-out', 'screencap'])
        if result_msg.is_success():
            image_bytes = result_msg.stdout
            shape = (self.simulator_cfg.resolution[1], self.simulator_cfg.resolution[0], 4) if self.simulator_cfg.app_rotation == 90 \
                else (self.simulator_cfg.resolution[0], self.simulator_cfg.resolution[1], 4)
            np_image = np.frombuffer(image_bytes, dtype=np.uint8)[-self.simulator_cfg.resolution[0] * self.simulator_cfg.resolution[1] * 4:] \
                           .reshape(*shape)[:, :, :channels]
            self.logger.debug(f"screencap")
            result_msg = ConnectionMsg(np_image, result_msg.stderr, 0)
        else:
            self.logger.error(f"screencap failed: {result_msg.stderr}")
        self.logger.debug(f"screencap")
        return result_msg
    
