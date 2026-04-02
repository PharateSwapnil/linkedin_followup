import os
import csv
import asyncio
from dotenv import load_dotenv
from playwright.async_api import async_playwright
from datetime import datetime

from agent import classify_reply  # new function

load_dotenv()

TRACKER_FILE = "tracker.csv"


async def login(page):
    await page.goto("https://www.linkedin.com/login")
    await page.fill("#username", os.getenv("EMAIL"))
    await page.fill("#password", os.getenv("EMAIL_PASSWORD"))
    await page.click("button[type='submit']")
    await page.wait_for_timeout(5000)


async def process_inbox():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        await login(page)

        await page.goto("https://www.linkedin.com/messaging/")
        await page.wait_for_timeout(5000)

        # Load tracker
        with open(TRACKER_FILE, "r", encoding="utf-8") as f:
            reader = list(csv.DictReader(f))
            fieldnames = reader[0].keys()

        updated_rows = []

        for row in reader:
            profile = row["Profile Link"]
            status = row["Status"]

            # Skip if already replied
            if status == "Replied":
                updated_rows.append(row)
                continue

            try:
                # Open chat
                await page.goto(profile)
                await page.wait_for_timeout(3000)

                msg_btn = page.locator("button:has-text('Message')")
                await msg_btn.click()
                await page.wait_for_timeout(3000)

                # Get last message
                messages = page.locator(".msg-s-message-list__event")
                count = await messages.count()

                if count == 0:
                    updated_rows.append(row)
                    continue

                last_msg = messages.nth(count - 1)
                text = await last_msg.inner_text()

                # Detect if recruiter replied
                if "You sent" not in text:

                    print(f"📩 Reply detected from {row['Name']}")

                    result = classify_reply(text)

                    row["Response"] = result["response"]
                    row["Notes"] = result["notes"]
                    row["Priority"] = result["priority"]
                    row["Status"] = "Replied"
                    row["Last Contact"] = datetime.now().strftime("%Y-%m-%d")

                else:
                    # Check if YOU didn't reply after recruiter
                    if row["Status"] == "Follow-up Sent":
                        row["Notes"] = "⚠️ Awaiting your reply"

                updated_rows.append(row)

            except Exception as e:
                print("Error:", e)
                updated_rows.append(row)

        # Save
        with open(TRACKER_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(updated_rows)

        await browser.close()


if __name__ == "__main__":
    asyncio.run(process_inbox())