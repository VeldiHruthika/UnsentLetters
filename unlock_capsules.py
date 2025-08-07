import sqlite3
from datetime import datetime

# Database connection
DB_PATH = 'unsent_letters.db'

def unlock_time_capsules():
    # Get today's date
    today = datetime.now().strftime('%Y-%m-%d')

    # Connect to the database
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Update the database to unlock the capsules where open_date is today or earlier
    c.execute('''UPDATE letters 
                 SET is_time_capsule = 0 
                 WHERE open_date <= ? AND is_time_capsule = 1''', (today,))
    conn.commit()
    conn.close()

    print(f"Unlocked time capsules for {today}.")

if __name__ == "__main__":
    unlock_time_capsules()
