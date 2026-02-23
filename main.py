#!/usr/bin/env python3
"""
Main Application Entry Point
CDR Analysis & Investigation Tool
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import tkinter as tk
from gui.case_selection_window import CaseSelectionWindow
from gui.main_window import CDRAnalysisTool


def main():
    """Main entry point for CDR Analysis Tool"""
    
    # Create root for login
    login_root = tk.Tk()
    
    current_user = None
    
    def on_login_success(username):
        nonlocal current_user
        current_user = username
        login_root.destroy()
        
    from gui.login_window import LoginWindow
    login_app = LoginWindow(login_root, on_login_success)
    login_root.mainloop()
    
    # If login successful, proceed to case selection
    if current_user:
        case_root = tk.Tk()
        
        selected_case_name = None
        selected_db_path = None
        
        def on_case_selected(case_name, db_path):
            nonlocal selected_case_name, selected_db_path
            selected_case_name = case_name
            selected_db_path = db_path
        
        case_window = CaseSelectionWindow(case_root, on_case_selected, current_user)
        case_root.mainloop()
        
        # If a case was selected, open the main application
        if selected_case_name and selected_db_path:
            main_root = tk.Tk()
            app = CDRAnalysisTool(main_root, selected_case_name, selected_db_path, current_user)
            main_root.mainloop()


if __name__ == "__main__":
    main()
