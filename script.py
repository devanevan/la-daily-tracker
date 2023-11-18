import pyautogui
from PIL import Image
import pytesseract
import time
import redis
from urllib.parse import urlparse
from skimage.metrics import structural_similarity as ssim
import numpy as np
from dotenv import load_dotenv
load_dotenv()
import os

def checkForGameMenu(x, y, width, height, tolerance=4, target_rgb=(53, 58, 63)):
    screenshot = pyautogui.screenshot(region=(x, y, width, height))
    saved_image_path = 'game_menu.png'
    try:
        # Open the saved image
        with Image.open(saved_image_path) as saved_img:
            # Resize the screenshot to match the saved image's dimensions
            screenshot = screenshot.resize(saved_img.size)

            # Convert images to grayscale for SSIM comparison
            saved_gray = saved_img.convert('L')
            screenshot_gray = screenshot.convert('L')

            # Convert grayscale images to NumPy arrays
            saved_gray_array = np.array(saved_gray)
            screenshot_gray_array = np.array(screenshot_gray)

            # Compute the Mean Squared Error (MSE)
            mse = np.sum((saved_gray_array - screenshot_gray_array) ** 2) / float(saved_gray_array.size)

            # Normalize MSE to a similarity score between 0 (completely different) and 1 (identical)
            similarity_score = 1 / (1 + mse)

            return similarity_score
    except Exception as e:
        print(f"Error: {e}")
        return 0
def capture_and_parse_text(x, y, width, height, configT="--psm 6"):
    try:
        # Capture the screenshot
        screenshot = pyautogui.screenshot(region=(x, y, width, height))

        # Perform OCR on the screenshot to extract text
        extracted_text = pytesseract.image_to_string(screenshot, config=configT)
        return extracted_text
    except Exception as e:
        print(f"Error extracting text: {e}")

def extract_letters(input_string):
    # Remove spaces and new lines
    cleaned_string = input_string.replace(" ", "").replace("\n", "")

    # Extract only letters
    letters_only = ''.join(char for char in cleaned_string if char.isalpha())

    return letters_only

x_position = 2294
y_position = 439
region_width = 480
region_height = 432

daily_task_width = 78
daily_task_height = 25

redis_url = os.getenv("REDIS_URL")

url_parts = urlparse(redis_url)

redis_client = redis.StrictRedis(
    host=url_parts.hostname,
    port=url_parts.port,
    password=url_parts.password,
    decode_responses=True,  # Decode responses to UTF-8
)

while True:
    # check for grey box for game menu
    if (checkForGameMenu(2781, 547, 13, 34) != 1.0):
        time.sleep(0.5)
        continue
    rawNameText = capture_and_parse_text(2481, 438, 145, 29)
    rawEndgameText = capture_and_parse_text(2652, 590, daily_task_width, daily_task_height)
    amountOfEndgameRaidsLeft = ''
    if (rawEndgameText):
        amountOfEndgameRaidsLeft = rawEndgameText[0]
    if (amountOfEndgameRaidsLeft in ['1','2','3']):
        name = extract_letters(rawNameText)
        value = redis_client.hget('endgame_raid_log', name)
        if (value == None):
            redis_client.hset('endgame_raid_log', name, amountOfEndgameRaidsLeft)
            print('Added:', name, ':', amountOfEndgameRaidsLeft)
        elif (value != amountOfEndgameRaidsLeft):
            print('Updated:', name, ':', amountOfEndgameRaidsLeft)
        print('Character', name, 'has', amountOfEndgameRaidsLeft, 'end game raids left.')
    else:
        print('Parse incorrect.')
    time.sleep(0.5)

# capture_and_parse_text(2652, 706, daily_task_width, daily_task_height, 'una.txt')
# capture_and_parse_text(2652, 761, daily_task_width, daily_task_height, 'guardian.txt')
# capture_and_parse_text(2652, 821, daily_task_width, daily_task_height, 'chaos.txt')
