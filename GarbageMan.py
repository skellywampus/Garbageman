import os
import shutil
import tkinter as tk
from tkinter import messagebox, ttk
import psutil

def list_drives():
    drives = []
    if os.name == 'nt':
        # Windows
        for drive in range(ord('A'), ord('Z') + 1):
            drive = chr(drive) + ':\\'
            if os.path.exists(drive) and drive != 'C:\\':
                drives.append(drive)
    else:
        # MacOS and Linux
        partitions = psutil.disk_partitions()
        for partition in partitions:
            if 'rw' in partition.opts.split(',') and not partition.mountpoint.startswith('/System'):
                drives.append(partition.mountpoint)
    return drives

def delete_mac_files(drive):
    deleted_files = []
    mac_garbage = [".DS_Store", ".fseventsd", ".Trashes", ".Spotlight-V100"]
    total_files = sum(len(files) for _, _, files in os.walk(drive))
    processed_files = 0

    for root_dir, dirs, files in os.walk(drive):
        for file in files:
            if file.startswith("._") or file in mac_garbage:
                file_path = os.path.join(root_dir, file)
                try:
                    os.remove(file_path)
                    deleted_files.append(file_path)
                except Exception as e:
                    print(f"Error deleting file {file_path}: {e}")
            processed_files += 1
            progress_var.set((processed_files / total_files) * 100)
            main_window.update_idletasks()
        for dir in dirs:
            if dir in mac_garbage:
                dir_path = os.path.join(root_dir, dir)
                try:
                    shutil.rmtree(dir_path)
                    deleted_files.append(dir_path)
                except Exception as e:
                    print(f"Error deleting directory {dir_path}: {e}")
            processed_files += 1
            progress_var.set((processed_files / total_files) * 100)
            main_window.update_idletasks()

    # Create .metadata_never_index file in the root directory to prevent further indexing
    metadata_file_path = os.path.join(drive, ".metadata_never_index")
    try:
        with open(metadata_file_path, 'w') as metadata_file:
            pass
    except Exception as e:
        print(f"Error creating .metadata_never_index file: {e}")

    if deleted_files:
        messagebox.showinfo("Files Deleted", "Files deleted.")
    else:
        messagebox.showinfo("No Files Found", "No files or folders matching the criteria were found.")

def start_cleaning():
    drive = drive_var.get()
    if drive:
        progress_bar.pack(pady=10)
        main_window.update_idletasks()
        delete_mac_files(drive)
        progress_bar.pack_forget()

# GUI setup
main_window = tk.Tk()
main_window.title("GarbageMan")
main_window.geometry("350x250")

# Instructions message
msg = tk.Label(main_window, text="Select the drive you would like to delete the MacOS garbage files from. "
                          "When you have selected the drive you wish to clean, click the 'Start' button to begin the cleaning process.",
               wraplength=330, justify="left")
msg.pack(pady=10)

# Dropdown for drive selection
drive_var = tk.StringVar(main_window)
drive_list = list_drives()

if drive_list:
    drive_menu = tk.OptionMenu(main_window, drive_var, *drive_list)
    drive_menu.pack(pady=10)
else:
    tk.Label(main_window, text="No drives found").pack(pady=20)

# Start button
start_button = tk.Button(main_window, text="Start", command=start_cleaning, width=20, height=2)
start_button.pack(pady=20)

# Progress bar
progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(main_window, variable=progress_var, maximum=100)
progress_bar.pack(pady=10)
progress_bar.pack_forget()

main_window.mainloop()
