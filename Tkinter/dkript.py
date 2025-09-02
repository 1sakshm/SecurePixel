import wave, base64, os, tkinter as tk, numpy as np
from tkinter import filedialog, messagebox, ttk
from PIL import Image
class AudioToImageDecryptor:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio to Image Decryptor")
        self.root.geometry("500x400")
        self.root.configure(bg="#27ae60")
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Custom.TButton', 
                       background="#e74c3c", 
                       foreground="white",
                       font=('Arial', 10, 'bold'))
        style.configure('Custom.TLabel',
                       background="#27ae60",
                       foreground="white",
                       font=('Arial', 12))
        self.setup_gui()
        
    def setup_gui(self):
        title_label = ttk.Label(self.root, text="Audio to Image Decryptor", 
                               font=('Arial', 18, 'bold'), style='Custom.TLabel')
        title_label.pack(pady=20)
        desc_label = ttk.Label(self.root, 
                              text="Restore your images from encrypted audio files",
                              style='Custom.TLabel')
        desc_label.pack(pady=10)
        file_frame = tk.Frame(self.root, bg="#27ae60")
        file_frame.pack(pady=30)
        
        self.file_label = ttk.Label(file_frame, text="No audio file selected", 
                                   style='Custom.TLabel')
        self.file_label.pack(pady=10)
        
        select_btn = ttk.Button(file_frame, text="Select Audio File", 
                               command=self.select_audio, style='Custom.TButton')
        select_btn.pack(pady=10)
        
        self.progress = ttk.Progressbar(self.root, mode='indeterminate')
        self.progress.pack(pady=20, padx=50, fill='x')

        convert_btn = ttk.Button(self.root, text="Decrypt to Image", 
                                command=self.convert_audio, style='Custom.TButton')
        convert_btn.pack(pady=20)

        self.status_label = ttk.Label(self.root, text="Ready to decrypt", 
                                     style='Custom.TLabel')
        self.status_label.pack(pady=10)
        self.selected_file = None
    def select_audio(self):
        file_types = [
            ("WAV files", "*.wav"),
            ("Audio files", "*.wav *.mp3 *.flac"),
            ("All files", "*.*")
        ]
        filename = filedialog.askopenfilename(
            title="Select an audio file",
            filetypes=file_types
        )
        if filename:
            self.selected_file = filename
            self.file_label.config(text=f"Selected: {os.path.basename(filename)}")
            self.status_label.config(text="Audio loaded - ready to decrypt")
            
    def audio_to_image(self, audio_path, output_path):
        try:
            with wave.open(audio_path, 'rb') as wav_file:
                sample_width = wav_file.getsampwidth()
                audio_data = wav_file.readframes(wav_file.getnframes())
                
            print(f"Audio sample width: {sample_width} bytes")
            if sample_width == 1:
                audio_samples = np.frombuffer(audio_data, dtype=np.uint8)
                data_bytes = audio_samples.tobytes()
            else:
                audio_samples = np.frombuffer(audio_data, dtype=np.int16)
                byte_values = (audio_samples.astype(np.int32) // 256) + 128
                byte_values = np.clip(byte_values, 0, 255)
                data_bytes = byte_values.astype(np.uint8).tobytes()
            
            print(f"Decoded {len(data_bytes)} bytes from audio")
            try:
                data_string = data_bytes.decode('utf-8')
            except UnicodeDecodeError as e:
                print(f"Unicode decode error: {e}")
                return False
            if not data_string.startswith("IMGDATA:"):
                print("Invalid file format - missing IMGDATA header")
                return False
            try:
                parts = data_string.split(':', 3)
                if len(parts) < 4:
                    print("Invalid metadata format")
                    return False
                _, width_str, height_str, b64_data = parts
                width = int(width_str)
                height = int(height_str)
                print(f"Decoded metadata: {width}x{height}")
            except ValueError as e:
                print(f"Metadata parsing error: {e}")
                return False
            try:
                compressed_data = base64.b64decode(b64_data)
                print(f"Base64 decoded: {len(compressed_data)} bytes")
            except Exception as e:
                print(f"Base64 decode error: {e}")
                return False
            try:
                import zlib
                img_data = zlib.decompress(compressed_data)
                print(f"Decompressed image data: {len(img_data)} bytes")
            except Exception as e:
                print(f"Zlib decompress error: {e}")
                return False
            with open(output_path, 'wb') as f:
                f.write(img_data)
            try:
                with Image.open(output_path) as img:
                    verify_width, verify_height = img.size
                    print(f"✓ Successfully restored image: {verify_width}x{verify_height}")
                    return True
            except Exception as e:
                print(f"Image verification error: {e}")
                return False
        except Exception as e:
            print(f"Error in conversion: {e}")
            import traceback
            traceback.print_exc()
            return False
    def convert_audio(self):
        if not self.selected_file:
            messagebox.showerror("Error", "Please select an audio file first!")
            return
        output_file = filedialog.asksaveasfilename(
            title="Save image file as...",
            defaultextension=".png",
            filetypes=[
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg"),
                ("All files", "*.*")
            ]
        )
        if output_file:
            self.progress.start()
            self.status_label.config(text="Decrypting audio to image...")
            self.root.update()
            try:
                success = self.audio_to_image(self.selected_file, output_file)
                self.progress.stop()
                if success:
                    self.status_label.config(text="Decryption completed successfully!")
                    messagebox.showinfo("Success", 
                                      f"Audio successfully decrypted to image!\nSaved as: {os.path.basename(output_file)}")
                else:
                    self.status_label.config(text="Decryption failed!")
                    messagebox.showerror("Error", "Failed to decrypt audio to image. Make sure the file was created by the encryptor.")
            except Exception as e:
                self.progress.stop()
                self.status_label.config(text="Decryption failed!")
                messagebox.showerror("Error", f"An error occurred: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AudioToImageDecryptor(root)
    root.mainloop()