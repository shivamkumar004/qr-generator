import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import qrcode
import os
import re
from reportlab.pdfgen import canvas
import svgwrite


class QRCodeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("QR Code Generator")
        self.root.geometry("450x600")
        self.root.resizable(False, False)

        self.qr_type = tk.StringVar(value="Text")
        self.data = tk.StringVar()
        self.qr_image = None
        self.tk_img = None
        self.uploaded_image_path = None
        self.fore_color = "#000000"
        self.back_color = "#ffffff"

        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self.root, text="QR Code Generator", font=("Arial", 16, "bold")).pack(pady=10)

        # QR Code Type Dropdown
        ttk.Label(self.root, text="Select QR Code Type:").pack()
        types = ["Text", "URL", "Phone Number", "Image"]
        self.type_menu = ttk.Combobox(self.root, values=types, textvariable=self.qr_type, state="readonly")
        self.type_menu.pack(pady=5)
        self.type_menu.bind("<<ComboboxSelected>>", self.toggle_image_upload)

        # Upload Button
        self.upload_btn = ttk.Button(self.root, text="Upload Image", command=self.upload_image)
        self.upload_btn.pack(pady=3)
        self.upload_btn.pack_forget()

        # Input Field
        self.data_label = ttk.Label(self.root, text="Enter Text:")
        self.data_label.pack()
        self.data_entry = ttk.Entry(self.root, textvariable=self.data, width=50)
        self.data_entry.pack(pady=5)

        # Color selectors
        ttk.Button(self.root, text="Choose Foreground Color", command=self.choose_fore_color).pack(pady=3)
        ttk.Button(self.root, text="Choose Background Color", command=self.choose_back_color).pack(pady=3)

        # Generate QR
        ttk.Button(self.root, text="Generate QR Code", command=self.generate_qr).pack(pady=10)

        # QR Code display area
        self.qr_canvas = tk.Label(self.root)
        self.qr_canvas.pack(pady=10)

        # Save/Export
        ttk.Button(self.root, text="Save as PNG", command=self.save_png).pack(pady=3)
        ttk.Button(self.root, text="Export as PDF", command=self.export_pdf).pack(pady=3)
        ttk.Button(self.root, text="Export as SVG", command=self.export_svg).pack(pady=3)

    def toggle_image_upload(self, event=None):
        selected_type = self.qr_type.get()
        self.data.set("")
        self.uploaded_image_path = None

        if selected_type == "Image":
            self.data_label.config(text="Image Path:")
            self.data_entry.pack_forget()
            self.upload_btn.pack(pady=3)
        elif selected_type == "URL":
            self.data_label.config(text="Enter URL (must start with https:// and contain .com):")
            self.upload_btn.pack_forget()
            self.data_entry.pack(pady=5)
        elif selected_type == "Phone Number":
            self.data_label.config(text="Enter 10-digit Phone Number:")
            self.upload_btn.pack_forget()
            self.data_entry.pack(pady=5)
        else:
            self.data_label.config(text=f"Enter {selected_type}:")
            self.upload_btn.pack_forget()
            self.data_entry.pack(pady=5)

    def upload_image(self):
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp")])
        if path:
            self.uploaded_image_path = path
            self.data.set(path)

    def choose_fore_color(self):
        from tkinter.colorchooser import askcolor
        color = askcolor()[1]
        if color:
            self.fore_color = color

    def choose_back_color(self):
        from tkinter.colorchooser import askcolor
        color = askcolor()[1]
        if color:
            self.back_color = color

    def validate_input(self):
        qr_type = self.qr_type.get()
        value = self.data.get().strip()

        if not value:
            return False, "Input cannot be empty."

        if qr_type == "URL":
            if not (value.startswith("http://") or value.startswith("https://")):
                return False, "URL must start with 'http://' or 'https://'"
            if ".com" not in value:
                return False, "URL must contain '.com'"

        elif qr_type == "Phone Number":
            if not re.match(r"^\d{10}$", value):
                return False, "Phone number must be exactly 10 digits (no '+' or special characters)."

        elif qr_type == "Image":
            if not os.path.isfile(value):
                return False, "Invalid image path."

        return True, ""

    def generate_qr(self):
        valid, msg = self.validate_input()
        if not valid:
            messagebox.showerror("Validation Error", msg)
            return

        data = self.data.get().strip()
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(data)
        qr.make(fit=True)
        self.qr_image = qr.make_image(fill_color=self.fore_color, back_color=self.back_color)

        img = self.qr_image.resize((220, 220))
        self.tk_img = ImageTk.PhotoImage(img)
        self.qr_canvas.config(image=self.tk_img)
        self.qr_canvas.image = self.tk_img

    def save_png(self):
        if self.qr_image is None:
            messagebox.showwarning("Warning", "Please generate a QR code first.")
            return

        path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
        if path:
            self.qr_image.save(path)
            messagebox.showinfo("Saved", f"QR code saved to:\n{path}")

    def export_pdf(self):
        if self.qr_image is None:
            messagebox.showwarning("Warning", "Generate QR code first.")
            return

        path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if path:
            try:
                self.qr_image.save("temp_qr.png")
                c = canvas.Canvas(path)
                c.drawImage("temp_qr.png", 100, 600, width=200, height=200)
                c.save()
                os.remove("temp_qr.png")
                messagebox.showinfo("Success", "Exported QR code to PDF.")
            except Exception as e:
                messagebox.showerror("Export Error", str(e))

    def export_svg(self):
        if self.data.get().strip() == "":
            messagebox.showwarning("Warning", "Generate QR code first.")
            return

        path = filedialog.asksaveasfilename(defaultextension=".svg", filetypes=[("SVG files", "*.svg")])
        if path:
            try:
                dwg = svgwrite.Drawing(path, profile='tiny')
                dwg.add(dwg.text(self.data.get(), insert=(10, 20)))
                dwg.save()
                messagebox.showinfo("Success", "Exported to SVG.")
            except Exception as e:
                messagebox.showerror("Export Error", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = QRCodeApp(root)
    root.mainloop()
