import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import os
import json

class ImageCoordinateSelector:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Image Coordinate Selector")

        self.image_label = tk.Label(self.root)
        self.image_label.pack()

        self.coordinates = []
        self.image_files = []
        self.current_image_index = 0
        self.current_image = None
        self.current_image_original = None
        self.output_file = "coordinates.json"

        self.image_label.bind("<Button-1>", self.save_coordinate)
        self.setup_ui()

    def setup_ui(self):
        tk.Button(self.root, text="Load Images", command=self.load_images).pack()
        tk.Button(self.root, text="Skip and Delete", command=self.skip_and_delete).pack()
        tk.Button(self.root, text="Save and Exit", command=self.save_and_exit).pack()

    def load_images(self):
        folder_path = filedialog.askdirectory(title="Select Image Folder")
        if not folder_path:
            return

        self.image_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.lower().endswith(('png', 'jpg', 'jpeg', 'bmp'))]
        if not self.image_files:
            print("No images found in the selected folder.")
            return

        self.display_image()

    def display_image(self):
        if self.current_image_index < len(self.image_files):
            image_path = self.image_files[self.current_image_index]
            self.current_image_original = Image.open(image_path)

            # Scale image to fit within the display window
            self.current_image = self.current_image_original.copy()
            display_width = 800
            display_height = 800
            self.current_image.thumbnail((display_width, display_height))

            img_tk = ImageTk.PhotoImage(self.current_image)
            self.image_label.config(image=img_tk)
            self.image_label.image = img_tk

            self.root.title(f"Image {self.current_image_index + 1}/{len(self.image_files)} - Click to select coordinate")
        else:
            print("All images processed.")
            self.image_label.config(image=None)
            self.root.title("All images processed")

    def save_coordinate(self, event):
        if self.current_image_original:
            image_path = self.image_files[self.current_image_index]
            file_name = os.path.splitext(os.path.basename(image_path))[0]

            # Scale coordinates back to original resolution
            original_width, original_height = self.current_image_original.size
            display_width, display_height = self.current_image.size

            x_scaled = int(event.x * (original_width / display_width))
            y_scaled = int(event.y * (original_height / display_height))

            x_normalized = round(x_scaled / original_width, 6)
            y_normalized = round(y_scaled / original_height, 6)

            self.coordinates.append({
                "file": file_name,
                "x": str(x_normalized),
                "y": str(y_normalized)
            })
            print(f"Saved coordinate for {file_name}: (xscaled: {x_scaled}, xnorm: {x_normalized}, yscaled: {y_scaled}, ynorm: {y_normalized})")

            self.current_image_index += 1
            self.display_image()

    def skip_and_delete(self):
        if self.current_image_index < len(self.image_files):
            image_path = self.image_files[self.current_image_index]
            try:
                os.remove(image_path)
                print(f"Deleted image: {image_path}")
            except Exception as e:
                print(f"Error deleting image: {e}")

            self.image_files.pop(self.current_image_index)
            self.display_image()
        else:
            print("No more images to skip and delete.")

    def save_and_exit(self):
        with open(self.output_file, "w") as f:
            json.dump(self.coordinates, f, indent=4)
        print(f"Coordinates saved to {self.output_file}")
        self.root.destroy()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ImageCoordinateSelector()
    app.run()