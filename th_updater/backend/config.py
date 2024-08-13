"""
Config related methods
"""
import yaml
from pathlib import Path


class Config(object):
    """Class for config object."""

    def __init__(self, path: Path) -> None:

        with open(Path(path, 'config.yml'), 'r') as f:
            config = yaml.safe_load(f)

        self.local_version: str = config['local_version'] or "0"
        self.moddb_url: str = config['moddb_url']
        self.th_moddb_path: str = config['th_moddb_path']
        self.th_exe_path: str = config['th_exe_path']
        self.overwrite_config_ini: bool = config['overwrite_config_ini']

    def save(self, path: Path):
        with open(Path(path, 'config.yml'), 'w') as file:
            yaml.dump(vars(self), file)
