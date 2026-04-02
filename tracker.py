import csv
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

from agent import generate_message
from linkedin import send_message_wrapper

load_dotenv()

TRACKER_FILE = "tracker.csv"
CONNECTIONS_FILE = "connections.csv"

DAILY_LIMIT = int(os.getenv("DAILY_MESSAGE_LIMIT", 20))
FOLLOWUP_LIMIT = int(os.getenv("FOLLOWUP_LIMIT", 10))

HEADERS = [
    "ID", "Name", "Company", "Role", "Profile Link",
    "Priority", "Message", "Status",
    "Last Contact", "Follow-up Date",
    "Response", "Notes"
]


# ----------------------------
# INIT TRACKER
# ----------------------------
def init_tracker():
    if not os.path.exists(TRACKER_FILE):
        with open(TRACKER_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(HEADERS)


# ----------------------------
# LOAD EXISTING DATA
# ----------------------------
def load_tracker_data():
    existing_profiles = set()
    sent_today = 0
    followups_today = 0

    today = datetime.now().strftime("%Y-%m-%d")

    if os.path.exists(TRACKER_FILE):
        with open(TRACKER_FILE, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for row in reader:
                existing_profiles.add(row["Profile Link"])

                if row["Last Contact"] == today:
                    if row["Status"] == "Sent":
                        sent_today += 1
                    elif row["Status"] == "Follow-up Sent":
                        followups_today += 1

    return existing_profiles, sent_today, followups_today


# ----------------------------
# APPEND ROW
# ----------------------------
def append_tracker(row):
    with open(TRACKER_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(row)


# ----------------------------
# MAIN PROCESS
# ----------------------------
def process_connections():
    init_tracker()

    existing_profiles, sent_today, followups_today = load_tracker_data()

    print(f"📊 Sent today: {sent_today}/{DAILY_LIMIT}")
    print(f"🔁 Follow-ups today: {followups_today}/{FOLLOWUP_LIMIT}")

    if sent_today >= DAILY_LIMIT:
        print("🚫 Daily message limit reached. Exiting.")
        return

    with open(CONNECTIONS_FILE, "r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))

        # ✅ ADD PRIORITY SORT HERE
        priority_order = {"High": 1, "Medium": 2, "Low": 3}
        reader.sort(key=lambda x: priority_order.get(x.get("Priority", "Medium"), 2))

        for i, lead in enumerate(reader, start=1):

            if sent_today >= DAILY_LIMIT:
                print("🚫 Limit reached while processing.")
                break

            profile = lead["Profile Link"]

            # Skip already contacted
            if profile in existing_profiles:
                continue

            name = lead["Name"]
            company = lead["Company"]
            role = lead["Role"]
            priority = lead.get("Priority", "Medium")

            print(f"➡️ Processing: {name} | {company}")

            # Generate AI message
            message = generate_message(name, role, company)

            # Send message
            status = send_message_wrapper(profile, message)

            now = datetime.now()
            follow_up_date = now + timedelta(days=3)

            append_tracker([
                i,
                name,
                company,
                role,
                profile,
                priority,
                message,
                status,
                now.strftime("%Y-%m-%d"),
                follow_up_date.strftime("%Y-%m-%d"),
                "",
                ""
            ])

            if status == "Sent":
                sent_today += 1
                print(f"✅ Sent count: {sent_today}/{DAILY_LIMIT}")

    print("✅ Processing complete.")


# ----------------------------
# RUN
# ----------------------------
if __name__ == "__main__":
    process_connections()