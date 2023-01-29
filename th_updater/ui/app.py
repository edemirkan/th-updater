"""
Main UI application
"""
import sys
import subprocess
from pathlib import Path
import tkinter as tk
import tkinter.scrolledtext as scrolledtext
import tkinter.filedialog as filedialog
import tkinter.messagebox as messagebox
import threading

from th_updater.backend.engine import AppEngine

APP_ICON = 'skull.ico'

class MainApplication(tk.Frame):
    def __init__(self, master=None, *args, **kwargs):
        tk.Frame.__init__(self, master, *args, **kwargs)
        # config frame
        self.frm_config = tk.LabelFrame(self, text="Config", padx=5, pady=5)
        self.config_overwrite_val = tk.BooleanVar()
        self.chk_config_overwrite = tk.Checkbutton(
            self.frm_config, text="Overwrite config.ini", variable=self.config_overwrite_val, command=self.update_config_overwrite)
        self.lbl_th_exe = tk.Label(
            self.frm_config, text="TH3.exe not found. Please click on browse to set it.", fg="red")

        self.btn_browse = tk.Button(
            self.frm_config, text="Browse", command=self.update_th_exe_path)

        # version frame
        self.frm_version = tk.LabelFrame(self, text="Version", padx=5, pady=5)
        self.lbl_local_version = tk.Label(self.frm_version)
        self.lbl_remote_version = tk.Label(self.frm_version)

        # application log
        self.st_app_log = scrolledtext.ScrolledText(
            self, state=tk.DISABLED, width=45, height=8, font='TkFixedFont')

        self.btn_update = tk.Button(
            self, text="Update", padx=15, pady=15, command=self.update)
        self.btn_launch = tk.Button(self, text="Launch", padx=15, pady=15)

        # config frame grid
        self.frm_config.grid(row=0, columnspan=2, padx=5,
                             pady=5, sticky=tk.NSEW)
        self.chk_config_overwrite.grid(
            row=0, column=0, columnspan=2,  sticky=tk.W)

        self.lbl_th_exe.grid(row=1, column=0, sticky=tk.W)
        self.btn_browse.grid(row=1, column=1, padx=15)
        # version Frame grid
        self.frm_version.grid(row=1, column=0, padx=5, sticky=tk.W)
        self.lbl_local_version.grid(row=0, column=0, sticky=tk.W)
        self.lbl_remote_version.grid(row=1, column=0, sticky=tk.W)
        # buttons grid
        self.btn_update.grid(row=1, column=1, pady=10, padx=5, sticky=tk.W)
        self.btn_launch.grid(row=1, column=1, pady=10, padx=5, sticky=tk.E)
        # application log grid
        self.st_app_log.grid(row=3, columnspan=2, pady=5, padx=5)

        self.master.title("The Hell Updater")
        self.master.resizable(False, False)

        # finally init backend
        try:
            self.app_engine = AppEngine(self)
        except FileNotFoundError as _:
            response = messagebox.showerror("Application Error", "Missing config.yaml file!\nMake sure that it is in the current directory.")
            if response:
                sys.exit(1)
        else:
            # set initial state for config_overwrite checkbox
            self.config_overwrite_val.set(
                self.app_engine.config.overwrite_config_ini)
            # if found in config.yaml, pdate th directory value
            if self.app_engine.config.th_exe_path:
                self.lbl_th_exe.configure(
                    text=self.app_engine.config.th_exe_path, fg="green")
            else:
                self.btn_update.configure(state=tk.DISABLED)
                self.btn_launch.configure(state=tk.DISABLED)
            
            self.btn_launch.configure(command=self.launch)

        # set window icon
        ico_path = Path(Path.cwd(), APP_ICON)
        try:
            self.master.iconbitmap(ico_path)
        except Exception as _:
            response = messagebox.showerror("Application Error", "Missing skull.ico file!\nMake sure that it is in the current directory.")
            if response:
                sys.exit(1)   
    def update(self):
        if self.app_engine.artifact.get_version() <= int(self.app_engine.config.local_version):
            response = messagebox.askyesno("Application Info", "Latest version is already installed.\nDo you want to download the latest version again?")
            if response:
                threading.Thread(target=self.app_engine.do_version_update).start()
        else:
            threading.Thread(target=self.app_engine.do_version_update).start()
    
    def launch(self):
        th_exe = Path(self.app_engine.config.th_exe_path)
        subprocess.Popen([th_exe], cwd=th_exe.parent,  creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP)

    def update_config_overwrite(self):
        self.app_engine.set_config_overwrite(self.config_overwrite_val.get())

    def update_th_exe_path(self):
        fdlg_th_exe_path = filedialog.askopenfile(
            initialdir="/", title="Select TH3.exe", filetypes=(("Applications", "TH3.exe"),))
        th_exe_path = fdlg_th_exe_path.name
        self.app_engine.set_th_exe_path(th_exe_path)

        self.btn_update.configure(state=tk.NORMAL)
        self.lbl_th_exe.configure(text=th_exe_path, fg="green")

        self.btn_launch.configure(state=tk.NORMAL)

    def append_to_log(self, msg: str, new_line: bool = False):
        self.st_app_log.configure(state=tk.NORMAL)
        nl = '\n' if new_line else ""
        self.st_app_log.insert(tk.END, f'{msg}{nl}')
        self.st_app_log.configure(state='disabled')
        # Autoscroll to the bottom
        self.st_app_log.yview(tk.END)


def run():
    root = tk.Tk()
    MainApplication(root).pack()
    root.mainloop()
