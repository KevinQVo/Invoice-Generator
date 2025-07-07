from fpdf import FPDF
import pandas as pd
import os
from datetime import datetime

# Load invoice data
df = pd.read_csv("invoice_data_template_randomized.csv")  

# Output directory
output_dir = "indented_invoice_pair_pdfs"
os.makedirs(output_dir, exist_ok=True)

class IndentedInvoicePDF(FPDF):
    def __init__(self):
        super().__init__(orientation='L', unit='mm', format='A4')
        self.set_auto_page_break(auto=True, margin=10)
        self.set_margins(10, 10, 10)
        self.label_width = 45
        self.y_start = 0

    def header(self):
        self.set_fill_color(0, 0, 0)
        self.set_text_color(255, 255, 255)
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "SMA Refund Reimbursement Form:", ln=True, align='C', fill=True)
        self.set_text_color(0, 0, 0)
        self.line(10, 20, 287, 20)
        self.y_start = self.get_y() + 4
        self.ln(4)

    def field_row(self, label, value, bold=False, draw_line=False):
        self.set_font("Arial", "B" if bold else "", 11)
        self.cell(self.label_width, 8, str(label), ln=0)
        y_current = self.get_y()
        self.line(10 + self.label_width, y_current, 10 + self.label_width, y_current + 8)
        self.set_font("Arial", "", 11)
        self.cell(0, 8, str(value), ln=1)
        if draw_line:
            self.line(10, self.get_y(), 287, self.get_y())

    def multi_address_block(self, row):
        for i, key in enumerate(["Street Address Line 1", "Street Address Line 2"]):
            line = row.get(key, "")
            if pd.notna(line) and str(line).strip():
                self.field_row("Street Address:" if i == 0 else "", line)

        city = row.get("Street Address Line 3", "").strip()
        state_zip = row.get("Street Address Line 4", "").strip()
        if city and state_zip:
            self.field_row("", f"{city}, {state_zip}")

    def invoice_pair_block(self, row):
        indent_x = 54.5
        box_widths = [60, 60, 60]
        heights = [8, 8]

        y_before = self.get_y()
        x_start = indent_x
        self.set_x(x_start)

        # First row: Original Invoice
        self.set_font("Arial", "B", 11)
        self.cell(box_widths[0], heights[0], "Original Invoice No. & Amount", border=1)
        self.set_font("Arial", "", 11)
        self.cell(box_widths[1], heights[0], str(row["Original Invoice Number"]), border=1)
        self.cell(box_widths[2], heights[0], f"${float(row['Original Invoice Ammount']):,.2f}", border=1)
        self.ln()

        # Second row: Pro-rated Invoice
        self.set_x(x_start)
        self.set_font("Arial", "B", 11)
        self.cell(box_widths[0], heights[1], "Pro-rated Invoice No. & Amount", border=1)
        self.set_font("Arial", "", 11)
        self.cell(box_widths[1], heights[1], str(row["Prorated Invoice Number"]), border=1)
        self.cell(box_widths[2], heights[1], f"${float(row['Pro-Rated Invoice Ammount']):,.2f}", border=1)
        self.ln()

# Generate PDFs
for _, row in df.iterrows():
    pdf = IndentedInvoicePDF()
    pdf.add_page()

    pdf.field_row("Vendor ID:", row["Vendor ID"], draw_line=True)
    pdf.field_row("Vendor Name:", row["Vendor Name"])
    pdf.multi_address_block(row)

    pdf.field_row("Invoice No.", row["Invoice Number"], bold=True)
    pdf.field_row("Invoice Date", datetime.now().strftime("%m/%d/%Y"))
    pdf.field_row("Refund Amount $", f"${float(row['Refund Amount']):,.2f}")
    pdf.field_row("Distribution Coding", "xxxxxxxxxxx")

    pdf.field_row("Description:", "Account Termination")
    pdf.invoice_pair_block(row)

    pdf.field_row("Preparer", "SMA Ops Billing Team")
    pdf.field_row("Approver", "John Doe")
    pdf.set_font("Arial", "B", 11)
    pdf.cell(45, 8, "Coupa Description:", ln=0)
    y_footer = pdf.get_y()
    pdf.line(10 + pdf.label_width, y_footer, 10 + pdf.label_width, y_footer + 8)
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 8, "Please add Watcher Group: AMRSPI", ln=1)

    x, y = 10, 10
    w, h = pdf.get_y() - 10
    pdf.rect(x, y, 277, h)
    pdf.line(x + pdf.label_width, pdf.y_start, x + pdf.label_width, 10 + h)

    filename = os.path.join(output_dir, f"{row['Vendor ID']}.pdf")
    pdf.output(filename)

print("✅ All PDFs generated with bordered invoice fields.")
