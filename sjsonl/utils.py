from typing import Type, Union
from pathlib import Path
import subprocess

def normalize_path(path: Union[Path, str]) -> Path:
    if isinstance(path, str):
        path = Path(path)
    elif isinstance(path, Path):
        pass
    else:
        raise TypeError(f'path must be a str or Path, not {type(path)}')
    return path.expanduser().resolve()


def count_lines(path: Union[Path, str]) -> int:
    # Execute the 'wc' command with the '-l' flag to count lines
    result = subprocess.run(['wc', '-l', str(path)], capture_output=True, text=True, check=True)
    
    # Retrieve the line count from the output
    line_count = int(result.stdout.split()[0])
    
    return line_count