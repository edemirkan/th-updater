"""
Local file system operations
"""
import hashlib
from pathlib import Path
import zipfile
import shutil
from th_updater.backend.artifact import Artifact


def unzip(source_path: Path, destination_path: Path) -> None:
    with zipfile.ZipFile(source_path, "r") as zip_ref:
        zip_ref.extractall(destination_path)


def create_staging_extract_path(path: Path) -> None:
    Path(path).mkdir(exist_ok=True, parents=True)


def rename(source_path: Path, destination_path: Path):
    """Rename a file"""
    source_path.replace(destination_path)


def delete_staging_folder(path: Path):
    """Delete a given folder recursively"""
    shutil.rmtree(path)


def is_exist(path: Path) -> bool:
    """Check existance of a file/folder"""
    return Path(path).exists()


def copy_artifact_files(source: Path, destination: Path):
    for file in source.iterdir():
        shutil.copyfile(file, Path(destination, file.name))


def verify_md5(path: Path, artifact: Artifact) -> bool:
    """Compare remote and local md5 value"""
    artifact_path = Path(path, artifact.name)
    try:
        with open(artifact_path, 'rb') as file_to_check:
            # read contents of the file
            data = file_to_check.read()
    except FileNotFoundError:
        return False
    else:
        # file found, pipe contents of the file through
        return artifact.md5_hash == hashlib.md5(data).hexdigest()
