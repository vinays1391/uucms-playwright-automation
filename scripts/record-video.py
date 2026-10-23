import argparse
import os
from pathlib import Path

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright


load_dotenv()
VIDEO_DIR = Path("recordings/videos")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Open the browser, record the session, and save the video to recordings/videos."
    )
    parser.add_argument(
        "--url",
        default=os.getenv("UUCMS_BASE_URL", "http://123.63.4.210:5010/"),
        help="URL to open in the browser (default: UUCMS_BASE_URL from .env)",
    )
    return parser.parse_args()


args = parse_args()
BROWSER_NAME = os.getenv("UUCMS_BROWSER", "chromium").strip().lower()


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
    page.goto(args.url, wait_until="commit", timeout=90_000)
    print("Complete the workflow in the browser window.")
    input("Press Enter here when you have finished recording: ")
    video = page.video
    context.close()
    browser.close()

if video is not None:
    print(f"Video saved to: {video.path()}")
