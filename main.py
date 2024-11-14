import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
from PyPDF2 import PdfReader
from fpdf import FPDF

class PDFMergerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Merger")
        self.root.geometry("400x200")
        self.pdf_paths = []
        self.label = tk.Label(root, text="Merge PDF Documents with Line Item Quantities")
        self.label.pack(pady=10)

        self.select_button = tk.Button(root, text="Select PDF Files", command=self.select_files)
        self.select_button.pack(pady=5)

        self.merge_button = tk.Button(root, text="Merge and Save", command=self.merge_and_save)
        self.merge_button.pack(pady=5)

    def select_files(self):
        self.pdf_paths = filedialog.askopenfilenames(filetypes=[("PDF Files", "*.pdf")])
        if self.pdf_paths:
            messagebox.showinfo("Files Selected", f"{len(self.pdf_paths)} files selected.")

    def extract_data_from_pdf(self, pdf_path):
        """Extracts line item data from a PDF file with flexible parsing."""
        reader = PdfReader(pdf_path)
        data = []

        for page in reader.pages:
            text = page.extract_text()
            lines = text.splitlines()

            for line in lines:
                if 'Product' in line and 'Quantity' in line:
                    continue 
                try:
                    parts = line.split(' - ')
                    if len(parts) == 2:
                        item = parts[0].strip()
                        quantity = int(parts[1].strip())
                        data.append({'Product': item, 'Quantity': quantity})
                    else:
                       
                        pass
                except ValueError:
                    pass  

        return pd.DataFrame(data)

    def merge_pdf_data(self):
        """Combines line item quantities across all selected PDFs, grouping by normalized product name."""
        all_data = [self.extract_data_from_pdf(path) for path in self.pdf_paths]
        if all_data:
            combined_df = pd.concat(all_data)
            combined_df['Product'] = combined_df['Product'].str.lower().str.strip()  
            merged_data = combined_df.groupby('Product', as_index=False).sum()
            return merged_data
        else:
            messagebox.showerror("Error", "No data found in selected PDFs.")
            return None

    def save_to_pdf(self, merged_df, output_pdf):
        """Saves merged data to a PDF file."""
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Merged Product Quantities", ln=True, align='C')

        for index, row in merged_df.iterrows():
            line = f"{row['Product']} - {row['Quantity']}"
            pdf.cell(200, 10, txt=line, ln=True)

        pdf.output(output_pdf)
        messagebox.showinfo("Success", f"Merged PDF saved as {output_pdf}")

    def merge_and_save(self):
        if not self.pdf_paths:
            messagebox.showerror("Error", "No PDF files selected.")
            return

        merged_df = self.merge_pdf_data()
        if merged_df is not None:
            save_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
            if save_path:
                self.save_to_pdf(merged_df, save_path)
root = tk.Tk()
app = PDFMergerApp(root)
root.mainloop()
