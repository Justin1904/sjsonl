from functools import lru_cache
import json
from pathlib import Path
from typing import Tuple, Union
from .utils import normalize_path
import numpy as np

class JSONLDataset:
    
    def __init__(self, path: Union[str, Path]) -> None:
        self._data_path, self._index_path = self._resolve_path(path)
        self.index = self._load_index(self._index_path)

    def _resolve_path(self, path) -> Tuple[Path, Path]:
        path = normalize_path(path)
        
        if path.is_dir():
            index_path = path / 'index.idx'
            data_path = path / 'data.jsonl'
        elif path.is_file():
            index_path = path.with_suffix('.idx')
            data_path = path.with_suffix('.jsonl')
        else:
            raise ValueError(f'path {path} must be a directory or file wrapped by pathlib.Path, not {type(path)}')
        
        if not index_path.exists():
            raise FileNotFoundError(f'index file {index_path} not found')

        if not data_path.exists():
            raise FileNotFoundError(f'data file {data_path} not found')
        
        return data_path, index_path

    def _load_index(self, path: Path) -> np.ndarray:
        # TODO: check if index loading is a performance bottleneck, if so, use a better integer loader
        return np.load(path, mmap_mode='r')

    @lru_cache(maxsize=32)
    def __getitem__(self, index: int) -> dict:
        # TODO: support only loading a subset of fields to speed up loading
        with open(self._data_path, 'rb') as f:
            f.seek(self.index[index])
            line = f.readline().decode('utf-8')
            data = json.loads(line)
        return data

    @property
    def __len__(self) -> int:
        return len(self.index)
