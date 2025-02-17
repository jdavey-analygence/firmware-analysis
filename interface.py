import tkinter as tk
from tkinter import filedialog, messagebox
from image import create_image

class FileUploadGUI:
    def __init__(self, root):
        # Root setup
        self.root = root
        self.root.title("Firmware Extractor Interface")
        # Set the window size
        self.root.geometry("1500x1000")

        # Initialize instance variables
        self.file_path = None
        self.image = None

        # Set up the UI components
        self.setup_ui()

    def setup_ui(self):
        # Label for the uploaded file
        self.file_label = tk.Label(self.root, text="No file selected", wraplength=550)
        self.file_label.pack(pady=10)

        # Button to upload firmware image
        self.upload_button = tk.Button(self.root, text="Upload Firmware Image", command=self.upload_file)
        self.upload_button.pack(pady=10)

        # Button to identify filesystem type
        self.find_type_button = tk.Button(self.root, text="Identify Filesystem Type", command=self.filesystem_type, state=tk.DISABLED)
        self.find_type_button.pack(pady=10)

        # Button to extract filesystem
        self.extract_fs_button = tk.Button(self.root, text="Extract Filesystem", command=self.extract_filesystem, state=tk.DISABLED)
        self.extract_fs_button.pack(pady=10)

        # Button to print filesystem
        self.print_fs_button = tk.Button(self.root, text="Print Filesystem", command=self.print_filesystem, state=tk.DISABLED)
        self.print_fs_button.pack(pady=20)

        # Button to print kernel version
        self.print_kernel_version_button = tk.Button(self.root, text="Print Kernel Version", command=self.print_kernel_version, state=tk.DISABLED)
        self.print_kernel_version_button.pack(pady=20)

        # Button to print command injections
        self.print_injections_button = tk.Button(self.root, text="Find Command Injections", command=self.print_injections, state=tk.DISABLED)
        self.print_injections_button.pack(pady=20)

        # Text box to display information
        self.text_box = tk.Text(self.root, wrap=tk.WORD, width=150, height=35)
        self.text_box.pack(pady=10)

    def upload_file(self):
        new_file = filedialog.askopenfilename()
        if new_file:
            self.file_path = new_file
            self.file_label.config(text=f"Selected File: {self.file_path}")
            self.find_type_button.config(state=tk.NORMAL)
            self.extract_fs_button.config(state=tk.DISABLED)
            self.print_fs_button.config(state=tk.DISABLED)
            self.print_kernel_version_button.config(state=tk.DISABLED)
            self.print_injections_button.config(state=tk.DISABLED)

    def filesystem_type(self):
        if not self.file_path:
            return
        try:
            # If the image has not been created or the path has changed, create a new image
            if not self.image or self.image.path != self.file_path:
                self.image = create_image(self.file_path)
            self.clear_text_box()
            self.text_box.insert(tk.END, f"File System Type looks like: {self.image.fs_type}\n\n")
            if not self.image.mounted:
                self.extract_fs_button.config(state=tk.NORMAL)
            # If the filesystem is already mounted, enable the print filesystem and kernel version buttons
            else:
                self.extract_fs_button.config(state=tk.DISABLED)
                self.print_fs_button.config(state=tk.NORMAL)
                self.print_kernel_version_button.config(state=tk.NORMAL)
                self.print_injections_button.config(state=tk.NORMAL)
        except Exception as e:
            self.show_error("Failed to identify filesystem type", e)

    def extract_filesystem(self):
        self.clear_text_box()
        self.text_box.insert(tk.END, "You may have to enter your password in the terminal.\n")
        # Force update the UI to show the message immediately
        self.root.update_idletasks()
        
        # Schedule the extraction to start after a short delay
        self.root.after(100, self._perform_extraction)

    def _perform_extraction(self):
        if not self.image:
            return
        try:
            extracted_dir = self.image.extractFS()
            if self.image.mounted:
                self.clear_text_box()
                self.text_box.insert(tk.END, f"Extracted Directory: {extracted_dir}\n")
                self.text_box.insert(tk.END, f"Successfully mounted {self.image.fs_type} file system!\n")
                self.print_fs_button.config(state=tk.NORMAL)
                self.print_kernel_version_button.config(state=tk.NORMAL)
                self.print_injections_button.config(state=tk.NORMAL)
                self.extract_fs_button.config(state=tk.DISABLED)
        except Exception as e:
            self.show_error("Failed to extract filesystem", e)

    def print_filesystem(self):
        if not self.image or not self.image.mounted:
            self.show_error("Filesystem not mounted", "Error: File system has not been mounted!")
            return
        try:
            directories = self.image.printFS()
            self.clear_text_box()
            self.text_box.insert(tk.END, f'Here are the contents of the {self.image.fs_type} filesystem:\n{directories}\n')
        except Exception as e:
            self.show_error("Failed to print filesystem", e)

    def print_kernel_version(self):
        if not self.image or not self.image.mounted:
            self.show_error("Filesystem not mounted", "Error: File system has not been mounted!")
            return
        try:
            kernel = self.image.get_kernel_version()
            self.clear_text_box()
            self.text_box.insert(tk.END, f'Here is the kernel version of the filesystem: {kernel}\n')
        except Exception as e:
            self.show_error("Failed to find a kernel version", e)

    def print_injections(self):
        if not self.image or not self.image.mounted:
            self.show_error("Filesystem not mounted", "Error: File system has not been mounted!")
            return
        try:
            injections = self.image.get_command_injections()
            self.clear_text_box()
            self.text_box.insert(tk.END, f'Here are the command injection possibilities found in the filesystem:\n{injections}\n')
        except Exception as e:
            self.show_error("Failed to find command injections", e)

    def clear_text_box(self):
        self.text_box.delete(1.0, tk.END)

    def show_error(self, title, error):
        messagebox.showerror(title, str(error))


if __name__ == "__main__":
    root = tk.Tk()
    app = FileUploadGUI(root)
    root.mainloop()