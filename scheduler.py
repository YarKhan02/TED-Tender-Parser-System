import schedule
import time
import subprocess

def run_tender_script():
    subprocess.run(["python", "src/tender.py"])

# Schedule: run every day at 9 AM
schedule.every().day.at("09:00").do(run_tender_script)

print("Scheduler started. Waiting for scheduled time...")

while True:
    schedule.run_pending()
    time.sleep(60)