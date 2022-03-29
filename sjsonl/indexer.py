from pathlib import Path
from typing import List, Optional, Union, Generator

import numpy as np
import tqdm
from .utils import count_lines, normalize_path

class JSONLIndexer:
    # TODO: see if there's need for parallel indexer
    def __init__(self, path: Union[str, Path], check: bool = False) -> None:
        """JSONL indexer. Receives a path to a JSONL file, and returns a list of indices that point to the beginning of each JSON object.

        Args:
            path (Union[str, Path]): path to the JSONL file
            check (bool, optional): whether or not to check if the index file lines are valid JSON. Defaults to False.
        """
        self.data_path = normalize_path(path)
        self.check = check
        self._index: List[int] = []

    def _path_to_byte_locations(self, path: Union[str, Path]) -> Generator[int, None, None]:
        yield 0
        with open(path, 'rb') as f:
            for line in f:
                if self.check:
                    self._check_line(line)
                yield f.tell()

    def _check_line(self, line: bytes) -> None:
        raise NotImplementedError('Checking lines is not implemented yet')

    def populate_index(self) -> None:
        print('Populating index...')
        total_lines = count_lines(self.data_path)
        print(f'Total lines: {total_lines}')
        with tqdm.tqdm(total=total_lines) as pbar:
            for loc in self._path_to_byte_locations(self.data_path):
                self._index.append(loc)
                pbar.update(len(self._index))
            self._index.pop()  # remove the last item which points to end of file
        print(f'Indexed {len(self._index)} lines')

    def write_index_to_disk(self, path: Optional[Union[str, Path]] = None) -> None:
        if not path:
            path = self.data_path.with_suffix('.index.npy')
        print(f'Writing index to disk at {path}...')
        data = np.array(self._index)
        np.save(path, data)
        print(f'Index written to {path}')
