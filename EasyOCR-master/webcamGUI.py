import cv2
import tkinter as tk
from tkinter import Label, Button, Text
from PIL import Image, ImageTk, ImageFont, ImageDraw, Image as PilImage
import numpy as np
from easyocr import Reader

class WebcamApp:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)

        self.video_source = 0  # Default webcam
        self.vid = cv2.VideoCapture(self.video_source)

        # Create a canvas that will show the video frame
        self.canvas = tk.Canvas(window, width=self.vid.get(cv2.CAP_PROP_FRAME_WIDTH),
                                height=self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.canvas.pack(side=tk.LEFT)

        # Create a canvas to show the captured image with OCR results
        self.captured_canvas = tk.Canvas(window, width=self.vid.get(cv2.CAP_PROP_FRAME_WIDTH),
                                         height=self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.captured_canvas.pack(side=tk.LEFT)

        # Create a text box to display the extracted text
        self.text_box = Text(window, width=25, height=10)
        self.text_box.pack(side=tk.RIGHT, padx=10, pady=20)

        # Button to take a snapshot
        self.btn_snapshot = Button(window, text="Take Snapshot & Detect Text", width=25, command=self.snapshot)
        self.btn_snapshot.pack(anchor=tk.CENTER, expand=True)

        self.delay = 15
        self.update()

        self.window.mainloop()

    def snapshot(self):
        # Get a frame from the video source
        ret, frame = self.vid.read()

        if ret:
            # Save the captured image to a file
            cv2.imwrite("snapshot.jpg", cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

            # Run OCR on the captured image
            img_with_text, extracted_text = self.run_ocr("snapshot.jpg")

            # Display the captured image with OCR results on the right canvas
            captured_image = ImageTk.PhotoImage(image=PilImage.fromarray(img_with_text))
            self.captured_canvas.create_image(0, 0, image=captured_image, anchor=tk.NW)
            self.captured_canvas.image = captured_image  # Keep a reference to avoid garbage collection

            # Display the extracted text in the text box
            self.text_box.delete(1.0, tk.END)
            self.text_box.insert(tk.END, extracted_text)

    def run_ocr(self, image_path):
        # Initialize the OCR reader
        reader = Reader(['en', 'pt'], gpu=True)

        # Read the image
        img = cv2.imread(image_path)
        original = img.copy()

        # Perform text recognition
        result = reader.readtext(img)

        # Function to draw the bounding box
        def box_coordinates(box):
            (lt, rt, br, bl) = box
            lt = (int(lt[0]), int(lt[1]))
            rt = (int(rt[0]), int(rt[1]))
            br = (int(br[0]), int(br[1]))
            bl = (int(bl[0]), int(bl[1]))
            return lt, rt, br, bl

        # Function to draw a rectangle and text
        def draw_img(img, lt, br, text, font_path='calibri.ttf', color=(200, 255, 0), thickness=2, font_size=22):
            cv2.rectangle(img, lt, br, color, thickness)
            font = ImageFont.truetype(font_path, font_size)
            img_pil = PilImage.fromarray(img)
            draw = ImageDraw.Draw(img_pil)
            draw.text((lt[0], lt[1] - font_size), text, font=font, fill=color)
            img = np.array(img_pil)
            return img

        # Apply OCR results to the image and prepare the extracted text
        extracted_text = ""
        for (box, text, probability) in result:
            lt, rt, br, bl = box_coordinates(box)
            img = draw_img(img, lt, br, text)
            extracted_text += f"{text}\n"

        return img, extracted_text

    def update(self):
        # Get a frame from the video source
        ret, frame = self.vid.read()

        if ret:
            # Convert the frame to a format that Tkinter can use
            self.photo = ImageTk.PhotoImage(image=PilImage.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))

            # Display the image on the left canvas
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)

        self.window.after(self.delay, self.update)

    def __del__(self):
        # Release the video source when the object is destroyed
        if self.vid.isOpened():
            self.vid.release()

# Create a window and pass it to the application object
WebcamApp(tk.Tk(), "Webcam Snapshot with OCR")
