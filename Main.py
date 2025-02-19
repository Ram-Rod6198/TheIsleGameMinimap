import pyautogui
import pytesseract
from PIL import Image, ImageDraw, ImageTk
import re
import tkinter as tk
from tkinter import Label, Button, Checkbutton, BooleanVar
import keyboard
import requests
from io import BytesIO
import os
import re
import tkinter as tk
from screeninfo import get_monitors

def get_screen_resolution():
    monitors = get_monitors()
    if monitors:
        width = monitors[0].width
        height = monitors[0].height
        print(f"Actual resolution: {width}x{height}")
        return width, height
    else:
        print("Failed to retrieve screen resolution.")
        return 0, 0

def get_image_region(width, height):  
    # 4K resolution
    if (width, height) == (3840, 2160) or (width, height) == (2160, 3840):
        return 2815, 305, 260, 110
    # 2K resolution
    elif (width, height) == (2560, 1440) or (width, height) == (1440, 2560):
        return 1875, 200, 175, 75
    # 1080p resolution
    elif (width, height) == (1920, 1080) or (width, height) == (1080, 1920):
        return 1400, 145, 145, 60
    # Default case (fallback)
    else:
        return 1400, 145, 145, 60  


def get_capture_area():
    width, height = get_screen_resolution()
    x, y, region_width, region_height = get_image_region(width, height)
    return x, y, region_width, region_height

class UIManager:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller  # Reference to main app controller

        self.root.title("Isle MiniMap - Admin Info")
        self.root.attributes("-topmost", True)

        # UI Components
        self.screenshot_canvas = tk.Canvas(self.root, width=175, height=75, bg='black')
        self.screenshot_canvas.pack()

        self.auto_process_var = BooleanVar()
        self.auto_process_checkbox = Checkbutton(self.root, text="Refresh on Tab", variable=self.auto_process_var)
        self.auto_process_checkbox.pack()

        self.convert_to_bw_var = BooleanVar()
        self.convert_to_bw_checkbox = Checkbutton(self.root, text="Convert to B/W", variable=self.convert_to_bw_var)
        self.convert_to_bw_checkbox.pack()

        self.process_button = Button(self.root, text="Refresh Map", command=self.controller.process_image)
        self.process_button.pack()

        self.quit_button = Button(self.root, text="Exit", command=root.quit)
        self.quit_button.pack()

        self.latitude_label = Label(self.root, text="Latitude: Not processed")
        self.latitude_label.pack()
        self.longitude_label = Label(self.root, text="Longitude: Not processed")
        self.longitude_label.pack()

    def update_coordinates(self, latitude, longitude):
        self.latitude_label.config(text=f"Latitude: {latitude}")
        self.longitude_label.config(text=f"Longitude: {longitude}")

    def update_image(self, image_path):
        image = Image.open(image_path)
        photo = ImageTk.PhotoImage(image)
        self.screenshot_canvas.create_image(0, 0, anchor=tk.NW, image=photo)
        self.screenshot_canvas.image = photo
    
class ScreenCapture:
    def __init__(self, convert_to_bw=False):
        self.convert_to_bw = convert_to_bw

    def capture_screenshot(self):
        x, y, width, height = get_capture_area()
        screenshot = pyautogui.screenshot(region=(x, y, width, height))
        return self._process_image(screenshot)

    def _process_image(self, image):
        if self.convert_to_bw:
            # Convert to grayscale
            image = image.convert("L")  
        return image

    def extract_coordinates(self, image):
        coordinates_text = pytesseract.image_to_string(image)
        coordinates = re.findall(r'-?\d+', coordinates_text)
        coordinates = [int(c) for c in coordinates if -600 <= int(c) <= 600]
        
        if len(coordinates) == 2:
            return coordinates[0], coordinates[1]
        # OCR failed to extract valid coordinates
        return None, None  

