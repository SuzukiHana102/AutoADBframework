from typing import Optional, Any

import yaml

from ..utils.logging import get_logger

class Config:
    class AssertConfig:
        def __init__(self) -> None:
            self.common_assert: Optional[str] = None
            self.LR_assert: Optional[str] = None
            self.resource_record_size: Optional[list[int]] = None
            self.max_io_buffer: Optional[int] = None
            self.resource_list: list[str] = list()
        
        def load_from_yaml(self, yaml_path: str) -> None:
            with open(yaml_path, 'r') as f:
                cfg_dict = yaml.safe_load(f)
            self.load_from_dict(cfg_dict)

        def load_from_dict(self, assert_dict: dict) -> None:
            self.common_assert = assert_dict['common_assert']
            self.LR_assert = assert_dict['LR_assert']
            self.resource_record_size = assert_dict['resource_record_size']
            self.max_io_buffer = assert_dict['max_io_buffer']
            if 'resource' in assert_dict.keys():
                for resource_key in assert_dict['resource'].keys():
                    setattr(self, resource_key, assert_dict['resource'][resource_key])
                    self.resource_list.append(resource_key)

    class SimulatorConfig:
        def __init__(self) -> None:
            self.adb_path: Optional[str] = None
            self.device_addr: Optional[str] = None
            self.screen_resolution: Optional[tuple[int, int]] = None
            self.app_rotation: Optional[int] = None

        def load_from_yaml(self, yaml_path: str) -> None:
            with open(yaml_path, 'r') as f:
                cfg_dict = yaml.safe_load(f)
            self.load_from_dict(cfg_dict)

        def load_from_dict(self, simulator_dict: dict) -> None:
            self.adb_path = simulator_dict['adb_path']
            self.device_addr = simulator_dict['device_addr']
            self.screen_resolution = simulator_dict['screen_resolution']
            self.app_rotation = simulator_dict['app_rotation']
    
    def __init__(self) -> None:
        self.name: Optional[str] = None
        self.assert_cfg: Config.AssertConfig = Config.AssertConfig()
        self.simulator_cfg: Config.SimulatorConfig = Config.SimulatorConfig()
        self.logger = None

    @staticmethod
    def load_from_yaml(yaml_path: str) -> 'Config':
        config = Config()
        with open(yaml_path, 'r') as f:
            cfg_dict = yaml.safe_load(f)
        config.assert_cfg.load_from_yaml(cfg_dict['assert_cfg_file'])
        config.simulator_cfg.load_from_yaml(cfg_dict['simulator_cfg_file'])
        config.name = cfg_dict['name']
        config.logger = get_logger('framework.config.{config.name}')
        config.logger.debug(f"load config from {yaml_path}")
        return config
    
    def register_to(self, obj: Any) -> Any:
        setattr(obj,'assert_cfg',self.assert_cfg)
        setattr(obj,'simulator_cfg',self.simulator_cfg)
        return self
