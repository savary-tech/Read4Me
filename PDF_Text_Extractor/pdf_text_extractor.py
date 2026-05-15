import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import PyPDF2
import re


class PDFTextExtractorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Text Extractor - One Line Per Page")
        self.root.geometry("900x700")

        self.text_content = ""

        # Buttons
        button_frame = tk.Frame(root)
        button_frame.pack(pady=10)

        load_button = tk.Button(
            button_frame,
            text="Load PDF",
            command=self.load_pdf,
            width=20
        )
        load_button.pack(side=tk.LEFT, padx=10)

        save_button = tk.Button(
            button_frame,
            text="Save Extracted Text",
            command=self.save_text,
            width=20
        )
        save_button.pack(side=tk.LEFT, padx=10)

        # Text display
        self.text_area = scrolledtext.ScrolledText(
            root,
            wrap=tk.WORD,
            font=("Arial", 11)
        )
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def clean_text_to_one_line(self, text):
        # Replace all newlines/tabs/multiple spaces with single spaces
        cleaned = re.sub(r'\s+', ' ', text)
        return cleaned.strip()

    def load_pdf(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("PDF Files", "*.pdf")]
        )

        if not file_path:
            return

        try:
            extracted_text = ""

            with open(file_path, "rb") as pdf_file:
                reader = PyPDF2.PdfReader(pdf_file)

                for page_num, page in enumerate(reader.pages, start=1):
                    page_text = page.extract_text()

                    if page_text:
                        cleaned_text = self.clean_text_to_one_line(page_text)
                    else:
                        cleaned_text = "[No readable text found on this page]"

                    extracted_text += f"--- Page {page_num} --- {cleaned_text}\n"

            self.text_content = extracted_text

            self.text_area.delete("1.0", tk.END)
            self.text_area.insert(tk.END, extracted_text)

            messagebox.showinfo(
                "Success",
                "PDF text extracted successfully!"
            )

        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Failed to extract text:\n{str(e)}"
            )

    def save_text(self):
        if not self.text_content:
            messagebox.showwarning(
                "No Text",
                "No extracted text to save."
            )
            return

        save_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt")]
        )

        if not save_path:
            return

        try:
            with open(save_path, "w", encoding="utf-8") as file:
                file.write(self.text_content)

            messagebox.showinfo(
                "Saved",
                "Text saved successfully!"
            )

        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Failed to save text:\n{str(e)}"
            )


if __name__ == "__main__":
    root = tk.Tk()
    app = PDFTextExtractorApp(root)
    root.mainloop()
