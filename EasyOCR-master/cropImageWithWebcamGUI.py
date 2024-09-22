import cv2
import numpy as np
from tkinter import *
from PIL import Image, ImageTk

class WebcamCropper:
    def __init__(self, root):
        self.root = root
        self.root.title("Webcam Cropper")
        
        self.cap = cv2.VideoCapture(0)
        self.canvas = Canvas(root, width=640, height=480)
        self.canvas.pack()
        
        self.rect = None
        self.start_x = None
        self.start_y = None
        self.rect_id = None
        
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        
        self.update_frame()
    
    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            self.current_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.img = Image.fromarray(self.current_frame)
            self.imgtk = ImageTk.PhotoImage(image=self.img)
            self.canvas.create_image(0, 0, anchor=NW, image=self.imgtk)
        
        self.root.after(10, self.update_frame)
    
    def on_button_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.rect = (self.start_x, self.start_y, self.start_x, self.start_y)
    
    def on_mouse_drag(self, event):
        cur_x, cur_y = (event.x, event.y)
        self.rect = (self.start_x, self.start_y, cur_x, cur_y)
        
        if self.rect_id:
            self.canvas.delete(self.rect_id)
        
        self.rect_id = self.canvas.create_rectangle(*self.rect, outline='red', width=2)
    
    def on_button_release(self, event):
        x1, y1, x2, y2 = self.rect
        if x1 < x2 and y1 < y2:
            cropped_frame = self.current_frame[y1:y2, x1:x2]
            cropped_img = Image.fromarray(cropped_frame)
            cropped_img.show()  # Display the cropped image
            
        self.rect = None
        if self.rect_id:
            self.canvas.delete(self.rect_id)
            self.rect_id = None
    
    def __del__(self):
        self.cap.release()

if __name__ == "__main__":
    root = Tk()
    app = WebcamCropper(root)
    root.mainloop()
