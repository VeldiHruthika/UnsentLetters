import sqlite3

conn = sqlite3.connect('unsent_letters.db')
c = conn.cursor()

# Create Users table
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password TEXT,
    otp TEXT,
    last_login TEXT
)
''')

# Create Letters table
c.execute('''
CREATE TABLE IF NOT EXISTS letters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_email TEXT,
    letter TEXT,
    reply TEXT,
    title TEXT DEFAULT '',
    mood TEXT DEFAULT '',
    profile_icon TEXT,
    avatar TEXT DEFAULT '',
    open_date TEXT,
    is_time_capsule INTEGER DEFAULT 0,
    burnt INTEGER DEFAULT 0,
    timestamp TEXT,
    image_path TEXT,
    FOREIGN KEY(user_email) REFERENCES users(email)
)
''')

# Create Login History table
DB_PATH = 'unsent_letters.db'
def get_db():
    return sqlite3.connect(DB_PATH)

def setup_login_history_table():
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS login_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

setup_login_history_table()

# Add avatar column to users table (for selected profile avatar)
try:
    c.execute("ALTER TABLE users ADD COLUMN avatar TEXT DEFAULT ''")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e).lower():
        print("⚠️ Column 'avatar' already exists.")
    else:
        raise


# Add reply column to letters table if not already added
try:
    c.execute("ALTER TABLE letters ADD COLUMN reply TEXT")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e).lower():
        print("⚠️ Column 'reply' already exists.")
    else:
        raise
# ✅ Add mood column to letters table if not already added
try:
    c.execute("ALTER TABLE letters ADD COLUMN mood TEXT DEFAULT ''")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e).lower():
        print("⚠️ Column 'mood' already exists.")
    else:
        raise

try:
    c.execute("ALTER TABLE users ADD COLUMN profile_icon TEXT DEFAULT '👤'")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e).lower():
        print("⚠️ Column 'profile_icon' already exists.")



# Add title column to letters table if not already added
try:
    c.execute("ALTER TABLE letters ADD COLUMN title TEXT DEFAULT ''")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e).lower():
        print("⚠️ Column 'title' already exists.")
    else:
        raise

# Create Voice Capsules table
try:
    c.execute('''
        CREATE TABLE IF NOT EXISTS voice_capsules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT,
            title TEXT,
            letter TEXT,
            voice_path TEXT,
            unlock_date TEXT,
            music TEXT,
            created_at TEXT
        )
    ''')
except Exception as e:
    print(f"⚠️ Voice capsule table error: {e}")

# Check the structure of the letters table
c.execute("PRAGMA table_info(letters);")
columns = c.fetchall()
print(columns)




conn.commit()
conn.close()

print("✅ Database and tables created.")
