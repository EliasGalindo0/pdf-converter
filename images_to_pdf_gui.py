import os
import tempfile
# import glob
import tkinter.ttk as ttk
import tkinter as tk
from tkinter import filedialog
from PIL import Image
from fpdf import FPDF


def convert_images_to_pdf(images, output_pdf):
    pdf = FPDF()
    for image in images:
        img = Image.open(image)
        pdf.add_page()
        pdf.image(image, 0, 0, img.width / 6, img.height / 6)
    pdf.output(output_pdf)


def save_to_directories(images, output_pdf_name, directories):
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
        output_path = os.path.join(directory, output_pdf_name)
        convert_images_to_pdf(images, output_path)


def browse_images():
    def on_ok():
        file_paths = [os.path.join(selected_dir, listbox.get(idx))
                      for idx in listbox.curselection()]
        images_listbox.delete(0, tk.END)
        for file_path in file_paths:
            images_listbox.insert(tk.END, file_path)
        file_dialog.destroy()

    file_dialog = tk.Toplevel(root)
    file_dialog.title("Browse Images")

    initial_directory = '/Users/eliasgalindo/Downloads'

    selected_dir = filedialog.askdirectory(initialdir=initial_directory)
    if not selected_dir:
        return

    listbox = tk.Listbox(
        file_dialog, selectmode=tk.MULTIPLE, width=50, height=10)
    listbox.pack(padx=5, pady=5)

    file_types = [".jpg", ".png", ".bmp", ".gif"]
    for file_name in os.listdir(selected_dir):
        if any(file_name.lower().endswith(ext) for ext in file_types):
            listbox.insert(tk.END, file_name)

    ok_button = ttk.Button(file_dialog, text="OK", command=on_ok)
    ok_button.pack(side=tk.RIGHT, padx=5, pady=5)

    cancel_button = ttk.Button(
        file_dialog, text="Cancel", command=file_dialog.destroy)
    cancel_button.pack(side=tk.RIGHT, padx=5, pady=5)


def add_directory():
    default_save_dir = 'Users/eliasgalindo/Desktop/'
    directory = filedialog.askdirectory(initialdir=default_save_dir)
    if directory:
        directories_listbox.insert(tk.END, directory)


def remove_selected(listbox):
    selected_indices = listbox.curselection()
    for index in reversed(selected_indices):
        listbox.delete(index)


def convert_and_save():
    images = images_listbox.get(0, tk.END)
    directories = directories_listbox.get(0, tk.END)
    output_pdf_name = output_name_entry.get()
    if images and directories and output_pdf_name:
        pdf = FPDF()
        for image_path in images:
            image = Image.open(image_path)
            # Resize the image to a standard size
            image = image.resize((800, 800), Image.ANTIALIAS)
            # Rotate the image if needed
            try:
                exif = image._getexif()
                orientation = exif.get(0x0112, 1)
                if orientation == 6:
                    image = image.rotate(-90, expand=True)
                elif orientation == 8:
                    image = image.rotate(90, expand=True)
            except (AttributeError, KeyError, IndexError):
                pass
            # Convert the image to JPEG format
            image_jpeg = image.convert("RGB")
            # Create a temporary file to hold the image data
            with tempfile.NamedTemporaryFile(suffix=".jpeg",
                                             delete=True) as temp:
                image_jpeg.save(temp.name, format="JPEG")
                # Add the image to the PDF
                pdf.add_page()
                pdf.image(temp.name, x=10, y=10, w=190, h=277)
        output_pdf = os.path.join(directories[0], output_pdf_name + ".pdf")
        pdf.output(output_pdf)
        status_label.config(text="PDF saved successfully.")
    else:
        status_label.config(
            text="Please provide images, output name, and directories.")


root = tk.Tk()
root.title("Images to PDF Converter")

# Images list
images_label = tk.Label(root, text="Images:")
images_label.grid(row=0, column=0, sticky="w")
images_listbox = tk.Listbox(root, selectmode=tk.MULTIPLE, width=50, height=10)
images_listbox.grid(row=1, column=0, padx=5, pady=5)
images_scrollbar = tk.Scrollbar(root, command=images_listbox.yview)
images_scrollbar.grid(row=1, column=1, sticky="ns")
images_listbox.config(yscrollcommand=images_scrollbar.set)
browse_button = tk.Button(root, text="Browse Images", command=browse_images)
browse_button.grid(row=2, column=0, pady=5)
remove_images_button = tk.Button(
    root, text="Remove Selected", command=lambda:
    remove_selected(images_listbox))
remove_images_button.grid(row=3, column=0, pady=5)

# Directories list
directories_label = tk.Label(root, text="Directories:")
directories_label.grid(row=0, column=2, sticky="w")
directories_listbox = tk.Listbox(
    root, selectmode=tk.MULTIPLE, width=50, height=10)
directories_listbox.grid(row=1, column=2, padx=5, pady=5)
directories_scrollbar = tk.Scrollbar(root, command=directories_listbox.yview)
directories_scrollbar.grid(row=1, column=3, sticky="ns")
directories_listbox.config(yscrollcommand=directories_scrollbar.set)
add_directory_button = tk.Button(
    root, text="Add Directory", command=add_directory)
add_directory_button.grid(row=2, column=2, pady=5)
remove_directories_button = tk.Button(
    root, text="Remove Selected", command=lambda:
    remove_selected(directories_listbox))
remove_directories_button.grid(row=3, column=2, pady=5)

# Output name
output_name_label = tk.Label(root, text="Output PDF Name:")
output_name_label.grid(row=4, column=0, sticky="w", padx=5, pady=5)
output_name_entry = tk.Entry(root)
output_name_entry.grid(row=4, column=1, columnspan=2,
                       sticky="we", padx=5, pady=5)

# Convert button
convert_button = tk.Button(
    root, text="Convert and Save", command=convert_and_save)
convert_button.grid(row=5, column=0, columnspan=3, pady=5)

# Status label
status_label = tk.Label(root, text="")
status_label.grid(row=6, column=0, columnspan=3, pady=5)

root.mainloop()
