
import sys
import os
import tkinter as tk
import traceback

# Add src to path
sys.path.insert(0, os.path.abspath("src"))

try:
    print("Attempting to import CDRAnalysisTool...")
    from gui.main_window import CDRAnalysisTool
    print("Import successful.")

    print("Attempting to instantiate CDRAnalysisTool...")
    root = tk.Tk()
    # Mocking current_user as a string for now, or None
    app = CDRAnalysisTool(root, case_name="DebugCase", db_path="debug.db", current_user="DebugUser")
    print("Instantiation successful.")
    
    # Check if attributes are preserved and initialized
    print(f"Current User: {app.current_user}")
    
    checks = [
        ("home_frame", app.home_frame),
        ("search_frame", app.search_frame),
        ("search_tree", app.search_tree),
        ("metric_cards", app.metric_cards)
    ]
    
    failed_checks = []
    for name, value in checks:
        if value is None:
            failed_checks.append(name)
        else:
            print(f"Verified {name} is initialized.")
            
    if failed_checks:
        print(f"FAILED: The following attributes are None: {failed_checks}")
        # This implies setup_ui didn't run or failed to assign them
        sys.exit(1)
    
    root.destroy()
    print("Test passed. All critical attributes initialized.")

except Exception:
    print("Test FAILED with error:")
    traceback.print_exc()
