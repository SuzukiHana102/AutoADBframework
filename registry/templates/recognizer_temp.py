from typing import Union, Optional, Tuple
import numpy as np


class RecognizerTemplate:
    SUPPORTED_RECOGNIZE_METHODS = []
    def recognize(self, pattern: Union[str, np.ndarray]) -> Optional[Tuple[int, int]]:
        pass
