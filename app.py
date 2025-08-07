from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_from_directory, flash
from flask_mail import Mail, Message
from random import randint
from datetime import datetime
import sqlite3
import os
from werkzeug.utils import secure_filename

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
VOICE_UPLOAD_DIR = os.path.join(os.getcwd(), 'voice_notes')
if not os.path.exists(VOICE_UPLOAD_DIR):
    os.makedirs(VOICE_UPLOAD_DIR)


app = Flask(__name__, template_folder='frontend', static_folder='frontend')
app.secret_key = 'ijmedfpijbanyxpt'

# Manually serve avatars from the assets folder
@app.route('/assets/avatars/<filename>')
def serve_avatar(filename):
    return send_from_directory(os.path.join(app.root_path, 'assets/avatars'), filename)



# === Flask Mail Config ===
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'hruthika.veldi123@gmail.com'
app.config['MAIL_PASSWORD'] = 'ijmedfpijbanyxpt'
app.config['MAIL_DEFAULT_SENDER'] = 'hruthika.veldi123@gmail.com'
mail = Mail(app)

DB_PATH = 'unsent_letters.db'

@app.route('/assets/<path:filename>')
def custom_static(filename):
    return send_from_directory('assets', filename)

def get_db():
    return sqlite3.connect(DB_PATH)

def send_otp(email, otp, reset=False):
    try:
        # Adjust the subject and body for password reset or registration
        subject = "Your OTP Code - Unsent Letters"
        
        if reset:
            body = f"""
            <html>
            <head>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        color: #333;
                    }}
                    .container {{
                        max-width: 600px;
                        margin: 0 auto;
                        background-color: #f7f7f7;
                        padding: 20px;
                        border-radius: 8px;
                    }}
                    .header {{
                        text-align: center;
                        font-size: 24px;
                        color: #2d2d2d;
                        margin-bottom: 20px;
                    }}
                    .otp {{
                        font-size: 36px;
                        font-weight: bold;
                        color: #4CAF50;
                        text-align: center;
                        margin: 20px 0;
                    }}
                    .footer {{
                        font-size: 12px;
                        color: #aaa;
                        text-align: center;
                        margin-top: 20px;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        Unsent Letters - Password Reset
                    </div>
                    <p>Hi there,</p>
                    <p>We received a request to reset your password. Please use the OTP below to proceed:</p>
                    <div class="otp">{otp}</div>
                    <p>This OTP is valid for the next 10 minutes. If you did not request this, please ignore this email.</p>
                    <div class="footer">
                        &copy; {datetime.now().year} Unsent Letters. All rights reserved.<br>
                        <a href="https://unsentletters.onrender.com/">Visit our website</a> for more information.
                    </div>
                </div>
            </body>
            </html>
            """
        else:
            # Existing registration email content
            body = f"""
            <html>
            <head>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        color: #333;
                    }}
                    .container {{
                        max-width: 600px;
                        margin: 0 auto;
                        background-color: #f7f7f7;
                        padding: 20px;
                        border-radius: 8px;
                    }}
                    .header {{
                        text-align: center;
                        font-size: 24px;
                        color: #2d2d2d;
                        margin-bottom: 20px;
                    }}
                    .otp {{
                        font-size: 36px;
                        font-weight: bold;
                        color: #4CAF50;
                        text-align: center;
                        margin: 20px 0;
                    }}
                    .footer {{
                        font-size: 12px;
                        color: #aaa;
                        text-align: center;
                        margin-top: 20px;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        Unsent Letters
                    </div>
                    <p>Hi there,</p>
                    <p>Thank you for registering with Unsent Letters. Please use the OTP below to verify your email address:</p>
                    <div class="otp">{otp}</div>
                    <p>This OTP is valid for the next 10 minutes. If you did not request this, please ignore this email.</p>
                    <div class="footer">
                        &copy; {datetime.now().year} Unsent Letters. All rights reserved.<br>
                        <a href="https://unsentletters.onrender.com/">Visit our website</a> for more information.
                    </div>
                </div>
            </body>
            </html>
            """
        
        # Sending email using Flask-Mail
        msg = Message(subject, sender=app.config['MAIL_USERNAME'], recipients=[email])
        msg.html = body  # Use the HTML content instead of plain text
        mail.send(msg)
    except Exception as e:
        print(f"❌ Failed to send OTP: {e}")


