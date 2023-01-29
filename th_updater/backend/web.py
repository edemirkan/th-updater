"""
Web parsing and download operations
"""
from bs4 import BeautifulSoup
import requests
from pathlib import Path

from th_updater.backend.artifact import Artifact
from th_updater.backend.config import Config


def get_artifact_info(artifact: Artifact, config: Config):

    th_moddb_url = f'{config.moddb_url}{config.th_moddb_path}'
    moddb_url = f'{config.moddb_url}'

    try:
        html_text = requests.get(f'{th_moddb_url}').text
    except Exception as e:
        print(f'Exception: {e}')

    soup = BeautifulSoup(html_text, 'html.parser')

    # Get filename
    file_name_span = soup.find("h5", string="Filename").find_next_sibling(
        "span", class_="summary")
    artifact.name = str(file_name_span.string).strip()

    # Get Hash
    file_hash_span = soup.find("h5", string="MD5 Hash").find_next_sibling(
        "span", class_="summary")
    artifact.md5_hash = str(file_hash_span.string).strip()

    # Get Download URL
    download_path = soup.find(
        id='downloadmirrorstoggle', class_="thickbox")['href']
    artifact.download_url = f'{moddb_url}{download_path}'


def download_artifact(artifact: Artifact, config: Config, path: Path):
    try:
        html_text = requests.get(artifact.download_url).text
    except Exception as e:
        print(f'Exception: {e}')

    soup = BeautifulSoup(html_text, 'html.parser')
    # Get Mirror URL
    mirror_path = soup.select("p > a")[0]['href']
    artifact_mirror_url = f'{config.moddb_url}{mirror_path}'
    # Start Download
    r = requests.get(artifact_mirror_url, allow_redirects=True)
    with open(Path(path, artifact.name), 'wb') as file:
        file.write(r.content)
