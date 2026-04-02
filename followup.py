import csv
import os
from datetime import datetime
from dotenv import load_dotenv

from linkedin import send_message_wrapper

load_dotenv()

TRACKER_FILE = "tracker.csv"
FOLLOWUP_LIMIT = int(os.getenv("FOLLOWUP_LIMIT", 10))


# ----------------------------
# MAIN FOLLOW-UP PROCESS
# ----------------------------
def process_followups():
    if not os.path.exists(TRACKER_FILE):
        print("❌ tracker.csv not found. Run tracker.py first.")
        return

    updated_rows = []
    followups_sent = 0
    today = datetime.now().strftime("%Y-%m-%d")

    print(f"🔁 Follow-up limit: {FOLLOWUP_LIMIT}")

    with open(TRACKER_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames

        for row in reader:

            # Stop if limit reached
            if followups_sent >= FOLLOWUP_LIMIT:
                updated_rows.append(row)
                continue

            status = row["Status"]
            follow_up_date = row["Follow-up Date"]
            last_contact = row["Last Contact"]
            response = row["Response"]

            # ----------------------------
            # SKIP CONDITIONS
            # ----------------------------

            # Skip if not initial message sent
            if status != "Sent":
                updated_rows.append(row)
                continue

            # Skip if recruiter replied
            if response.strip():
                updated_rows.append(row)
                continue

            # Skip if no follow-up date
            if not follow_up_date:
                updated_rows.append(row)
                continue

            # Skip if follow-up date not reached
            if datetime.now() < datetime.strptime(follow_up_date, "%Y-%m-%d"):
                updated_rows.append(row)
                continue

            # Skip if already contacted today
            if last_contact == today:
                updated_rows.append(row)
                continue

            # ----------------------------
            # SEND FOLLOW-UP
            # ----------------------------

            name = row["Name"]
            profile = row["Profile Link"]

            followup_msg = f"Hi {name}, just wanted to follow up on my previous message. Would love to connect!"

            print(f"➡️ Sending follow-up to {name}")

            result = send_message_wrapper(profile, followup_msg)

            # ----------------------------
            # UPDATE ROW
            # ----------------------------

            if result == "Sent":
                row["Status"] = "Follow-up Sent"
                row["Last Contact"] = today
                row["Notes"] = "Follow-up sent"
                followups_sent += 1

                print(f"✅ Follow-up sent ({followups_sent}/{FOLLOWUP_LIMIT})")
            else:
                print(f"❌ Failed for {name}: {result}")

            updated_rows.append(row)

    # ----------------------------
    # SAVE UPDATED TRACKER
    # ----------------------------
    with open(TRACKER_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(updated_rows)

    print("✅ Follow-up process complete.")


# ----------------------------
# RUN
# ----------------------------
if __name__ == "__main__":
    process_followups()