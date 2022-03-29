from typing import Type, Union
from pathlib import Path
from sh import wc  # type: ignore

def normalize_path(path: Union[Path, str]) -> Path:
    if isinstance(path, str):
        path = Path(path)
    elif isinstance(path, Path):
        pass
    else:
        raise TypeError(f'path must be a str or Path, not {type(path)}')
    return path.expanduser().resolve()


def count_lines(path: Union[Path, str]) -> int:
    return int(wc('-l', path).split()[0])
