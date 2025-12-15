"""
Windows GUI application for any2md.
User-friendly interface for converting documents to Markdown.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import threading
import sys
from typing import List, Optional

# Add src to path for imports
src_path = Path(__file__).parent.parent
sys.path.insert(0, str(src_path))

from any2md.converters import DOCXConverter, PDFConverter, XLSXConverter
from any2md.core.config import ConversionConfig
from any2md.normalizer import MarkdownNormalizer


class Any2MdGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("any2md - Convert Any Document to Markdown")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Set icon (if available)
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass
        
        # Variables
        self.files_to_convert: List[Path] = []
        self.output_dir: Optional[Path] = None
        self.is_converting = False
        
        # Converters
        self.converters = {
            '.docx': DOCXConverter(),
            '.doc': DOCXConverter(),
            '.pdf': PDFConverter(),
            '.xlsx': XLSXConverter(),
            '.xls': XLSXConverter(),
        }
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface."""
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Main container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="📄 any2md",
            font=("Segoe UI", 24, "bold")
        )
        title_label.grid(row=0, column=0, pady=(0, 5))

        subtitle_label = ttk.Label(
            main_frame,
            text="Convert any document to Markdown",
            font=("Segoe UI", 10)
        )
        subtitle_label.grid(row=1, column=0, pady=(0, 20))
        
        # File selection section
        file_frame = ttk.LabelFrame(main_frame, text="Files to Convert", padding="10")
        file_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        file_frame.columnconfigure(0, weight=1)
        file_frame.rowconfigure(0, weight=1)
        
        # File listbox with scrollbar
        listbox_frame = ttk.Frame(file_frame)
        listbox_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        listbox_frame.columnconfigure(0, weight=1)
        listbox_frame.rowconfigure(0, weight=1)
        
        self.file_listbox = tk.Listbox(
            listbox_frame,
            height=10,
            font=("Segoe UI", 9)
        )
        self.file_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=self.file_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.file_listbox.configure(yscrollcommand=scrollbar.set)
        
        # File buttons
        file_btn_frame = ttk.Frame(file_frame)
        file_btn_frame.grid(row=1, column=0, pady=(10, 0))
        
        ttk.Button(
            file_btn_frame,
            text="➕ Add Files",
            command=self.add_files
        ).grid(row=0, column=0, padx=5)
        
        ttk.Button(
            file_btn_frame,
            text="📁 Add Folder",
            command=self.add_folder
        ).grid(row=0, column=1, padx=5)
        
        ttk.Button(
            file_btn_frame,
            text="🗑️ Remove Selected",
            command=self.remove_selected
        ).grid(row=0, column=2, padx=5)
        
        ttk.Button(
            file_btn_frame,
            text="🧹 Clear All",
            command=self.clear_all
        ).grid(row=0, column=3, padx=5)
        
        # Output directory section
        output_frame = ttk.LabelFrame(main_frame, text="Output Directory", padding="10")
        output_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        output_frame.columnconfigure(0, weight=1)
        
        self.output_label = ttk.Label(
            output_frame,
            text="No output directory selected",
            foreground="gray"
        )
        self.output_label.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        ttk.Button(
            output_frame,
            text="📂 Choose Directory",
            command=self.choose_output_dir
        ).grid(row=0, column=1)
        
        # Progress section
        progress_frame = ttk.Frame(main_frame)
        progress_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        progress_frame.columnconfigure(0, weight=1)

        self.progress_label = ttk.Label(
            progress_frame,
            text="Ready to convert",
            font=("Segoe UI", 9)
        )
        self.progress_label.grid(row=0, column=0, sticky=tk.W)

        self.progress_bar = ttk.Progressbar(
            progress_frame,
            mode='determinate',
            length=300
        )
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))

        # Convert button
        self.convert_btn = ttk.Button(
            main_frame,
            text="🚀 Convert Files",
            command=self.start_conversion,
            style="Accent.TButton"
        )
        self.convert_btn.grid(row=5, column=0, pady=(0, 10))

        # Status text area
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        status_frame.grid(row=6, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        status_frame.columnconfigure(0, weight=1)
        status_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(6, weight=1)

        self.status_text = tk.Text(
            status_frame,
            height=8,
            font=("Consolas", 9),
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.status_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        status_scrollbar = ttk.Scrollbar(
            status_frame,
            orient=tk.VERTICAL,
            command=self.status_text.yview
        )
        status_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.status_text.configure(yscrollcommand=status_scrollbar.set)

        # Configure button style
        style.configure("Accent.TButton", font=("Segoe UI", 11, "bold"))

    def add_files(self):
        """Add files to convert."""
        files = filedialog.askopenfilenames(
            title="Select files to convert",
            filetypes=[
                ("Supported files", "*.docx *.doc *.pdf *.xlsx *.xls"),
                ("Word documents", "*.docx *.doc"),
                ("PDF files", "*.pdf"),
                ("Excel files", "*.xlsx *.xls"),
                ("All files", "*.*")
            ]
        )

        for file in files:
            file_path = Path(file)
            if file_path not in self.files_to_convert:
                self.files_to_convert.append(file_path)
                self.file_listbox.insert(tk.END, file_path.name)

        self.log_status(f"Added {len(files)} file(s)")

    def add_folder(self):
        """Add all supported files from a folder."""
        folder = filedialog.askdirectory(title="Select folder")
        if not folder:
            return

        folder_path = Path(folder)
        supported_extensions = {'.docx', '.doc', '.pdf', '.xlsx', '.xls'}

        added = 0
        for ext in supported_extensions:
            for file_path in folder_path.rglob(f"*{ext}"):
                if file_path not in self.files_to_convert:
                    self.files_to_convert.append(file_path)
                    self.file_listbox.insert(tk.END, file_path.name)
                    added += 1

        self.log_status(f"Added {added} file(s) from folder")

    def remove_selected(self):
        """Remove selected files from the list."""
        selection = self.file_listbox.curselection()
        if not selection:
            return

        # Remove in reverse order to maintain indices
        for index in reversed(selection):
            self.file_listbox.delete(index)
            del self.files_to_convert[index]

        self.log_status(f"Removed {len(selection)} file(s)")

    def clear_all(self):
        """Clear all files from the list."""
        count = len(self.files_to_convert)
        self.files_to_convert.clear()
        self.file_listbox.delete(0, tk.END)
        self.log_status(f"Cleared {count} file(s)")

    def choose_output_dir(self):
        """Choose output directory."""
        directory = filedialog.askdirectory(title="Select output directory")
        if directory:
            self.output_dir = Path(directory)
            self.output_label.configure(
                text=str(self.output_dir),
                foreground="black"
            )
            self.log_status(f"Output directory: {self.output_dir}")

    def log_status(self, message: str):
        """Log a status message."""
        self.status_text.configure(state=tk.NORMAL)
        self.status_text.insert(tk.END, f"{message}\n")
        self.status_text.see(tk.END)
        self.status_text.configure(state=tk.DISABLED)

    def start_conversion(self):
        """Start the conversion process."""
        # Validation
        if not self.files_to_convert:
            messagebox.showwarning("No Files", "Please add files to convert")
            return

        if not self.output_dir:
            messagebox.showwarning("No Output Directory", "Please choose an output directory")
            return

        # Start conversion in a separate thread
        self.is_converting = True
        self.convert_btn.configure(state=tk.DISABLED)
        self.progress_bar['value'] = 0

        thread = threading.Thread(target=self.convert_files, daemon=True)
        thread.start()

    def convert_files(self):
        """Convert all files (runs in separate thread)."""
        total_files = len(self.files_to_convert)
        config = ConversionConfig(output_dir=self.output_dir)
        normalizer = MarkdownNormalizer()

        self.root.after(0, self.log_status, f"\n{'='*50}")
        self.root.after(0, self.log_status, f"Starting conversion of {total_files} file(s)...")
        self.root.after(0, self.log_status, f"{'='*50}\n")

        successful = 0
        failed = 0

        for i, file_path in enumerate(self.files_to_convert):
            # Update progress
            progress = int((i / total_files) * 100)
            self.root.after(0, self.update_progress, progress, f"Converting {file_path.name}...")

            try:
                # Get converter
                ext = file_path.suffix.lower()
                converter = self.converters.get(ext)

                if not converter:
                    self.root.after(0, self.log_status, f"❌ {file_path.name}: Unsupported format")
                    failed += 1
                    continue

                # Convert
                self.root.after(0, self.log_status, f"🔄 Converting: {file_path.name}")
                result = converter.convert(file_path, config)

                # Normalize
                if result.markdown_content:
                    result.markdown_content = normalizer.normalize(result.markdown_content)

                # Save
                output_file = self.output_dir / f"{file_path.stem}.md"
                output_file.write_text(result.markdown_content, encoding='utf-8')

                # Save images
                if result.images:
                    images_dir = self.output_dir / "images"
                    images_dir.mkdir(exist_ok=True)
                    for img_name, img_data in result.images.items():
                        img_path = images_dir / img_name
                        img_path.write_bytes(img_data)

                self.root.after(0, self.log_status, f"✅ {file_path.name} → {output_file.name}")
                successful += 1

            except Exception as e:
                self.root.after(0, self.log_status, f"❌ {file_path.name}: {str(e)}")
                failed += 1

        # Final progress
        self.root.after(0, self.update_progress, 100, "Conversion complete!")

        # Summary
        self.root.after(0, self.log_status, f"\n{'='*50}")
        self.root.after(0, self.log_status, f"Conversion Summary:")
        self.root.after(0, self.log_status, f"  ✅ Successful: {successful}")
        self.root.after(0, self.log_status, f"  ❌ Failed: {failed}")
        self.root.after(0, self.log_status, f"  📁 Output: {self.output_dir}")
        self.root.after(0, self.log_status, f"{'='*50}\n")

        # Re-enable button
        self.root.after(0, lambda: self.convert_btn.configure(state=tk.NORMAL))
        self.is_converting = False

        # Show completion message
        if successful > 0:
            self.root.after(0, lambda: messagebox.showinfo(
                "Conversion Complete",
                f"Successfully converted {successful} file(s)!\n\nOutput: {self.output_dir}"
            ))

    def update_progress(self, value: int, message: str):
        """Update progress bar and label."""
        self.progress_bar['value'] = value
        self.progress_label.configure(text=message)


def main():
    """Main entry point for the GUI."""
    root = tk.Tk()
    app = Any2MdGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()