# ========== REGISTER ==========
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        otp = str(randint(1000, 9999))
        now = datetime.now().strftime("%Y-%m-%d %H:%M")

        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT password FROM users WHERE email = ?", (email,))
        result = c.fetchone()

        if result and result[0] is not None:
            conn.close()
            flash("⚠️ Account already exists. Please log in instead.")
            return redirect(url_for('login'))

        if result:
            c.execute("UPDATE users SET otp = ?, last_login = ? WHERE email = ?", (otp, now, email))
        else:
            c.execute("INSERT INTO users (email, otp, last_login) VALUES (?, ?, ?)", (email, otp, now))

        conn.commit()
        conn.close()

        # Store password temporarily in session until OTP is verified
        session['email'] = email
        session['temp_password'] = password

        send_otp(email, otp)
        return redirect(url_for('verify_otp'))

    return render_template('register.html')

# ========== LOGIN ==========
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT password FROM users WHERE email = ?", (email,))
        result = c.fetchone()

        if result and result[0] == password:
            # If login is successful, set the session
            session['email'] = email
            # Save login to history table
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            c.execute("INSERT INTO login_history (email, timestamp) VALUES (?, ?)", (email, timestamp))
            conn.commit()
            conn.close()
            return redirect(url_for('index_redirect', show_popup=True))  # Redirect to index with popup flag

        else:
            # If login is invalid, clear the session to prevent auto login with existing email
            session.clear()
            conn.close()
            error = "❌ Invalid login. Try again."  # Show error message
            return render_template('login.html', error=error, email=email)  # Keep entered email in the form

    # Prefill email if provided (for quick login attempts)
    prefill_email = request.args.get('email', '')  
    return render_template('login.html', email=prefill_email)


# ========== VERIFY OTP ==========
@app.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    if request.method == 'POST':
        otp_entered = request.form['otp']
        email = session.get('email')
        temp_password = session.get('temp_password')

        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT otp, password FROM users WHERE email = ?", (email,))
        result = c.fetchone()

        if not result:
            conn.close()
            return "⚠️ This email is not registered."

        otp_stored, password_stored = result

        if password_stored is not None:
            conn.close()
            return "⚠️ Account already verified. Please log in."

        if otp_entered.strip() == otp_stored.strip():
            c.execute("UPDATE users SET password = ? WHERE email = ?", (temp_password, email))
            conn.commit()
            conn.close()

            session.pop('temp_password', None)
            return redirect(url_for('static', filename='index.html'))
        else:
            conn.close()
            return "Invalid OTP. Please try again."

    return render_template('verify_otp.html')