class ImageProcessorApp:
    def __init__(self, root, map_window):
        # Main root window for admin info (Normal window)
        self.root = root
        self.root.title("Isle MiniMap - Admin Info")
        # Keeps this on the top to overlay on game
        self.root.attributes("-topmost", True)  
        # Separate window for the map image (Overlay)
        self.map_window = map_window
        self.map_window.title("Isle MiniMap - Map")
        # Borderless = true
        self.map_window.overrideredirect(True)  
        self.map_window.attributes("-topmost", True)
        # Keep the transparency
        self.map_window.attributes("-alpha", 0.7)  

        # Track the position for dragging
        self.offset_x = 0
        self.offset_y = 0
        self.map_offset_x = 0
        self.map_offset_y = 0

        # Bind mouse events for dragging (admin window)
        self.root.bind("<Button-1>", self.click_window)
        self.root.bind("<B1-Motion>", self.drag_window)

        # Bind mouse events for dragging (map window)
        self.map_window.bind("<Button-1>", self.click_map_window)
        self.map_window.bind("<B1-Motion>", self.drag_map_window)

        # Setup GUI components for admin window
        self.screenshot_canvas = tk.Canvas(self.root, width=175, height=75, bg='black')
        self.screenshot_canvas.pack()

        # Refresh on Tab
        self.auto_process_var = BooleanVar()
        self.auto_process_checkbox = Checkbutton(self.root, text="Refresh on Tab", variable=self.auto_process_var, fg='black')
        self.auto_process_checkbox.pack()

        # Convert to B/W
        self.convert_to_bw_var = BooleanVar()
        self.convert_to_bw_checkbox = Checkbutton(self.root, text="Convert to B/W", variable=self.convert_to_bw_var, fg='black')
        self.convert_to_bw_checkbox.pack()

        # Cancel Auto Refresh on Escape
        self.cancel_auto_process_var = BooleanVar()
        self.cancel_auto_process_checkbox = Checkbutton(self.root, text="Cancel Auto Refresh on Escape", variable=self.cancel_auto_process_var, fg='black')
        self.cancel_auto_process_checkbox.pack()

        self.process_button = Button(self.root, text="Refresh Map", command=self.process_image, fg='black')
        self.process_button.pack()

        self.quit_button = Button(self.root, text="Exit", command=root.quit, fg='black')
        self.quit_button.pack()

        self.latitude_label = Label(self.root, text="Latitude: Not processed", fg='black')
        self.latitude_label.pack()
        self.longitude_label = Label(self.root, text="Longitude: Not processed", fg='black')
        self.longitude_label.pack()

        # Setup GUI components for map window
        self.cropped_map_canvas = tk.Canvas(self.map_window, width=200, height=200, bg='black')
        self.cropped_map_canvas.pack()

        # Bind Escape key to handle auto process cancellation
        self.root.bind('<Escape>', self.handle_escape)

        # Set up global key listeners
        keyboard.on_press_key('tab', self.handle_tab)

        self.auto_processing_enabled = False
        self.previous_cropped_image_path = "cropped_map_with_marker.png"

    def handle_escape(self, event=None):
        if self.auto_process_var.get():
            self.auto_process_var.set(False)
            print("Auto process canceled")

    def handle_tab(self, event=None):
        if self.auto_process_var.get():
            self.process_image()

    def click_window(self, event):
        self.offset_x = event.x_root - self.root.winfo_x()
        self.offset_y = event.y_root - self.root.winfo_y()

    def drag_window(self, event):
        new_x = event.x_root - self.offset_x
        new_y = event.y_root - self.offset_y
        self.root.geometry(f"+{new_x}+{new_y}")

    def click_map_window(self, event):
        self.map_offset_x = event.x_root - self.map_window.winfo_x()
        self.map_offset_y = event.y_root - self.map_window.winfo_y()

    def drag_map_window(self, event):
        new_x = event.x_root - self.map_offset_x
        new_y = event.y_root - self.map_offset_y
        self.map_window.geometry(f"+{new_x}+{new_y}")

    def display_image(self, image_path, canvas, width, height):
        image = Image.open(image_path)
        image = image.resize((width, height), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(image)
        canvas.create_image(0, 0, anchor=tk.NW, image=photo)
        canvas.image = photo

    def convert_to_bw(self, image):
        if self.convert_to_bw_var.get():
             # Converts to grayscale
            return image.convert("L") 
        return image

    def process_image(self):
        # Capture a region of the screen
        x, y, width, height = get_capture_area()

        screenshot = pyautogui.screenshot(region=(x, y, width, height))

        # Convert the screenshot to grayscale (black and white)
        grayscale_screenshot = self.convert_to_bw(screenshot)

        # Save the grayscale screenshot
        grayscale_screenshot.save("screenshot.png")

        # Display the screenshot
        self.display_image("screenshot.png", self.screenshot_canvas, width, height)

        # Load the grayscale screenshot
        image = Image.open("screenshot.png")

        # Use Tesseract to extract text
        coordinates_text = pytesseract.image_to_string(image)

        # Replace '=' with '-'
        modified_text = coordinates_text.replace('=', '-')

        # Remove everything after the numbers
        cleaned_text = re.sub(r'[^\d\n-]+.*', '', modified_text).strip()

        # Extract numbers with optional leading minus sign
        coordinates = []
        for line in cleaned_text.splitlines():
            result = re.match(r'-?\d+', line)
            if result:
                coordinate_str = result.group()
                # Ensure coordinate is within valid range
                if -600 <= int(coordinate_str) <= 600:
                    coordinates.append(int(coordinate_str))
                else:
                    # Truncate to the first 3 digits
                    truncated_coordinate_str = coordinate_str[:4]  
                    truncated_coordinate = int(truncated_coordinate_str)
                    coordinates.append(truncated_coordinate)
                    print(f"Coordinate {coordinate_str} is out of range; using truncated value {truncated_coordinate}.")

        if len(coordinates) == 2:
            latitude, longitude = coordinates
            self.latitude_label.config(text=f"Latitude: {latitude}")
            self.longitude_label.config(text=f"Longitude: {longitude}")
            self.save_coordinates_to_file(coordinates_text, modified_text, latitude, longitude)
            self.crop_and_mark_map(coordinates)
        else:
            print("Failed to extract valid coordinates.")
            self.display_image(self.previous_cropped_image_path, self.cropped_map_canvas, 200, 200)

    def save_coordinates_to_file(self, original_text, modified_text, latitude, longitude):
        with open("coordinates.txt", "w") as file:
            file.write(f"Original Text:\n{original_text}\n\n")
            file.write(f"Modified Text:\n{modified_text}\n\n")
            file.write(f"Latitude: {latitude}\n")
            file.write(f"Longitude: {longitude}\n")

    def crop_and_mark_map(self, coordinates):
        latitude, longitude = coordinates

        # Define the relative path to the local image
        local_image_path = os.path.join(os.path.dirname(__file__), 'Map.png')

        if os.path.exists(local_image_path):
            # Load the map image from the local file if it exists
            map_image = Image.open(local_image_path).convert("RGBA")
        else:
            # If the file doesn't exist locally, download it from GitHub
            image_url = "https://raw.githubusercontent.com/Ram-Rod6198/TheIsleMiniMap/main/Map.png"
            response = requests.get(image_url)
            image_data = BytesIO(response.content)
            map_image = Image.open(image_data).convert("RGBA")

        # Calculate the center point of the crop area
        center_x = (longitude + 600) * map_image.width // 1200
        center_y = (latitude + 600) * map_image.height // 1200

        # Define the crop box (200x200 centered on the calculated point)
        crop_radius = 100
        crop_box = (
            center_x - crop_radius,
            center_y - crop_radius,
            center_x + crop_radius,
            center_y + crop_radius
        )

        # Crop the image
        cropped_image = map_image.crop(crop_box)

        # Draw a small dot in the center of the cropped image
        center_dot_radius = 3
        draw = ImageDraw.Draw(cropped_image)
        center_dot = (
            crop_radius - center_dot_radius,
            crop_radius - center_dot_radius,
            crop_radius + center_dot_radius,
            crop_radius + center_dot_radius
        )
        draw.ellipse(center_dot, fill='red')

        # Save the cropped image with the marker
        cropped_image_path = "cropped_map_with_marker.png"
        cropped_image.save(cropped_image_path)

        # Display the cropped image in the map window
        self.display_image(cropped_image_path, self.cropped_map_canvas, 200, 200)

        self.previous_cropped_image_path = cropped_image_path

    def run(self):
        self.root.mainloop()
        self.map_window.mainloop()

# Usage
if __name__ == "__main__":
    root = tk.Tk()
    map_window = tk.Toplevel(root)
    app = ImageProcessorApp(root, map_window)
    app.run()
