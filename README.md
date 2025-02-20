# The Isle Game MiniMap

## Overview
I enjoyed playing the game The Isle but I found it frustrating constantly getting lost every step of the way. The game has no map nor minimap system which motivated me to find a solution to this problem.
TheIsle Game MiniMap is a Python-based tool that captures a section of the screen, extracts coordinates using OCR, and displays a minimap with the extracted location marked. It is designed to assist with navigation by providing a visual representation of coordinates on a predefined map. I found the game frustrating with how huge the map is and had the idea to make a minimap when I saw that it had coordinates.

![Demonstration](MinimapDemonstration.png)


## Features
- Captures a portion of the screen to extract coordinate information.
- Uses OCR (Tesseract) to recognize and process coordinates.
- Displays a cropped minimap centered on the extracted coordinates.
- Provides UI controls for enabling auto-refresh, converting images to black and white, and adjusting settings.
- Drag-and-drop functionality for both the main window and the minimap.
- Works with different screen resolutions (4K, 2K, and 1080p).

## Requirements
Ensure you have the following installed before running the program:

### Dependencies
- Python 3.7+
- `pyautogui`
- `pytesseract`
- `Pillow`
- `tkinter`
- `keyboard`
- `requests`
- `screeninfo`

### External Requirements
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) (Ensure it is installed and configured properly on your system.)
- A local or online copy of the map image (`Map.png`). (I created the map by taking an existing map and setting the size of it to be 600 pixels as that is the max grid coordinate size.)

## Installation
1. Clone or download this repository.
2. Install the required dependencies using:
   ```sh
   pip install -r requirements.txt
   ```
3. Ensure Tesseract OCR is installed and its path is configured correctly.

## Usage
1. Run the script using:
   ```sh
   python main.py
   ```
2. The main admin window will open, displaying a canvas and control buttons.
3. Click **Refresh Map** to capture the screen, process coordinates, and update the minimap.
4. Enable **Refresh on Tab** to automatically update the map when the `Tab` key is pressed.
5. Enable **Convert to B/W** if OCR struggles with text recognition.
6. Drag the minimap window to reposition it as needed.
7. Press `Escape` to cancel auto-refresh.

## How It Works
1. **Screen Capture**: The script determines the screen resolution and captures a predefined region.
2. **OCR Processing**: Tesseract extracts numerical coordinates from the captured image.
3. **Coordinate Mapping**: Extracted coordinates are matched against a predefined map image.
4. **Minimap Display**: The program crops and displays a portion of the map centered on the extracted location, marking it with a red dot.

## Known Issues
- **OCR Errors**: If coordinates are not recognized correctly, try enabling **Convert to B/W** or adjusting the screenshot region (I am working on a method to grab the more clear image of both)
- **Multiple Monitor Errors**: I just discovered that if there are multiple monitors that it will grab one's resolution at random if you have multiple different resolutions.

## License
This project is open-source under the MIT License. 
I do not care what you do with this program or if you add onto it or even if you use it to make a similar program so long as you credit me.

## Author
[Ram-Rod6198]
