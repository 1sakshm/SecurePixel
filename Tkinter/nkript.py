import tkinter as tk, numpy as np, wave, base64, os
from tkinter import filedialog, messagebox, ttk
from PIL import Image

class ImageToAudioEncryptor:
    def __init__(self, root):
        self.root = root
        self.root.title("Image to Audio Encryptor")
        self.root.geometry("500x400")
        self.root.configure(bg="#2c3e50")
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Custom.TButton', 
                       background="#3498db", 
                       foreground="white",
                       font=('Arial', 10, 'bold'))
        style.configure('Custom.TLabel',
                       background="#2c3e50",
                       foreground="white",
                       font=('Arial', 12))
        self.setup_gui()
        
    def setup_gui(self):
        title_label = ttk.Label(self.root, text="Image to Audio Encryptor", 
                               font=('Arial', 18, 'bold'), style='Custom.TLabel')
        title_label.pack(pady=20)
        desc_label = ttk.Label(self.root, 
                              text="Convert your images into audio files for secure storage",
                              style='Custom.TLabel')
        desc_label.pack(pady=10)
        file_frame = tk.Frame(self.root, bg="#2c3e50")
        file_frame.pack(pady=30)
        
        self.file_label = ttk.Label(file_frame, text="No file selected", 
                                   style='Custom.TLabel')
        self.file_label.pack(pady=10)
        
        select_btn = ttk.Button(file_frame, text="Select Image File", 
                               command=self.select_image, style='Custom.TButton')
        select_btn.pack(pady=10)
        self.progress = ttk.Progressbar(self.root, mode='indeterminate')
        self.progress.pack(pady=20, padx=50, fill='x')
        convert_btn = ttk.Button(self.root, text="Convert to Audio", 
                                command=self.convert_image, style='Custom.TButton')
        convert_btn.pack(pady=20)
        self.status_label = ttk.Label(self.root, text="Ready to encrypt", 
                                     style='Custom.TLabel')
        self.status_label.pack(pady=10)
        
        self.selected_file = None
        
    def select_image(self):
        file_types = [
            ("Image files", "*.png *.jpg *.jpeg *.bmp *.tiff *.gif"),
            ("PNG files", "*.png"),
            ("JPEG files", "*.jpg *.jpeg"),
            ("All files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Select an image file",
            filetypes=file_types
        )
        
        if filename:
            self.selected_file = filename
            self.file_label.config(text=f"Selected: {os.path.basename(filename)}")
            self.status_label.config(text="Image loaded - ready to convert")
            
    def image_to_audio(self, image_path, output_path):
        try:
            orig_size = os.path.getsize(image_path)
            print(f"Original image size: {orig_size} bytes")
            img = Image.open(image_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            width, height = img.size
            img_array = np.array(img)
            metadata = f"IMGDATA:{width}:{height}:"
            import io
            png_buffer = io.BytesIO()
            img.save(png_buffer, format='PNG', optimize=True, compress_level=9)
            compressed_img_data = png_buffer.getvalue()
            
            print(f"PNG compressed size: {len(compressed_img_data)} bytes")
            import zlib
            ultra_compressed = zlib.compress(compressed_img_data, level=9)
            print(f"Zlib compressed size: {len(ultra_compressed)} bytes")
            b64_data = base64.b64encode(ultra_compressed).decode('ascii')
            full_data = metadata + b64_data
            print(f"Total data length: {len(full_data)} characters")
            data_bytes = full_data.encode('utf-8')
            audio_samples = np.array([b for b in data_bytes], dtype=np.uint8)
            with wave.open(output_path, 'wb') as wav_file:
                wav_file.setnchannels(1)  
                wav_file.setsampwidth(1)  
                wav_file.setframerate(8000)
                wav_file.writeframes(audio_samples.tobytes())
            audio_size = os.path.getsize(output_path)
            compression_ratio = (orig_size - audio_size) / orig_size * 100
            print(f"Audio file size: {audio_size} bytes")
            print(f"Compression ratio: {compression_ratio:.1f}%")
            if audio_size < orig_size:
                print("✓ Audio file is smaller than original!")
            else:
                print("⚠ Audio file is larger than original")
            return True
            
        except Exception as e:
            print(f"Error in conversion: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    def convert_image(self):
        if not self.selected_file:
            messagebox.showerror("Error", "Please select an image file first!")
            return
        output_file = filedialog.asksaveasfilename(
            title="Save audio file as...",
            defaultextension=".wav",
            filetypes=[("WAV files", "*.wav"), ("All files", "*.*")]
        )
        
        if output_file:
            self.progress.start()
            self.status_label.config(text="Converting image to audio...")
            self.root.update()
            try:
                success = self.image_to_audio(self.selected_file, output_file)
                self.progress.stop()
                if success:
                    self.status_label.config(text="Conversion completed successfully!")
                    messagebox.showinfo("Success", 
                                      f"Image successfully converted to audio!\nSaved as: {os.path.basename(output_file)}")
                else:
                    self.status_label.config(text="Conversion failed!")
                    messagebox.showerror("Error", "Failed to convert image to audio.")
            except Exception as e:
                self.progress.stop()
                self.status_label.config(text="Conversion failed!")
                messagebox.showerror("Error", f"An error occurred: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageToAudioEncryptor(root)
    root.mainloop()