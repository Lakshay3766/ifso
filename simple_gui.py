#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox

class SimpleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple GUI App")
        self.root.geometry("400x300")
        
        # Main frame
        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = ttk.Label(main_frame, text="Simple GUI Application", font=("Helvetica", 16, "bold"))
        title.pack(pady=(0, 20))
        
        # Input section
        input_frame = ttk.LabelFrame(main_frame, text="Enter Your Name", padding="10")
        input_frame.pack(fill=tk.X, pady=10)
        
        self.name_var = tk.StringVar()
        name_entry = ttk.Entry(input_frame, textvariable=self.name_var, width=30)
        name_entry.pack(pady=10)
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        greet_btn = ttk.Button(button_frame, text="Greet", command=self.greet)
        greet_btn.pack(side=tk.LEFT, padx=5)
        
        clear_btn = ttk.Button(button_frame, text="Clear", command=self.clear)
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Output label
        self.output_label = ttk.Label(main_frame, text="", font=("Helvetica", 12), foreground="blue")
        self.output_label.pack(pady=10)
    
    def greet(self):
        name = self.name_var.get().strip()
        if name:
            self.output_label.config(text=f"Hello, {name}!")
            messagebox.showinfo("Greeting", f"Welcome, {name}!")
        else:
            messagebox.showwarning("Input Error", "Please enter your name!")
    
    def clear(self):
        self.name_var.set("")
        self.output_label.config(text="")

if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleApp(root)
    root.mainloop()
