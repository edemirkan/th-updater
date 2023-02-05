"""
Web parsing and download operations
"""
from bs4 import BeautifulSoup
import requests
from pathlib import Path
import tkinter as tk
from threading import Event

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


def download_artifact(artifact: Artifact, config: Config, path: Path, tk_frame: tk.Frame, event: Event):
    try:
        html_text = requests.get(artifact.download_url).text
    except Exception as e:
        print(f'Exception: {e}')

    soup = BeautifulSoup(html_text, 'html.parser')
    # Get Mirror URL
    mirror_path = soup.select("p > a")[0]['href']
    artifact_mirror_url = f'{config.moddb_url}{mirror_path}'

    with open(path / artifact.name, 'wb') as file:
        # Start Download
        r = requests.get(artifact_mirror_url,
                         allow_redirects=True, stream=True)
        total_size_in_bytes = int(r.headers.get('content-length', 0))
        chunk_size = 4096  # 1 Kibibyte
        if total_size_in_bytes == 0:  # no content length header
            file.write(r.content)
        else:
            dl = 0
            for data in r.iter_content(chunk_size=chunk_size):
                # set to true if any exit event is set.
                if event.is_set():
                    raise SystemExit
                else:
                    dl += len(data)
                    pb_value = int(100 * dl / total_size_in_bytes)
                    file.write(data)
                    tk_frame.pb_download['value'] = pb_value
