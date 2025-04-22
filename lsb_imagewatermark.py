import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import datetime
import os

# ========================== Utility Functions ==========================

def text_to_binary(text):
    return ''.join(format(ord(i), '08b') for i in text)

def binary_to_text(binary):
    chars = [binary[i:i+8] for i in range(0, len(binary), 8)]
    return ''.join([chr(int(c, 2)) for c in chars if int(c, 2) != 0])

def encode_image(image_path, watermark_text, output_path):
    try:
        img = Image.open(image_path).convert("RGB")
    except Exception as e:
        raise ValueError(f"Error opening image: {e}")

    encoded = img.copy()
    width, height = img.size
    watermark_bin = text_to_binary(watermark_text) + '1111111111111110'

    if len(watermark_bin) > width * height:
        raise ValueError("Watermark text is too long for the selected image.")

    data_index = 0
    for y in range(height):
        for x in range(width):
            if data_index >= len(watermark_bin):
                break
            r, g, b = img.getpixel((x, y))
            r_bin = format(r, '08b')
            r_bin = r_bin[:-1] + watermark_bin[data_index]
            r = int(r_bin, 2)
            encoded.putpixel((x, y), (r, g, b))
            data_index += 1
        if data_index >= len(watermark_bin):
            break

    try:
        encoded.save(output_path)
    except Exception as e:
        raise ValueError(f"Error saving encoded image: {e}")
    
    generate_report(image_path, output_path, watermark_text, "Success")
    return output_path

def decode_image(image_path):
    try:
        img = Image.open(image_path).convert("RGB")
    except Exception as e:
        raise ValueError(f"Error opening image: {e}")

    binary_data = ''
    width, height = img.size

    for y in range(height):
        for x in range(width):
            r, g, b = img.getpixel((x, y))
            r_bin = format(r, '08b')
            binary_data += r_bin[-1]

    end_index = binary_data.find('1111111111111110')
    if end_index != -1:
        binary_data = binary_data[:end_index]
    else:
        return "[⚠️] No watermark found."

    return binary_to_text(binary_data)

def generate_report(original_path, encoded_path, watermark_text, status):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report = f"""
    ======= Watermarking Report =======

    Timestamp       : {now}
    Status          : {status}

    Original Image  : {os.path.basename(original_path)}
    Watermarked Image: {os.path.basename(encoded_path)}

    Image Size      : {Image.open(original_path).size}
    Watermark Text  : {watermark_text}

    Encoding Method : Least Significant Bit (LSB)
    EOF Marker      : 1111111111111110

    ====================================
    """
    with open("watermark_report.txt", "w") as f:
        f.write(report)

# ========================== GUI ==========================

class LSBWatermarkerApp:
    def __init__(self, master):
        self.master = master
        master.title("🔐 LSB Image Watermarking Tool")
        master.geometry("800x600")
        master.config(bg="#2E3B4E")

        self.image_path = ""

        # Add Frame for better organization
        self.main_frame = tk.Frame(master, bg="#2E3B4E")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.title = tk.Label(self.main_frame, text="LSB Image Watermarking Tool", font=("Helvetica", 22, "bold"), bg="#2E3B4E", fg="#FFFFFF")
        self.title.pack(pady=20)

        # Button to upload image with modern icon
        self.upload_btn = tk.Button(self.main_frame, text="📁 Upload Image", command=self.upload_image, font=("Helvetica", 14), bg="#4CAF50", fg="white", relief="flat", width=20)
        self.upload_btn.pack(pady=10)

        self.image_label = tk.Label(self.main_frame, bg="#2E3B4E")
        self.image_label.pack(pady=10)

        # Watermark entry with clear placeholder
        self.watermark_entry = tk.Entry(self.main_frame, width=40, font=("Helvetica", 14), bd=2)
        self.watermark_entry.insert(0, "Enter watermark text here...")
        self.watermark_entry.bind("<FocusIn>", self.clear_entry)
        self.watermark_entry.bind("<FocusOut>", self.restore_entry)
        self.watermark_entry.pack(pady=10)

        # Encoding Button with attractive design
        self.encode_btn = tk.Button(self.main_frame, text="🔒 Encode Watermark", command=self.encode_watermark, font=("Helvetica", 14), bg="#2196F3", fg="white", relief="flat", width=20)
        self.encode_btn.pack(pady=10)

        # Decoding Button with hover effect
        self.decode_btn = tk.Button(self.main_frame, text="🔍 Decode Watermark", command=self.decode_watermark, font=("Helvetica", 14), bg="#FF5722", fg="white", relief="flat", width=20)
        self.decode_btn.pack(pady=10)

        # Result Text Box for output
        self.result_text = tk.Text(self.main_frame, height=8, width=70, bg="#f0f0f0", font=("Helvetica", 12), bd=2)
        self.result_text.pack(pady=10)

    def clear_entry(self, event):
        if self.watermark_entry.get() == "Enter watermark text here...":
            self.watermark_entry.delete(0, tk.END)

    def restore_entry(self, event):
        if self.watermark_entry.get() == "":
            self.watermark_entry.insert(0, "Enter watermark text here...")

    def upload_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.bmp")])
        if file_path:
            self.image_path = file_path
            img = Image.open(file_path)
            img.thumbnail((250, 250))
            img = ImageTk.PhotoImage(img)
            self.image_label.configure(image=img)
            self.image_label.image = img
            self.result_text.delete(1.0, tk.END)

    def encode_watermark(self):
        if not self.image_path:
            messagebox.showwarning("Warning", "Please upload an image first!")
            return
        text = self.watermark_entry.get()

        if not text or text == "Enter watermark text here...":
            messagebox.showwarning("Warning", "Please enter a valid watermark text!")
            return

        output_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg")])
        if not output_path:
            return

        try:
            encode_image(self.image_path, text, output_path)
            messagebox.showinfo("Success", f"Watermark encoded! Saved as {output_path}")
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"✔️ Watermark encoded successfully!\nSaved as: {output_path}\n\nReport saved as watermark_report.txt")
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def decode_watermark(self):
        if not self.image_path:
            messagebox.showwarning("Warning", "Please upload an encoded image first!")
            return
        result = decode_image(self.image_path)
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, f"📩 Decoded Watermark:\n{result}")

# ========================== Run App ==========================

if __name__ == "__main__":
    root = tk.Tk()
    app = LSBWatermarkerApp(root)
    root.mainloop()
