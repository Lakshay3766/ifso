#!/usr/bin/env python3
"""
Case Selection Window
Window for selecting or creating cases
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.case_manager import CaseManager


class CaseSelectionWindow:
    """Window for case selection and management"""
    
    def __init__(self, root, on_case_selected, current_user=None):
        """
        Initialize case selection window
        
        Args:
            root: Tkinter root window
            on_case_selected: Callback function when case is selected
            current_user: Currently logged in user
        """
        self.root = root
        self.on_case_selected = on_case_selected
        self.current_user = current_user
        self.root.title(f"CDR Analysis - Case Selection - {self.current_user if self.current_user else 'Guest'}")
        self.root.geometry("980x620")
        self.root.resizable(True, True)
        self._configure_style()
        
        self.case_manager = CaseManager()
        self.selected_case = None
        
        self.setup_ui()
        self.refresh_case_list()
    
    def _configure_style(self):
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
            
        bg_color = "#f8fafc"
        card_color = "#ffffff"
        text_color = "#0f172a"
        accent_color = "#2563eb"
        
        style.configure("TFrame", background=bg_color)
        style.configure("Card.TFrame", background=card_color, relief="flat", borderwidth=1, bordercolor="#e2e8f0")
        style.configure("Accent.TButton", background=accent_color, foreground="#ffffff", borderwidth=0)
        style.map("Accent.TButton", background=[("active", "#1d4ed8")])
        style.configure("Muted.TLabel", foreground="#64748b", background=bg_color)
        
        style.configure("TLabel", foreground=text_color, background=bg_color)
        style.configure("TButton", background="#e2e8f0", foreground=text_color)
        style.configure("TEntry", fieldbackground="#ffffff", foreground=text_color)
        style.configure("Treeview", background="#ffffff", fieldbackground="#ffffff", foreground=text_color)
        style.configure("Treeview.Heading", background="#f1f5f9", foreground="#334155", font=("Helvetica", 9, "bold"))
        
        self.root.configure(background=bg_color)
    
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        header = ttk.Frame(main_frame)
        header.pack(fill=tk.X, pady=(0, 16))
        
        title_label = ttk.Label(
            header,
            text="CDR Case Workspace",
            font=("Helvetica", 18, "bold"),
        )
        title_label.pack(anchor=tk.W)
        
        subtitle_label = ttk.Label(
            header,
            text="Select an existing case or create a new investigation workspace",
            style="Muted.TLabel",
        )
        subtitle_label.pack(anchor=tk.W, pady=(4, 0))
        
        content = ttk.Frame(main_frame)
        content.pack(fill=tk.BOTH, expand=True)
        content.columnconfigure(0, weight=2)
        content.columnconfigure(1, weight=1)
        content.rowconfigure(0, weight=1)
        
        left_card = ttk.Frame(content, style="Card.TFrame", padding=12)
        left_card.grid(row=0, column=0, sticky=tk.NSEW, padx=(0, 12))
        
        right_card = ttk.Frame(content, style="Card.TFrame", padding=12)
        right_card.grid(row=0, column=1, sticky=tk.NSEW)
        
        button_frame = ttk.Frame(left_card)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(
            button_frame,
            text="Create New Case",
            style="Accent.TButton",
            command=self.create_new_case,
            width=18,
        ).pack(side=tk.LEFT, padx=(0, 8))
        
        ttk.Button(
            button_frame,
            text="Open Selected",
            command=self.open_selected_case,
            width=16,
        ).pack(side=tk.LEFT, padx=(0, 8))
        
        ttk.Button(
            button_frame,
            text="Delete",
            command=self.delete_selected_case,
            width=10,
        ).pack(side=tk.LEFT, padx=(0, 8))
        
        ttk.Button(
            button_frame,
            text="Refresh",
            command=self.refresh_case_list,
            width=10,
        ).pack(side=tk.LEFT)
        
        list_container = ttk.Frame(left_card)
        list_container.pack(fill=tk.BOTH, expand=True)
        
        vsb = ttk.Scrollbar(list_container, orient=tk.VERTICAL)
        hsb = ttk.Scrollbar(list_container, orient=tk.HORIZONTAL)
        
        self.cases_tree = ttk.Treeview(
            list_container,
            columns=("CASE_NUMBER", "OFFICER", "CREATED", "LAST_ACCESSED", "STATUS", "RECORDS"),
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set,
        )
        vsb.config(command=self.cases_tree.yview)
        hsb.config(command=self.cases_tree.xview)
        
        self.cases_tree.column("#0", width=200, minwidth=150)
        self.cases_tree.column("CASE_NUMBER", width=120, minwidth=100)
        self.cases_tree.column("OFFICER", width=150, minwidth=120)
        self.cases_tree.column("CREATED", width=150, minwidth=120)
        self.cases_tree.column("LAST_ACCESSED", width=150, minwidth=120)
        self.cases_tree.column("STATUS", width=80, minwidth=80)
        self.cases_tree.column("RECORDS", width=100, minwidth=80)
        
        self.cases_tree.heading("#0", text="Case Name", anchor=tk.W)
        self.cases_tree.heading("CASE_NUMBER", text="Case Number", anchor=tk.W)
        self.cases_tree.heading("OFFICER", text="Investigating Officer", anchor=tk.W)
        self.cases_tree.heading("CREATED", text="Created Date", anchor=tk.W)
        self.cases_tree.heading("LAST_ACCESSED", text="Last Accessed", anchor=tk.W)
        self.cases_tree.heading("STATUS", text="Status", anchor=tk.W)
        self.cases_tree.heading("RECORDS", text="Records", anchor=tk.W)
        
        self.cases_tree.grid(row=0, column=0, sticky=tk.NSEW)
        vsb.grid(row=0, column=1, sticky=tk.NS)
        hsb.grid(row=1, column=0, sticky=tk.EW)
        list_container.columnconfigure(0, weight=1)
        list_container.rowconfigure(0, weight=1)
        
        self.cases_tree.bind("<Double-1>", lambda e: self.open_selected_case())
        
        right_title = ttk.Label(
            right_card,
            text="How cases work",
            font=("Helvetica", 12, "bold"),
        )
        right_title.pack(anchor=tk.W, pady=(0, 8))
        
        info_text = (
            "• Create one case per investigation.\n"
            "• Each case has its own encrypted CDR database.\n"
            "• Upload multiple CSV files into a case.\n"
            "• All searches and analytics stay within the case."
        )
        
        info_label = ttk.Label(
            right_card,
            text=info_text,
            justify=tk.LEFT,
            style="Muted.TLabel",
        )
        info_label.pack(fill=tk.X, pady=(0, 16))
        
        tips_title = ttk.Label(
            right_card,
            text="Investigator tips",
            font=("Helvetica", 11, "bold"),
        )
        tips_title.pack(anchor=tk.W, pady=(0, 4))
        
        tips_text = (
            "Use clear case names and numbers so reports and\n"
            "exports remain traceable for court and audit use."
        )
        
        tips_label = ttk.Label(
            right_card,
            text=tips_text,
            justify=tk.LEFT,
            style="Muted.TLabel",
        )
        tips_label.pack(fill=tk.X)
    
    def refresh_case_list(self):
        """Refresh the list of cases"""
        # Clear existing items
        for item in self.cases_tree.get_children():
            self.cases_tree.delete(item)
        
        # Get all cases for current user
        cases = self.case_manager.get_all_cases(self.current_user)
        
        for case in cases:
            case_id, case_name, case_number, officer, created, last_accessed, status = case
            
            # Get statistics
            stats = self.case_manager.get_case_statistics(case_name)
            records_count = stats.get('total_records', 0)
            
            # Format dates
            created_date = created[:10] if created else "N/A"
            accessed_date = last_accessed[:10] if last_accessed else "N/A"
            
            self.cases_tree.insert("", tk.END, text=case_name, 
                                  values=(case_number or "N/A", 
                                         officer or "N/A", 
                                         created_date, 
                                         accessed_date, 
                                         status,
                                         records_count))
    
    def create_new_case(self):
        """Open dialog to create a new case"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Create New Case")
        dialog.geometry("550x500")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (550 // 2)
        y = (dialog.winfo_screenheight() // 2) - (500 // 2)
        dialog.geometry(f"550x500+{x}+{y}")
        
        # Main frame
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Create New Case", font=("Helvetica", 14, "bold")).pack(pady=(0, 20))
        
        # Case name
        ttk.Label(frame, text="Case Name: *").pack(anchor=tk.W, pady=(5, 0))
        case_name_var = tk.StringVar()
        case_name_entry = ttk.Entry(frame, textvariable=case_name_var, width=50)
        case_name_entry.pack(fill=tk.X, pady=(0, 10))
        case_name_entry.focus()
        
        # Case number
        ttk.Label(frame, text="Case Number:").pack(anchor=tk.W, pady=(5, 0))
        case_number_var = tk.StringVar()
        case_number_entry = ttk.Entry(frame, textvariable=case_number_var, width=50)
        case_number_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Investigating officer
        ttk.Label(frame, text="Investigating Officer:").pack(anchor=tk.W, pady=(5, 0))
        officer_var = tk.StringVar()
        officer_entry = ttk.Entry(frame, textvariable=officer_var, width=50)
        officer_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Description
        ttk.Label(frame, text="Description:").pack(anchor=tk.W, pady=(5, 0))
        description_text = tk.Text(frame, height=6, width=50, wrap=tk.WORD)
        description_text.pack(fill=tk.X, pady=(0, 15))
        
        def create_case():
            case_name = case_name_var.get().strip()
            if not case_name:
                messagebox.showwarning("Invalid Input", "Case name is required!")
                case_name_entry.focus()
                return
            
            case_number = case_number_var.get().strip()
            officer = officer_var.get().strip()
            description = description_text.get("1.0", tk.END).strip()
            
            success, message = self.case_manager.create_case(
                case_name, case_number, description, officer, user_id=self.current_user
            )
            
            if success:
                messagebox.showinfo("Success", message)
                dialog.destroy()
                self.refresh_case_list()
            else:
                messagebox.showerror("Error", message)
        
        # Bind Enter key to create case (but not in Text widget)
        def on_enter(event):
            if event.widget != description_text:
                create_case()
        
        dialog.bind('<Return>', on_enter)
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=15, side=tk.BOTTOM)
        
        create_button = ttk.Button(button_frame, text="✓ Create Case", command=create_case, width=20)
        create_button.pack(side=tk.LEFT, padx=5)
        
        cancel_button = ttk.Button(button_frame, text="✗ Cancel", command=dialog.destroy, width=15)
        cancel_button.pack(side=tk.LEFT, padx=5)
    
    def open_selected_case(self):
        """Open the selected case"""
        selected = self.cases_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a case to open")
            return
        
        case_name = self.cases_tree.item(selected[0])['text']
        db_path = self.case_manager.get_case_db_path(case_name)
        
        if db_path:
            # Update last accessed
            self.case_manager.update_last_accessed(case_name)
            
            # Call the callback with case info
            self.selected_case = case_name
            self.on_case_selected(case_name, db_path)
            self.root.destroy()
        else:
            messagebox.showerror("Error", f"Could not find database for case: {case_name}")
    
    def delete_selected_case(self):
        """Delete the selected case"""
        selected = self.cases_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a case to delete")
            return
        
        case_name = self.cases_tree.item(selected[0])['text']
        
        if messagebox.askyesno("Confirm Deletion", 
                              f"Are you sure you want to delete case '{case_name}'?\n\n"
                              "This will delete all CDR data associated with this case.\n"
                              "This action cannot be undone!"):
            success, message = self.case_manager.delete_case(case_name)
            
            if success:
                messagebox.showinfo("Success", message)
                self.refresh_case_list()
            else:
                messagebox.showerror("Error", message)


def main():
    """Main entry point for testing"""
    def on_case_selected(case_name, db_path):
        print(f"Selected case: {case_name}")
        print(f"Database path: {db_path}")
    
    root = tk.Tk()
    app = CaseSelectionWindow(root, on_case_selected)
    root.mainloop()


if __name__ == "__main__":
    main()
