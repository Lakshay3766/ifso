#!/usr/bin/env python3
"""
Login Window
Authentication interface for the application
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.auth_manager import AuthManager


class LoginWindow:
    """Window for user login and registration"""
    
    def __init__(self, root, on_login_success):
        """
        Initialize login window
        
        Args:
            root: Tkinter root window
            on_login_success: Callback function executed on successful login
        """
        self.root = root
        self.on_login_success = on_login_success
        self.auth_manager = AuthManager()
        
        self.root.title("IFS0 Special Cell - Access Control")
        self.root.geometry("400x520")
        self.root.resizable(False, False)
        
        # Center the window
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - 400) // 2
        y = (screen_height - 520) // 2
        self.root.geometry(f"400x520+{x}+{y}")
        
        self._configure_style()
        self.setup_ui()
        
    def _configure_style(self):
        """Configure light theme styles"""
        style = ttk.Style(self.root)
        try:
            style.theme_use('clam')
        except tk.TclError:
            pass
            
        # Colors - Light Theme
        bg_color = "#f8fafc"      # Very light slate/white
        card_color = "#ffffff"    # Pure white
        text_color = "#0f172a"    # Dark slate
        accent_color = "#2563eb"  # Professional Blue
        accent_hover = "#1d4ed8"  # Darker Blue
        border_color = "#e2e8f0"  # Light gray
        
        style.configure("Login.TFrame", background=bg_color)
        style.configure("Card.TFrame", background=card_color, relief="flat", borderwidth=0)
        
        style.configure("Title.TLabel", 
                       background=bg_color, 
                       foreground=text_color, 
                       font=("Helvetica", 16, "bold"))
                       
        style.configure("Subtitle.TLabel", 
                       background=bg_color, 
                       foreground="#64748b",  # Slate-500
                       font=("Helvetica", 10))
                       
        style.configure("TLabel", 
                       background=card_color, 
                       foreground=text_color,
                       font=("Helvetica", 10))
                       
        style.configure("TEntry", 
                       fieldbackground="#f1f5f9",
                       foreground=text_color,
                       borderwidth=1,
                       relief="flat")
                       
        style.configure("Primary.TButton",
                       background=accent_color,
                       foreground="#ffffff",
                       font=("Helvetica", 11, "bold"),
                       borderwidth=0,
                       relief="flat")
        style.map("Primary.TButton", 
                 background=[('active', accent_hover)])
                 
        style.configure("Secondary.TButton",
                       background="transparent",
                       foreground=accent_color,
                       font=("Helvetica", 10),
                       borderwidth=0)
                       
        self.root.configure(background=bg_color)
        
    def setup_ui(self):
        """Setup UI components"""
        main_frame = ttk.Frame(self.root, style="Login.TFrame", padding=30)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_frame = ttk.Frame(main_frame, style="Login.TFrame")
        header_frame.pack(fill=tk.X, pady=(20, 30))
        
        ttk.Label(header_frame, text="IFSO SPECIAL CELL",
                 style="Title.TLabel", justify="center").pack()
                 
        ttk.Label(header_frame, text="Intelligence & Forensics Console",
                 style="Subtitle.TLabel", justify="center").pack(pady=(5,0))

        # Login Card
        self.card_frame = ttk.Frame(main_frame, style="Card.TFrame", padding=25)
        self.card_frame.pack(fill=tk.BOTH, expand=True)
        
        # We will switch between Login and Register frames inside the card
        self.login_frame = ttk.Frame(self.card_frame, style="Card.TFrame")
        self.register_frame = ttk.Frame(self.card_frame, style="Card.TFrame")
        
        self.show_login_form()
        
    def show_login_form(self):
        """Show login form"""
        self.register_frame.pack_forget()
        self.login_frame.pack(fill=tk.BOTH, expand=True)
        
        # Clean up existing widgets if any (to avoid duplicates if called multiple times)
        for widget in self.login_frame.winfo_children():
            widget.destroy()
            
        ttk.Label(self.login_frame, text="Sign In", 
                 font=("Helvetica", 14, "bold"), style="TLabel").pack(anchor=tk.W, pady=(0, 20))
        
        # Username
        ttk.Label(self.login_frame, text="Username").pack(anchor=tk.W, pady=(0, 5))
        self.login_username = ttk.Entry(self.login_frame, font=("Helvetica", 11))
        self.login_username.pack(fill=tk.X, pady=(0, 15), ipady=5)
        self.login_username.focus()
        
        # Password
        ttk.Label(self.login_frame, text="Password").pack(anchor=tk.W, pady=(0, 5))
        self.login_password = ttk.Entry(self.login_frame, show="•", font=("Helvetica", 11))
        self.login_password.pack(fill=tk.X, pady=(0, 25), ipady=5)
        
        # Login Button
        login_btn = ttk.Button(self.login_frame, text="Login", 
                             style="Primary.TButton", 
                             command=self.perform_login,
                             cursor="hand2")
        login_btn.pack(fill=tk.X, pady=(0, 15), ipady=4)
        
        # Register Link
        link_frame = ttk.Frame(self.login_frame, style="Card.TFrame")
        link_frame.pack(fill=tk.X)
        ttk.Label(link_frame, text="No account?", style="Subtitle.TLabel").pack(side=tk.LEFT)
        reg_btn = tk.Label(link_frame, text="Create one", 
                          bg="#ffffff", fg="#2563eb", cursor="hand2",
                          font=("Helvetica", 10, "bold"))
        reg_btn.pack(side=tk.LEFT, padx=5)
        reg_btn.bind("<Button-1>", lambda e: self.show_register_form())
        
        # Bind enter key
        self.root.bind('<Return>', lambda e: self.perform_login())

    def show_register_form(self):
        """Show registration form"""
        self.login_frame.pack_forget()
        self.register_frame.pack(fill=tk.BOTH, expand=True)
        
        # Clean up existing widgets
        for widget in self.register_frame.winfo_children():
            widget.destroy()
            
        ttk.Label(self.register_frame, text="Create Account", 
                 font=("Helvetica", 14, "bold"), style="TLabel").pack(anchor=tk.W, pady=(0, 20))
        
        # Username
        ttk.Label(self.register_frame, text="Username").pack(anchor=tk.W, pady=(0, 5))
        self.reg_username = ttk.Entry(self.register_frame, font=("Helvetica", 11))
        self.reg_username.pack(fill=tk.X, pady=(0, 15), ipady=5)
        self.reg_username.focus()
        
        # Password
        ttk.Label(self.register_frame, text="Password").pack(anchor=tk.W, pady=(0, 5))
        self.reg_password = ttk.Entry(self.register_frame, show="•", font=("Helvetica", 11))
        self.reg_password.pack(fill=tk.X, pady=(0, 15), ipady=5)
        
        # Confirm Password
        ttk.Label(self.register_frame, text="Confirm Password").pack(anchor=tk.W, pady=(0, 5))
        self.reg_confirm = ttk.Entry(self.register_frame, show="•", font=("Helvetica", 11))
        self.reg_confirm.pack(fill=tk.X, pady=(0, 25), ipady=5)
        
        # Register Button
        reg_btn = ttk.Button(self.register_frame, text="Register", 
                           style="Primary.TButton", 
                           command=self.perform_register,
                           cursor="hand2")
        reg_btn.pack(fill=tk.X, pady=(0, 15), ipady=4)
        
        # Back to Login
        link_frame = ttk.Frame(self.register_frame, style="Card.TFrame")
        link_frame.pack(fill=tk.X)
        ttk.Label(link_frame, text="Already have an account?", style="Subtitle.TLabel").pack(side=tk.LEFT)
        login_link = tk.Label(link_frame, text="Sign in", 
                            bg="#ffffff", fg="#2563eb", cursor="hand2",
                            font=("Helvetica", 10, "bold"))
        login_link.pack(side=tk.LEFT, padx=5)
        login_link.bind("<Button-1>", lambda e: self.show_login_form())
        
        # Bind enter key
        self.root.bind('<Return>', lambda e: self.perform_register())

    def perform_login(self):
        """Handle login action"""
        username = self.login_username.get().strip()
        password = self.login_password.get().strip()
        
        if not username or not password:
            messagebox.showwarning("Input Required", "Please enter username and password")
            return
            
        success, message = self.auth_manager.login_user(username, password)
        
        if success:
            self.on_login_success(username)
        else:
            messagebox.showerror("Login Failed", message)
            
    def perform_register(self):
        """Handle registration action"""
        username = self.reg_username.get().strip()
        password = self.reg_password.get().strip()
        confirm = self.reg_confirm.get().strip()
        
        if not username or not password:
            messagebox.showwarning("Input Required", "Please fill all fields")
            return
            
        if password != confirm:
            messagebox.showerror("Error", "Passwords do not match")
            return
            
        success, message = self.auth_manager.register_user(username, password)
        
        if success:
            messagebox.showinfo("Success", "Account created successfully! Please login.")
            self.show_login_form()
        else:
            messagebox.showerror("Registration Failed", message)


def test_login():
    """Test login window"""
    root = tk.Tk()
    def on_success(user):
        print(f"Logged in as {user}")
        root.destroy()
    app = LoginWindow(root, on_success)
    root.mainloop()

if __name__ == "__main__":
    test_login()
