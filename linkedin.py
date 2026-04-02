import os
import asyncio
import random
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

LINKEDIN_EMAIL = os.getenv("EMAIL")
LINKEDIN_PASSWORD = os.getenv("EMAIL_PASSWORD")
RESUME_PATH = "Swapnil_Pharate_resume.pdf"   # <-- your resume

# ----------------------------
# Human behavior utils
# ----------------------------

def random_delay(min_s=2, max_s=5):
    return random.uniform(min_s, max_s) * 1000


async def human_scroll(page):
    await page.mouse.wheel(0, random.randint(300, 800))
    await page.wait_for_timeout(random_delay(1, 3))
    await page.mouse.wheel(0, -random.randint(100, 300))


async def human_mouse_move(page):
    await page.mouse.move(
        random.randint(100, 500),
        random.randint(100, 500),
        steps=random.randint(5, 20)
    )


async def human_typing(page, text):
    for char in text:
        await page.keyboard.type(char, delay=random.randint(50, 120))


# ----------------------------
# Login
# ----------------------------

async def login(page):
    await page.goto("https://www.linkedin.com/login")
    await page.wait_for_timeout(random_delay())

    await page.fill("#username", LINKEDIN_EMAIL)
    await page.fill("#password", LINKEDIN_PASSWORD)

    await page.wait_for_timeout(random_delay())
    await page.click("button[type='submit']")
    await page.wait_for_timeout(5000)


# ----------------------------
# Attach Resume
# ----------------------------

async def attach_resume(page):
    try:
        # Click attachment icon (paperclip)
        attach_button = page.locator("input[type='file']")
        await attach_button.set_input_files(RESUME_PATH)

        await page.wait_for_timeout(random_delay(2, 4))
        print("📎 Resume attached")

    except Exception as e:
        print("⚠️ Resume attach failed:", str(e))


# ----------------------------
# Send Message
# ----------------------------

async def send_message(page, profile_url, message):
    await page.goto(profile_url)
    await page.wait_for_timeout(random_delay(3, 6))

    await human_scroll(page)
    await human_mouse_move(page)

    # Click Message button
    try:
        msg_btn = page.locator("button:has-text('Message')")
        await msg_btn.hover()
        await page.wait_for_timeout(random_delay(1, 2))
        await msg_btn.click()
    except:
        print("❌ Message button not found")
        return "Failed"

    await page.wait_for_timeout(random_delay(2, 4))

    # Type message
    await human_typing(page, message)

    await page.wait_for_timeout(random_delay(1, 2))

    # ✅ Attach Resume HERE
    await attach_resume(page)

    await page.wait_for_timeout(random_delay(1, 2))

    # Send message
    await page.keyboard.press("Enter")

    print(f"✅ Message sent to {profile_url}")
    return "Sent"


# ----------------------------
# Wrapper (IMPORTANT)
# ----------------------------

async def send_message_async(profile, message):
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,     # ⚠️ keep False for safety
            slow_mo=50
        )

        context = await browser.new_context()
        page = await context.new_page()

        await login(page)

        try:
            result = await send_message(page, profile, message)
        except Exception as e:
            result = f"Failed: {str(e)}"

        await browser.close()
        return result


def send_message_wrapper(profile, message):
    return asyncio.run(send_message_async(profile, message))