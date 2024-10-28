import yaml
import os

from .config import Config
from ..utils.logging import get_logger

class ConfigParser:
    def __init__(self) -> None:
        self.config_path_list: list[str] = list()
        self.logger = get_logger("framework.config_parser")

    def add_config_from_yaml(self, yaml_path: str) -> 'ConfigParser':
        self.config_path_list.append(yaml_path)
        return self

    def generate_config(self,idx: int = 0) -> Config:
        assert idx < len(self.config_path_list) and idx >= 0, f"index {idx} is out of range"
        return Config.load_from_yaml(self.config_path_list[idx])
    
    @property
    def config_path_list(self) -> list[str]:
        return self.config_path_list

    def __len__(self) -> int:
        return len(self.config_path_list)

    def search_from_dir(self, dir_name: str = './configs') -> Config:
        for file in os.listdir(dir_name):
            if file.endswith('.yaml'):
                self.add_config_from_yaml(os.path.join(dir_name, file))
        self.logger.debug(f"search configs from {dir_name}, find {len(self)} configs")
        return self
    
    def __str__(self) -> str:
        return f"ConfigParser with {len(self)} configs [{self.config_path_list}]"
    
    def __repr__(self) -> str:
        return self.__str__()