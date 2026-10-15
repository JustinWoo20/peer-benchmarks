from pathlib import Path
import yaml

def find_config(start: Path = None) -> Path:
    current = start or Path.cwd()
    for _ in range(10):
        candidate = current / 'config.yaml'
        if candidate.exists():
            return candidate
        current = current.parent

    raise FileNotFoundError('No config.yaml found')

_config_path = find_config()
_config_root = _config_path.parent

with open(_config_path) as f:
    _raw_config = yaml.safe_load(f)

DATA_DIR = (_config_root / _raw_config['data_dir']).resolve()
PEER_BENCHMARKS = (_config_root / _raw_config['peer_benchmarks']).resolve()