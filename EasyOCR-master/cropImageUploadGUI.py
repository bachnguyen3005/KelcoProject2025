import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

class ImageCropper:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Cropper")
        
        self.canvas = tk.Canvas(root, width=800, height=600)
        self.canvas.pack()
        
        self.upload_btn = tk.Button(root, text="Upload Image", command=self.upload_image)
        self.upload_btn.pack()
        
        self.rect = None
        self.start_x = None
        self.start_y = None
        self.rect_id = None
        self.image = None
        self.image_tk = None
        
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
    
    def upload_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.image = Image.open(file_path)
            self.display_image(self.image)
    
    def display_image(self, img):
        self.image_tk = ImageTk.PhotoImage(img)
        self.canvas.config(width=self.image_tk.width(), height=self.image_tk.height())
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.image_tk)
    
    def on_button_press(self, event):
        if self.image:
            self.start_x = event.x
            self.start_y = event.y
            self.rect = (self.start_x, self.start_y, self.start_x, self.start_y)
    
    def on_mouse_drag(self, event):
        if self.image:
            cur_x, cur_y = (event.x, event.y)
            self.rect = (self.start_x, self.start_y, cur_x, cur_y)
            
            if self.rect_id:
                self.canvas.delete(self.rect_id)
            
            self.rect_id = self.canvas.create_rectangle(*self.rect, outline='red', width=2)
    
    def on_button_release(self, event):
        if self.image:
            x1, y1, x2, y2 = self.rect
            if x1 < x2 and y1 < y2:
                cropped_image = self.image.crop((x1, y1, x2, y2))
                cropped_image.show()  # Display the cropped image
            
            self.rect = None
            if self.rect_id:
                self.canvas.delete(self.rect_id)
                self.rect_id = None

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageCropper(root)
    root.mainloop()
