"""
Metro Flat Theme Manager for GUI Application
Provides consistent styling across the application
"""
import tkinter as tk
from tkinter import ttk
import platform

def apply_metro_flat_theme():
    """Apply Metro Flat theme to the application"""
    style = ttk.Style()
    style.theme_use('clam')
    
    # Configure colors
    style.configure(".", 
                   background="#f5f6fa",
                   foreground="#333333",
                   troughcolor="#e4e6ef",
                   fieldbackground="#ffffff",
                   borderwidth=0,
                   highlightthickness=0)
    
    # Button styling
    style.configure("TButton", 
                   background="#3498db", 
                   foreground="#ffffff",
                   borderwidth=0,
                   relief="flat", 
                   padding=8)
    
    style.map("TButton",
             background=[('active', '#2980b9'), ('pressed', '#2573a7')],
             relief=[('pressed', 'flat')])
    
    # Secondary button
    style.configure("Secondary.TButton", 
                   background="#95a5a6", 
                   foreground="#ffffff",
                   borderwidth=0,
                   relief="flat", 
                   padding=8)
    
    style.map("Secondary.TButton",
             background=[('active', '#7f8c8d'), ('pressed', '#6c7879')],
             relief=[('pressed', 'flat')])
    
    # Accent button for special actions
    style.configure("Accent.TButton", 
                   background="#e74c3c", 
                   foreground="#ffffff",
                   borderwidth=0,
                   relief="flat", 
                   padding=8)
    
    style.map("Accent.TButton",
             background=[('active', '#c0392b'), ('pressed', '#a93226')],
             relief=[('pressed', 'flat')])
    
    # Entry styling - flat with just bottom border    
    style.configure("TEntry", 
                   foreground="#333333",
                   fieldbackground="#ffffff",
                   borderwidth=0,
                   relief="flat",
                   insertcolor="#3498db")
    
    # Label styling
    style.configure("TLabel",
                  background="#f5f6fa",
                  foreground="#333333")
                  
    # Title label styling
    style.configure("Title.TLabel",
                  background="#f5f6fa",
                  foreground="#3498db",
                  font=('Segoe UI' if platform.system() == 'Windows' else 'Helvetica', 16, 'normal'))
    
    # Subtitle label styling
    style.configure("Subtitle.TLabel",
                  background="#f5f6fa",
                  foreground="#7f8c8d",
                  font=('Segoe UI' if platform.system() == 'Windows' else 'Helvetica', 10))
    
    # File label styling
    style.configure("File.TLabel",
                  background="#f5f6fa",
                  foreground="#2c3e50",
                  font=('Segoe UI' if platform.system() == 'Windows' else 'Helvetica', 11))
    
    # Frame styling
    style.configure("TFrame",
                  background="#f5f6fa")
    
    # Create separator style
    style.configure("Separator.TFrame",
                  background="#e4e6ef",
                  height=1)
    
    # LabelFrame styling
    style.configure("TLabelframe",
                  background="#f5f6fa",
                  foreground="#3498db",
                  bordercolor="#e4e6ef",
                  labeloutside=True)
                  
    style.configure("TLabelframe.Label",
                  background="#f5f6fa",
                  foreground="#3498db",
                  font=('Segoe UI' if platform.system() == 'Windows' else 'Helvetica', 10))
    
    # Checkbutton - square, not rounded
    style.configure("TCheckbutton", 
                  background="#f5f6fa",
                  foreground="#333333")
    
    style.map("TCheckbutton",
             indicatorcolor=[('selected', '#3498db'), ('!selected', '#ffffff')],
             background=[('active', '#f5f6fa')])
    
    # Progressbar - copy layout first
    style.layout("Horizontal.TProgressbar", [
        ('Horizontal.Progressbar.trough', {
            'sticky': 'nswe',
            'children': [
                ('Horizontal.Progressbar.pbar', {
                    'side': 'left',
                    'sticky': 'ns'
                })
            ]
        })
    ])
    
    # Configure progressbar - thin and flat
    style.configure("Horizontal.TProgressbar", 
                   background="#3498db",
                   troughcolor="#e4e6ef",
                   borderwidth=0,
                   thickness=4)
    
    # Treeview styling (for file lists, playlist tables)
    style.configure("Treeview",
                   background="#ffffff",
                   foreground="#333333",
                   fieldbackground="#ffffff",
                   borderwidth=0)
    
    style.map("Treeview",
             background=[('selected', '#3498db')],
             foreground=[('selected', '#ffffff')])
             
    style.configure("Treeview.Heading",
                   background="#f5f6fa",
                   foreground="#2c3e50",
                   borderwidth=0,
                   relief="flat")
    
    # Tab style (Notebook)
    style.configure("TNotebook", 
                   background="#f5f6fa",
                   borderwidth=0)
    
    style.configure("TNotebook.Tab", 
                   background="#e4e6ef",
                   foreground="#7f8c8d",
                   padding=[10, 5],
                   borderwidth=0)
    
    style.map("TNotebook.Tab",
             background=[('selected', '#3498db'), ('active', '#2980b9')],
             foreground=[('selected', '#ffffff'), ('active', '#ffffff')])
    
    # Combobox styling
    style.configure("TCombobox",
                   foreground="#333333",
                   fieldbackground="#ffffff",
                   background="#ffffff",
                   arrowcolor="#3498db")
                   
    style.map("TCombobox",
             fieldbackground=[('readonly', '#ffffff')],
             selectbackground=[('readonly', '#3498db')],
             selectforeground=[('readonly', '#ffffff')])
    
    # Scrollbar styling
    style.configure("TScrollbar",
                  background="#f5f6fa",
                  troughcolor="#e4e6ef",
                  borderwidth=0,
                  arrowcolor="#3498db")
    
    # Status bar styling
    style.configure("Status.TFrame",
                  background="#e4e6ef")
    
    style.configure("Status.TLabel",
                  background="#e4e6ef",
                  foreground="#7f8c8d")
    
    # Return the style object in case further customization is needed
    return style

def configure_root_for_metro(root):
    """Configure a Tk root window for the Metro theme"""
    # Set window background
    root.configure(background="#f5f6fa")
    
    # Configure padding on main window
    root.option_add('*padX', 5)
    root.option_add('*padY', 5)
    
    # Apply theme
    apply_metro_flat_theme()