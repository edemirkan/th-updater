"""
Main application backend controller
"""
from pathlib import Path
from threading import Event
import tkinter as tk

from th_updater.backend.config import Config
from th_updater.backend.artifact import Artifact
import th_updater.backend.web as web
import th_updater.backend.filesys as filesys

STAGING_FOLDER = '__TH_STAGING__'
EXTRACT_FOLDER = 'extract'
CONFIG_INI = 'config.ini'
CONFIG_NEW_INI = 'config.new.ini'


class AppEngine():
    def __init__(self, tk_frame: tk.Frame) -> None:
        self.t = tk_frame
        self.cwd: Path = Path.cwd()
        self.artifact: Artifact = Artifact()
        self.config = Config(self.cwd)
        self.version_info()

    def version_info(self):
        self.t.append_to_log("Fetching version info...")
        web.get_artifact_info(self.artifact, self.config)
        self.t.append_to_log("Done.", True)
        self.t.lbl_local_version['text'] = f"Local version: {self.config.local_version}"
        self.t.lbl_remote_version['text'] = f"Latest version: {self.artifact.get_version()}"
        if self.artifact.get_version() <= int(self.config.local_version):
            self.t.append_to_log("Latest version is installed.", True)

    def set_config_overwrite(self, status: bool):
        self.config.overwrite_config_ini = status
        self.config.save(self.cwd)

    def set_th_exe_path(self, path: str):
        self.config.th_exe_path = path
        self.config.save(self.cwd)

    def do_version_update(self, event: Event):
        # setup th path
        th_path = Path(self.config.th_exe_path).parent
        # setup staging path
        staging_path: Path = Path(self.cwd, STAGING_FOLDER)
        # setup extract path
        staging_extract_path: Path = Path(staging_path, EXTRACT_FOLDER)
        # create staging and extract paths
        self.t.append_to_log("Creating temp staging folder...")
        filesys.create_staging_extract_path(staging_extract_path)
        self.t.append_to_log("Done.", True)

        # download remote artifact if it's missing or md5 checksum fails
        if not filesys.verify_md5(staging_path, self.artifact):
            self.t.append_to_log("Downloading update. Please wait...")
            try:
                web.download_artifact(
                    self.artifact, self.config, staging_path, self.t, event)
            except SystemExit:
                return None
            self.t.append_to_log("Done.", True)

        # verify downloaded files md5 hash
        if filesys.verify_md5(staging_path, self.artifact):
            source_file = Path(staging_path, self.artifact.name)
            self.t.append_to_log("Extracting downloaded archive...")
            filesys.unzip(source_file, staging_extract_path)
            self.t.append_to_log("Done.", True)
            # rename config, if overwrite_config_ini is false
            if not self.config.overwrite_config_ini:
                # Well, no need to rename it, if there's no config.ini in the first place.
                if filesys.is_exist(Path(th_path, CONFIG_INI)):
                    self.t.append_to_log(
                        "Renaming config.ini as config.new.ini...", True)
                    filesys.rename(Path(staging_extract_path, CONFIG_INI), Path(
                        staging_extract_path, CONFIG_NEW_INI))
            # copy files from staging to configured th folder
            self.t.append_to_log("Copying new files...")
            filesys.copy_artifact_files(
                staging_extract_path, th_path)
            self.t.append_to_log("Done.", True)
            # Delete staging folder, clean up
            # If everything is ok, update local version
            self.config.local_version = self.artifact.get_version()
            # save config file
            self.t.append_to_log("Updating version info...")
            self.config.save(self.cwd)
            self.t.append_to_log("Done.", True)
            self.version_info()
            self.t.append_to_log("Update completed successfully.", True)
        else:
            self.t.append_to_log(
                "Download Error! md5 verification has failed, try to update again...", True)

        # clean up staging folder
        self.t.append_to_log("Cleaning up staging folder...")
        filesys.delete_staging_folder(staging_path)
        self.t.append_to_log("Done.", True)
        # enable back update and launch buttons
        self.t.btn_update.configure(state=tk.NORMAL)
        self.t.btn_launch.configure(state=tk.NORMAL)
