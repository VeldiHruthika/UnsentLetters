import sqlite3

conn = sqlite3.connect('unsent_letters.db')
c = conn.cursor()

# Fix 1: Add open_date column to letters table
try:
    c.execute("ALTER TABLE letters ADD COLUMN open_date TEXT")
    print("✅ open_date column added to letters table")
except sqlite3.OperationalError as e:
    if "duplicate column" in str(e).lower():
        print("⚠️ open_date already exists in letters table")
    else:
        raise

# Fix 2: Add is_time_capsule column to letters table
try:
    c.execute("ALTER TABLE letters ADD COLUMN is_time_capsule INTEGER DEFAULT 0")
    print("✅ is_time_capsule column added to letters table")
except sqlite3.OperationalError as e:
    if "duplicate column" in str(e).lower():
        print("⚠️ is_time_capsule already exists in letters table")
    else:
        raise


# Optionally: Add open_date column to voice_capsules table (if applicable)
try:
    c.execute("ALTER TABLE voice_capsules ADD COLUMN open_date TEXT")
    print("✅ open_date column added to voice_capsules table")
except sqlite3.OperationalError as e:
    if "duplicate column" in str(e).lower():
        print("⚠️ open_date already exists in voice_capsules table")
    else:
        raise

# Optionally: Add is_time_capsule column to voice_capsules table (if applicable)
try:
    c.execute("ALTER TABLE voice_capsules ADD COLUMN is_time_capsule INTEGER DEFAULT 0")
    print("✅ is_time_capsule column added to voice_capsules table")
except sqlite3.OperationalError as e:
    if "duplicate column" in str(e).lower():
        print("⚠️ is_time_capsule already exists in voice_capsules table")
    else:
        raise


# Fix: Add deleted column to voice_capsules table
try:
    c.execute("ALTER TABLE voice_capsules ADD COLUMN deleted INTEGER DEFAULT 0")
    print("✅ deleted column added to voice_capsules table")
except sqlite3.OperationalError as e:
    if "duplicate column" in str(e).lower():
        print("⚠️ deleted already exists in voice_capsules table")
    else:
        raise

# Fix: Update open_date columns in both letters and voice_capsules to ensure consistency
c.execute('''
    UPDATE letters
    SET open_date = REPLACE(open_date, 'T', ' ')
    WHERE open_date LIKE '%T%'
''')

c.execute('''
    UPDATE voice_capsules
    SET open_date = REPLACE(open_date, 'T', ' ')
    WHERE open_date LIKE '%T%'
''')



# Check the table structure BEFORE closing the connection
c.execute("PRAGMA table_info(voice_capsules);")
columns = c.fetchall()

# Print out the columns in the table
for column in columns:
    print(column)

# Commit and close the connection
conn.commit()
conn.close()

print("🎉 Database updated successfully!")
