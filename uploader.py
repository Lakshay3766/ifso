#!/usr/bin/env python3
"""
CDR Uploader Entry Point
Standalone uploader application
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import tkinter as tk
from gui.uploader_window import CDRUploaderGUI


def main():
    """Main entry point for CDR Uploader"""
    root = tk.Tk()
    app = CDRUploaderGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
