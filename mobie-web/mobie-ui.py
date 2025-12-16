#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk, messagebox
import requests
import subprocess
import imagej
import scyjava

import os
os.environ["HOME"]="/root"
view=os.getenv("VIEW","cells")
try:
    scyjava.config.add_option('-Dscijava.log.level=warn')
    scyjava.config.add_option('-Dscijava.ui.headless=true')
    ij = imagej.init("/usr/local/Fiji.app", headless=False)
    print("Fiji/MoBIE JVM started successfully")
except Exception as e:
    raise RuntimeError(f"Failed to initialize Fiji/MoBIE: {e}")


try:
    cmd = [
           "/usr/local/mobie-viewer-fiji/mobie-project",
           "-p", "https://github.com/mobie/platybrowser-datasets", 
           "-v", view
           ]
    subprocess.Popen(cmd) 
except Exception as e:
    messagebox.showerror("Error", f"Failed to run mobie-project:\n{e}")


