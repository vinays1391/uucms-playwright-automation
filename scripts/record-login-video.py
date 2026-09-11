import os
from pathlib import Path

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright


load_dotenv()
BASE_URL = os.getenv("UUCMS_BASE_URL", "http://123.63.4.210:5010/")
BROWSER_NAME = os.getenv("UUCMS_BROWSER", "chromium").strip().lower()
VIDEO_DIR = Path("recordings/videos")


with sync_playwright() as playwright:
    VIDEO_DIR.mkdir(parents=True, exist_ok=True)
    browser_type = getattr(playwright, BROWSER_NAME, None)
    if browser_type is None:
        raise ValueError("UUCMS_BROWSER must be chromium, firefox, or webkit")
    browser = browser_type.launch(headless=False)
    context = browser.new_context(
        record_video_dir=str(VIDEO_DIR),
        record_video_size={"width": 1280, "height": 720},
    )
    page = context.new_page()
    page.goto(BASE_URL, wait_until="domcontentloaded")
    print("Complete the login flow in the browser window.")
    input("Press Enter here when you have finished recording: ")
    video = page.video
    context.close()
    browser.close()

if video is not None:
    print(f"Video saved to: {video.path()}")
