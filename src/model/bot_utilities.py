'''
This file contains a collection of general purpose bot functions that are used by the bot classes.
MPos was used to acquire hardcoded coordinates.

For more on ImageSearch, see: https://brokencode.io/how-to-easily-image-search-with-python/
'''
import argparse
from collections import namedtuple
import cv2
from easyocr import Reader
import pathlib
import pyautogui as pag
import pygetwindow
from PIL import ImageGrab
from python_imagesearch.imagesearch import imagesearcharea, region_grabber
import time

# --- The path to this directory ---
PATH = pathlib.Path(__file__).parent.resolve()

# --- The path to the bot images directory ---
IMAGES_PATH = "./src/images/bot"

# --- Named Tuples ---
Point = namedtuple('Point', 'x y')
Rectangle = namedtuple('Rectangle', 'start end')

# --- Desired client position ---
window = Rectangle(start=(0, 0), end=(809, 534))

# ------- Rects of Interest -------
activity_rect = Rectangle(start=(10, 52), end=(171, 93))  # top left corner of screen

# ------- Points of Interest -------
# --- Orbs ---
orb_compass = Point(x=571, y=48)
orb_prayer = Point(x=565, y=119)
orb_spec = Point(x=597, y=178)

# --- Control Panel ---
h1 = 213  # top row height
h2 = 510  # bottom row height
cp_combat = Point(x=545, y=h1)
cp_inventory = Point(x=646, y=h1)
cp_equipment = Point(x=678, y=h1)
cp_prayer = Point(x=713, y=h1)
cp_spellbook = Point(x=744, y=h1)
cp_logout = Point(x=646, y=h2)
cp_settings = Point(x=680, y=h2)


# --- Inventory Slots ---
def get_inventory_slots() -> list:
    '''
    Returns a 2D list of the inventory slots represented as Points.
    Inventory is 7x4.
    '''
    inv = []
    curr_y = 253
    for _ in range(7):
        curr_x = 583  # reset x
        row = []
        for _ in range(4):
            row.append(Point(x=curr_x, y=curr_y))
            curr_x += 42  # x delta
        inv.append(row)
        curr_y += 36  # y delta
    return inv


inventory_slots = get_inventory_slots()

# --- Configure OCR Arguments ---
ap = argparse.ArgumentParser()
ap.add_argument("-l", "--langs", type=str, default="en", help="comma separated list of languages to OCR")
ap.add_argument("-g", "--gpu", type=int, default=-1, help="whether or not GPU should be used")
args = vars(ap.parse_args())


def visit_points():
    '''
    Moves mouse to each defined point of interest.
    TODO: Remove. This is just for testing.
    '''
    pag.moveTo(orb_compass.x, orb_compass.y)
    time.sleep(0.5)
    pag.moveTo(orb_prayer.x, orb_prayer.y)
    time.sleep(0.5)
    pag.moveTo(orb_spec.x, orb_spec.y)
    time.sleep(0.5)
    pag.moveTo(cp_combat.x, cp_combat.y)
    time.sleep(0.5)
    pag.moveTo(cp_inventory.x, cp_inventory.y)
    time.sleep(0.5)
    pag.moveTo(cp_equipment.x, cp_equipment.y)
    time.sleep(0.5)
    pag.moveTo(cp_prayer.x, cp_prayer.y)
    time.sleep(0.5)
    pag.moveTo(cp_spellbook.x, cp_spellbook.y)
    time.sleep(0.5)
    pag.moveTo(cp_logout.x, cp_logout.y)
    time.sleep(0.5)
    pag.moveTo(cp_settings.x, cp_settings.y)
    time.sleep(0.5)
    for row in inventory_slots:
        for slot in row:
            pag.moveTo(slot.x, slot.y)
            time.sleep(0.5)
    pag.moveTo(inventory_slots[2][1].x, inventory_slots[2][1].y)


def capture_screen(rect: Rectangle):
    '''
    Captures a given Rectangle and saves it to a file.
    Parameters:
        x: The distance in pixels from the left side of the screen.
        y: The distance in pixels from the top of the screen.
    Returns:
        The path to the saved image.
    '''
    im = ImageGrab.grab(bbox=(rect.start[0], rect.start[1], rect.end[0], rect.end[1]))
    path = f"{PATH}/screenshot.png"
    im.save(path)
    return path


# --- Image Search ---
def search_img_in_rect(img_path: str, rect: Rectangle, conf: float = 0.8):
    '''
    Searches for an image in a rectangle.
    Parameters:
        rect: The rectangle to search in.
        img_path: The path to the image to search for.
    Returns:
        The coordinates of the image if found, otherwise None.
    '''
    im = region_grabber((rect.start[0], rect.start[1], rect.end[0], rect.end[1]))
    pos = imagesearcharea(img_path, rect.start[0], rect.start[1], rect.end[0], rect.end[1], conf, im)
    if pos == [-1, -1]:
        return None
    return pos


# --- OCR ---
def search_text_in_rect(rect: Rectangle, expected: list, blacklist: list = None,) -> bool:
    '''
    Searches for text in a Rectangle.
    Parameters:
        rect: The rectangle to search in.
        expected: List of strings that are expected within the rectangle area.
        blacklist: List of strings that, if found, will cause the function to return False.
    Returns:
        False if ANY blacklist words are found, else True if ANY expected text exists,
        and None if the text is irrelevant.
    '''
    # Screenshot the rectangle
    path = capture_screen(rect)
    # Load the image
    image = cv2.imread(path)

    # OCR the input image using EasyOCR
    print("[INFO] OCR'ing input image...")
    langs = args["langs"].split(",")
    reader = Reader(langs, gpu=args["gpu"] > 0)

    res = reader.readtext(image)

    # Loop through results
    word_found = False
    for (_, text, _) in res:
        if text is None or text == "":
            return None
        text = text.lower()
        print(f"OCR Result: {text}")
        # If any strings in blacklist are found in text, return false
        if blacklist is not None:
            for word in blacklist:
                print(f"Checking blacklist word: {word.lower()}")
                if word.lower() in text:
                    print(f"Blacklist word found: {word.lower()}")
                    return False
        for word in expected:
            print(f"Checking expected word: {word.lower()}")
            if word.lower() in text:
                print(f"Expected word found: {word.lower()}")
                word_found = True
    if word_found:
        return True
    return None


def setup_client_alora():
    '''
    Configures the client window of Alora.
    Experimental.
    '''
    # Move window to top left corner
    win = pygetwindow.getWindowsWithTitle('Alora')[0]
    win.moveTo(window.start[0], window.start[1])

    # Resize to desired size
    win.size = (window.end[0], window.end[1])

    # Search for settings button and click it
    time.sleep(1)
    pos = search_img_in_rect(f"{IMAGES_PATH}/cp_settings_icon.png", window)
    print(pos)
    if pos is None:
        print("it's none")
    else:
        pag.click(pos[0]+5, pos[1]+5)


setup_client_alora()

# Returns true if player is fishing, false if they are not
res = search_text_in_rect(activity_rect, ["fishing"], ["NOT"])
print(res)