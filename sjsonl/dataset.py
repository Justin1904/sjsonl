from functools import lru_cache
import json
from pathlib import Path
from typing import Tuple, Union
from .utils import normalize_path
from .indexer import JSONLIndexer
import numpy as np

class JSONLDataset:
    
    def __init__(self, path: Union[str, Path], build_index_on_load: bool = True) -> None:
        self.build_index_on_load = build_index_on_load
        self._data_path, self._index_path = self._resolve_path(path)
        
        if not self.index:
            print(f"Loading existing index from {self._index_path}...")
            self.index = self._load_index(self._index_path)

    def _resolve_path(self, path: Union[str, Path]) -> Tuple[Path, Path]:
        path = normalize_path(path)
        if path.suffix and path.suffix != '.jsonl':
            raise ValueError(f'path must have .jsonl extension, not {path.suffix}')

        if path.is_dir():
            index_path = path / 'data.index.npy'
            data_path = path / 'data.jsonl'
        elif path.with_suffix('.jsonl').is_file():
            index_path = path.with_suffix('.index.npy')
            data_path = path.with_suffix('.jsonl')
        else:
            raise ValueError(f'path must be a directory, JSONL file or extension-less path'
                             f'to both .index.npy and .jsonl files wrapped by pathlib.Path, but got {path}')

        if not data_path.exists():
            raise FileNotFoundError(f'data file {data_path} not found')\

        if not index_path.exists():
            if self.build_index_on_load:
                print(f"Index not found, building index at {index_path}...")
                self._build_index(data_path)
            else:
                raise FileNotFoundError(f'index file {index_path} not found')

        return data_path, index_path

    def _build_index(self, data_path: Path) -> None:
        indexer = JSONLIndexer(data_path)
        indexer.populate_index()
        indexer.write_index_to_disk()
        self.index = indexer._index

    def _load_index(self, path: Path) -> np.ndarray:
        # TODO: check if index loading is a performance bottleneck, if so, use a better integer loader
        return np.load(path, mmap_mode='r')

    @lru_cache(maxsize=1024)
    def __getitem__(self, index: int) -> dict:
        if index < 0 or index >= len(self):
            raise IndexError(f'index must be between 0 and {len(self)-1}')
        # TODO: support only loading a subset of fields to speed up loading
        with open(self._data_path, 'rb') as f:
            f.seek(self.index[index])
            line = f.readline().decode('utf-8')
            data = json.loads(line)
        return data

    def __len__(self) -> int:
        return len(self.index)
