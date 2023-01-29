"""
Artifact related methods
"""
class Artifact(object):
    """Class for keeping properties of downloaded file."""

    def __init__(self) -> None:
        self.name: str
        self.md5_hash: str
        self.download_url: str

    def get_version(self) -> int:
        version = int("".join(self.name.split('_v')[1].split('.')[0:2]))
        return version
