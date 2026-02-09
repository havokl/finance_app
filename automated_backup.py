# automated_backup.py
import shutil
import os
import datetime

# --- CONFIGURATION ---
PROJECT_DIR = "/users/haava/OneDrive/Skrivebord\finance_app" 
DB_FILE = os.path.join(PROJECT_DIR, "finance.db")
BACKUP_DIR = os.path.join(PROJECT_DIR, "backups")
MAX_BACKUPS = 10  # Keep only the last 10 weeks

def perform_backup():
    # 1. Ensure backup directory exists
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
        print(f"Created backup directory: {BACKUP_DIR}")

    # 2. Create filename with timestamp (e.g., finance_backup_2026-02-09.db)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d")
    backup_filename = f"finance_backup_{timestamp}.db"
    backup_path = os.path.join(BACKUP_DIR, backup_filename)

    # 3. Copy the file
    try:
        shutil.copy2(DB_FILE, backup_path)
        print(f"✅ Backup successful: {backup_filename}")
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        return

    # 4. Cleanup old backups (Retention Policy)
    # Get list of backups sorted by time (oldest first)
    files = sorted(
        [os.path.join(BACKUP_DIR, f) for f in os.listdir(BACKUP_DIR) if f.endswith(".db")],
        key=os.path.getmtime
    )

    # If we have more than MAX_BACKUPS, delete the oldest ones
    if len(files) > MAX_BACKUPS:
        files_to_delete = files[:len(files) - MAX_BACKUPS]
        for f in files_to_delete:
            os.remove(f)
            print(f"🗑️ Deleted old backup: {os.path.basename(f)}")

if __name__ == "__main__":
    perform_backup()