# ========== LETTER ROUTES ==========
@app.route('/create-letter', methods=['POST'])
def create_letter():
    email = session.get('email')
    if not email:
        return 'Unauthorized', 403

    letter = request.form['letter']
    reply = request.form.get('reply', '')  # Get AI reply
    title = request.form.get('title', '')  # ✅ New
    mood = request.form.get('mood', '')  # ✅ THIS WAS MISSING

    profile_icon = request.form.get('profile_icon', '👤')
    avatar = request.form.get('avatar', '')
    open_date = request.form.get('open_date')
    is_time_capsule = int(request.form.get('isTimeCapsule', 0))
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    conn = get_db()
    c = conn.cursor()
    c.execute('''
    INSERT INTO letters (user_email, letter, reply, title,mood, profile_icon, avatar, burnt, timestamp, open_date, is_time_capsule)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', (email, letter, reply, title,mood, profile_icon, avatar, 0, timestamp, open_date, is_time_capsule))

    conn.commit()
    conn.close()
    return '', 204

@app.route('/get-user')
def get_user():
    email = session.get('email')
    history = []

    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT avatar FROM users WHERE email = ?", (email,))
    row = c.fetchone()
    avatar = row[0] if row else None  # If no avatar, None is returned

    # If no avatar is selected, fallback to the default one
    if not avatar:
        avatar = 'default_avatar.png'

    c.execute("SELECT DISTINCT email FROM login_history ORDER BY id DESC")
    history = [row[0] for row in c.fetchall()]
    conn.close()

    return jsonify({
        'email': email if email else 'Not logged in',
        'history': history,
        'avatar': avatar  # Send the avatar path to the frontend
    })
@app.route('/burnt-letters')
def burnt_letters():
    email = session.get('email')
    if not email:
        return jsonify([])

    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT id, letter, timestamp FROM letters WHERE user_email = ? AND burnt = 1', (email,))
    rows = c.fetchall()
    conn.close()

    return jsonify([
        {'id': r[0], 'letter': r[1], 'timestamp': r[2]}
        for r in rows
    ])

@app.route('/burn-letter/<int:letter_id>', methods=['POST'])
def burn_letter(letter_id):
    email = session.get('email')
    if not email:
        return 'Unauthorized', 403

    conn = get_db()
    c = conn.cursor()
    c.execute('UPDATE letters SET burnt = 1 WHERE id = ? AND user_email = ?', (letter_id, email))
    conn.commit()
    conn.close()
    return '', 204

import os

@app.route('/delete-voice-capsule/<int:voice_id>', methods=['POST'])
def delete_voice_capsule(voice_id):
    email = session.get('email')
    if not email:
        return 'Unauthorized', 403

    conn = get_db()
    c = conn.cursor()

    # Check if the voice capsule exists for this user
    c.execute('SELECT voice_path FROM voice_capsules WHERE id = ? AND user_email = ?', (voice_id, email))
    voice_data = c.fetchone()

    if not voice_data:
        conn.close()
        return 'Voice Capsule not found or you do not have permission to delete it', 404

    # Get the file path to delete
    voice_file_path = os.path.join(app.config['UPLOAD_FOLDER'], voice_data[0])

    # Delete the voice capsule record from the database
    c.execute('DELETE FROM voice_capsules WHERE id = ? AND user_email = ?', (voice_id, email))
    conn.commit()

    # Delete the actual voice file from the server
    if os.path.exists(voice_file_path):
        try:
            os.remove(voice_file_path)  # Delete the file from the server
            print(f"Voice capsule deleted: {voice_file_path}")  # Debugging
        except Exception as e:
            print(f"Error while deleting voice capsule file: {e}")
    else:
        print(f"File not found: {voice_file_path}")  # Debugging for missing file

    conn.close()
    return '', 204  # Successful deletion, no content response



# ========== PROFILE & SESSION ==========
@app.route('/profile')
def profile():
    email = session.get('email')
    if not email:
        return redirect(url_for('login'))  # If not logged in, redirect to login

    conn = get_db()
    c = conn.cursor()

    # Fetch the avatar for the logged-in user
    c.execute("SELECT avatar FROM users WHERE email = ?", (email,))
    avatar = c.fetchone()

    # Prepare the data dictionary to pass to the template
    data = {
        'email': email,
        'avatar': avatar[0] if avatar else None  # None if avatar doesn't exist
    }

    conn.close()

    return render_template('profile.html', data=data)  # Pass the 'data' to the template


@app.route('/')
def intro():
    return render_template('intro.html')

@app.route('/index')
def index_redirect():
    if 'email' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('static', filename='index.html'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

from flask_mail import Message

@app.route('/delete-account', methods=['POST'])
def delete_account():
    email = session.get('email')
    if not email:
        return "Not logged in."

    # Connect to the database and delete user info
    conn = get_db()
    c = conn.cursor()
    
    # Delete user data from the relevant tables
    c.execute("DELETE FROM users WHERE email = ?", (email,))
    c.execute("DELETE FROM letters WHERE user_email = ?", (email,))
    c.execute("DELETE FROM login_history WHERE email = ?", (email,))
    c.execute("DELETE FROM voice_capsules WHERE user_email = ?", (email,))
    conn.commit()
    conn.close()

    # Send a confirmation email about account deletion
    send_account_deletion_email(email)

    # Clear session to log the user out
    session.clear()

    # Pass None for data when the account is deleted
    return render_template('profile.html', message="✅ Your account has been deleted. You will receive a confirmation email.", data=None)

# Send the account deletion confirmation email
def send_account_deletion_email(email):
    try:
        # Create the email subject and body for account deletion
        subject = "Account Deletion Confirmation - Unsent Letters"
        body = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background-color: #f7f7f7;
                    padding: 20px;
                    border-radius: 8px;
                }}
                .header {{
                    text-align: center;
                    font-size: 24px;
                    color: #2d2d2d;
                    margin-bottom: 20px;
                }}
                .footer {{
                    font-size: 12px;
                    color: #aaa;
                    text-align: center;
                    margin-top: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    Unsent Letters
                </div>
                <p>Hi there,</p>
                <p>We wanted to confirm that your account has been successfully deleted from Unsent Letters.</p>
                <p>If this was a mistake, you can always re-register and start anew.</p>
                <div class="footer">
                    &copy; {datetime.now().year} Unsent Letters. All rights reserved.<br>
                    <a href="https://unsentletters.onrender.com/">Visit our website</a> for more information.
                </div>
            </div>
        </body>
        </html>
        """

        # Sending email using Flask-Mail
        msg = Message(subject, sender=app.config['MAIL_USERNAME'], recipients=[email])
        msg.html = body  # Use the HTML content instead of plain text
        mail.send(msg)

    except Exception as e:
        print(f"❌ Failed to send account deletion email: {e}")


# ========== FORGOT PASSWORD ==========
@app.route('/forgot', methods=['GET', 'POST'])
def forgot():
    if request.method == 'POST':
        email = request.form['email']

        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = c.fetchone()

        if not user:
            conn.close()
            return "⚠️ No account found with that email."

        otp = str(randint(1000, 9999))
        c.execute("UPDATE users SET otp = ? WHERE email = ?", (otp, email))
        conn.commit()
        conn.close()

        session['reset_email'] = email
        session['reset_otp'] = otp
        # Send OTP email for password reset, pass reset=True
        send_otp(email, otp, reset=True)  # This triggers the password reset content


        return redirect('/verify-reset-otp')
    return render_template('forgot.html')

@app.route('/verify-reset-otp', methods=['GET', 'POST'])
def verify_reset_otp():
    if request.method == 'POST':
        otp_entered = request.form['otp']
        email = session.get('reset_email')
        expected_otp = session.get('reset_otp')

        if otp_entered.strip() == expected_otp.strip():
            return redirect('/reset-password')
        else:
            return "Invalid OTP. Please try again."

    return render_template('verify_reset_otp.html')

@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        new_password = request.form['new_password']
        email = session.get('reset_email')

        conn = get_db()
        c = conn.cursor()
        c.execute("UPDATE users SET password = ? WHERE email = ?", (new_password, email))
        conn.commit()
        conn.close()

        session.pop('reset_email', None)
        session.pop('reset_otp', None)

        # Success message with HTML and CSS
        return render_template('reset_success.html')

    return render_template('reset_password.html')

@app.route('/login-history')
def login_history():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT DISTINCT email FROM login_history ORDER BY id DESC")
    emails = [row[0] for row in c.fetchall()]
    conn.close()
    return jsonify(emails)
@app.route('/delete-letter/<int:letter_id>', methods=['POST'])
def delete_letter(letter_id):
    email = session.get('email')
    if not email:
        return 'Unauthorized', 403

    conn = get_db()
    c = conn.cursor()
    c.execute('DELETE FROM letters WHERE id = ? AND user_email = ?', (letter_id, email))
    conn.commit()
    conn.close()
    return '', 204

@app.route('/saved-letters-page')
def saved_letters_page():
    email = session.get('email')
    if not email:
        return redirect(url_for('login'))  # Redirect to login if the user is not logged in

    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT avatar FROM users WHERE email = ?", (email,))
    avatar = c.fetchone()

    # If no avatar, set a fallback
    avatar = avatar[0] if avatar else 'default_avatar.png'

    conn.close()

    # Pass the avatar to the template
    return render_template('saved_letters.html', data={'avatar': avatar})

from flask import make_response

@app.route('/saved-letters')
def saved_letters():
    email = session.get('email')
    if not email:
        return jsonify([])

    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)  # Normalize today's date to midnight
    conn = get_db()
    c = conn.cursor()

    # Fetch Text Time Capsules (letters)
    c.execute('''SELECT letters.id, letter, reply, title, mood, letters.timestamp, 
                        letters.burnt, letters.profile_icon, users.avatar, letters.open_date, letters.is_time_capsule 
                 FROM letters
                 JOIN users ON letters.user_email = users.email
                 WHERE letters.user_email = ? AND letters.burnt = 0''', (email,))
    letter_rows = c.fetchall()

    # Fetch Voice Capsules
    c.execute('''SELECT id, title, letter, voice_path, unlock_date, music, created_at
                 FROM voice_capsules
                 WHERE user_email = ? AND deleted = 0''', (email,))
    voice_rows = c.fetchall()

    conn.close()

    # Merging both text letters and voice capsules
    all_capsules = []

    # Adding text letters to the merged list
    for r in letter_rows:
        try:
            # Handle empty open_date for text capsules
            if not r[9]:  # If open_date is empty
                letter_date = today  # Use today's date as default
            else:
                letter_date = datetime.strptime(r[9], '%Y-%m-%d')  # Convert open_date to a date object
                letter_date = letter_date.replace(hour=0, minute=0, second=0, microsecond=0)  # Set time to midnight

            # Ensure today is normalized to midnight
            today = today.replace(hour=0, minute=0, second=0, microsecond=0)

            # Debugging: Log the open_date and today's date
            print(f"Letter Open Date: {letter_date}, Today's Date: {today}")

            # Check if the text time capsule is locked based on the open_date
            is_locked = r[10] == 1 and letter_date > today  # If it's a time capsule and the open_date is in the future
            
            # Debugging: Log the locked state
            print(f"Is Locked: {is_locked}")

            all_capsules.append({
                'id': r[0],
                'letter': r[1],
                'reply': r[2],
                'title': r[3],
                'mood': r[4],
                'timestamp': r[5],
                'burnt': r[6],
                'profile_icon': r[7],
                'avatar': r[8],
                'open_date': r[9],
                'is_time_capsule': r[10],
                'is_locked': is_locked,  # Add an additional field to indicate if it's locked
                'type': 'text'
            })
        except Exception as e:
            print(f"Error processing letter ID {r[0]}: {e}")

    # Adding voice capsules to the merged list
    for r in voice_rows:
        try:
            # Handle empty unlock_date for voice capsules
            if not r[4]:  # If unlock_date is empty
                unlock_date = today  # Use today's date as default
            else:
                unlock_date = datetime.strptime(r[4], '%Y-%m-%d')  # Convert unlock_date to a date object
                unlock_date = unlock_date.replace(hour=0, minute=0, second=0, microsecond=0)  # Set time to midnight

            # Ensure today is normalized to midnight
            today = today.replace(hour=0, minute=0, second=0, microsecond=0)

            # Check if the voice time capsule is locked based on the unlock_date
            is_locked = unlock_date > today  # If the unlock date is in the future, it's locked

            all_capsules.append({
                'id': r[0],
                'letter': r[2],
                'title': r[1],
                'voice_path': r[3],
                'open_date': r[4],
                'music': r[5],
                'timestamp': r[6],
                'is_time_capsule': 1,  # Mark as time capsule
                'is_locked': is_locked,  # Add an additional field to indicate if it's locked
                'type': 'voice'
            })
        except Exception as e:
            print(f"Error processing voice capsule ID {r[0]}: {e}")

    return jsonify(all_capsules)



@app.route('/letter-analytics')
def letter_analytics():
    email = session.get('email')
    if not email:
        return jsonify({})

    conn = get_db()
    c = conn.cursor()

    # Total saved (non-burnt) letters
    c.execute('SELECT COUNT(*) FROM letters WHERE user_email = ? AND burnt = 0', (email,))
    total_saved = c.fetchone()[0]

    # Mood frequency
    c.execute('SELECT mood, COUNT(*) as count FROM letters WHERE user_email = ? AND burnt = 0 GROUP BY mood ORDER BY count DESC LIMIT 1', (email,))
    mood_row = c.fetchone()
    most_common_mood = mood_row[0] if mood_row else "None"

    conn.close()

    return jsonify({
        'total_saved': total_saved,
        'most_common_mood': most_common_mood
    })
@app.route('/burn-vs-saved')
def burn_vs_saved():
    email = session.get('email')
    if not email:
        return jsonify({})

    conn = get_db()
    c = conn.cursor()

    c.execute('SELECT COUNT(*) FROM letters WHERE user_email = ? AND burnt = 1', (email,))
    burnt = c.fetchone()[0]

    c.execute('SELECT COUNT(*) FROM letters WHERE user_email = ? AND burnt = 0', (email,))
    saved = c.fetchone()[0]

    conn.close()
    return jsonify({
        'burnt': burnt,
        'saved': saved
    })
@app.route('/set-avatar', methods=['POST'])
def set_avatar():
    email = session.get('email')
    if not email:
        return 'Unauthorized', 403

    avatar = request.form.get('avatar', '')
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE users SET avatar = ? WHERE email = ?", (avatar, email))
    conn.commit()
    conn.close()
    return '', 204
@app.route('/choose-avatar')
def choose_avatar():
    email = session.get('email')
    if not email:
        return redirect(url_for('login'))  # Redirect to login if user is not logged in

    conn = get_db()
    c = conn.cursor()

    # Fetch the avatar for the logged-in user
    c.execute("SELECT avatar FROM users WHERE email = ?", (email,))
    avatar = c.fetchone()

    # If avatar doesn't exist, set a fallback to the default avatar
    avatar = avatar[0] if avatar else 'default_avatar.png'

    conn.close()

    # Pass the avatar in the data dictionary to the template
    data = {'avatar': avatar}
    return render_template('avatar_picker.html', data=data)

@app.route('/save-voicecapsule', methods=['POST'])
def save_voice_capsule():
    email = session.get('email')
    if not email:
        return 'Unauthorized', 403

    title = request.form.get('title')
    letter = request.form.get('letter')
    music = request.form.get('music_choice')
    unlock_date = request.form.get('unlock_date') or request.form.get('openDate')
    voice_blob_base64 = request.form.get('voice_blob')
    created_at = datetime.now().strftime('%Y-%m-%d %H:%M')

    voice_data = ''
    if voice_blob_base64:
        try:
            voice_data = voice_blob_base64.strip()  # full data URL with header
        except Exception as e:
            return jsonify({'error': f'Voice processing failed: {str(e)}'}), 500

    conn = get_db()
    c = conn.cursor()
    c.execute('''
        INSERT INTO voice_capsules (user_email, title, letter, voice_path, unlock_date, music, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (email, title, letter, voice_data, unlock_date, music, created_at))
    conn.commit()
    conn.close()

    return jsonify({'message': '✅ Capsule saved successfully'})

@app.route('/save-timecapsule', methods=['POST'])
def save_timecapsule():
    # Get the form data
    title = request.form['title']
    letter = request.form['letter']
    open_date = request.form['unlock_date']  # Get the open date

    # Ensure the open_date includes the time (set to midnight if not provided)
    if open_date:
        open_date = f"{open_date} 00:00:00"  # Adding time as midnight
    
    # Save to database
    conn = get_db()
    c = conn.cursor()
    c.execute('''INSERT INTO letters (title, letter, open_date, is_time_capsule) VALUES (?, ?, ?, 1)''', (title, letter, open_date))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Time Capsule saved!'})

from datetime import datetime

# Register the adapter to convert datetime to string
sqlite3.register_adapter(datetime, lambda v: v.strftime('%Y-%m-%d'))
@app.route('/check-capsule-status')
def check_capsule_status():
    email = session.get('email')
    if not email:
        return jsonify({'should_unlock': False})

    today = datetime.now()
    conn = get_db()
    c = conn.cursor()

    # Check if there are any time capsules with today's date or before
    c.execute('''SELECT COUNT(*) FROM letters WHERE user_email = ? AND is_time_capsule = 1 AND open_date <= ?''', (email, today))
    result = c.fetchone()  # Fetch count of matching time capsules

    conn.close()

    return jsonify({'should_unlock': result[0] > 0})  # Return True if time capsule should be unlocked, otherwise False
def send_unlock_notification(email, capsule_title):
    """Send email notification when a time capsule is unlocked."""
    msg = Message(
        subject=f"Your Time Capsule '{capsule_title}' has been unlocked!",
        recipients=[email]
    )
    msg.body = f"Good news! Your time capsule '{capsule_title}' has just been unlocked. Check it out now!"
    try:
        mail.send(msg)
        print(f"Email sent to {email}")
    except Exception as e:
        print(f"Failed to send email: {e}")




from flask import send_from_directory, jsonify
import os

@app.route('/voice/<filename>')
def serve_voice(filename):
    print(f"Requested file: {filename}")  # Debugging

    voice_notes_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    if os.path.exists(voice_notes_path):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    else:
        return jsonify({"error": f"File '{filename}' not found"}), 404


@app.route('/timecapsule')
def timecapsule():
    email = session.get('email')
    if not email:
        return redirect(url_for('login'))

    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT avatar FROM users WHERE email = ?", (email,))
    avatar = c.fetchone()

    # If no avatar, set a fallback
    avatar = avatar[0] if avatar else 'default_avatar.png'

    conn.close()

    return render_template('timecapsule.html', data={'avatar': avatar})

import os

# Use the absolute path to the folder
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'voice_notes')  # Use the current working directory
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



# Ensure the directory exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
from werkzeug.utils import secure_filename

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    # Debugging: print the saved file path
    print(f"File saved at: {file_path}")

    return jsonify({"message": "File uploaded successfully", "filename": filename}), 200

# ========== RUN ==========
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)


