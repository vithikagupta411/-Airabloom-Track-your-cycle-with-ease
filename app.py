from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime, timedelta
import sqlite3
import calendar
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'supersecretkey123!'
DB_NAME = 'period_tracker.db'

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    if 'user_id' in session:
        return render_template('index.html')
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
            conn.commit()
            flash("Account created successfully. Please login.", "success")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("Username already exists.", "error")
        finally:
            conn.close()
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            # Toast notification message after successful login
            flash("Welcome back! Don’t forget to log your latest cycle date 💌", "success")
            return redirect(url_for('home'))
        else:
            flash("Invalid username or password.", "error")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for('login'))

@app.route('/result', methods=['POST'])
def result():
    if 'user_id' not in session:
        flash("Please log in first.", "error")
        return redirect(url_for('login'))

    user_id = session['user_id']
    last_period_date = request.form['last_period_date']
    cycle_length = int(request.form['cycle_length'])

    conn = get_db_connection()
    conn.execute('INSERT INTO user_cycles (user_id, last_period_date, cycle_length) VALUES (?, ?, ?)',
                 (user_id, last_period_date, cycle_length))
    conn.commit()
    conn.close()

    today = datetime.now().date()
    last_date = datetime.strptime(last_period_date, '%Y-%m-%d').date()

    period_days = set()
    ovulation_days = set()

    for month_offset in range(6):
        first_day = (today.replace(day=1) + timedelta(days=32 * month_offset)).replace(day=1)
        year, month = first_day.year, first_day.month
        _, last_day = calendar.monthrange(year, month)

        for i in range(last_day):
            day = datetime(year, month, i + 1).date()
            days_since = (day - last_date).days
            if days_since >= 0 and days_since % cycle_length == 0:
                for j in range(5):
                    period_days.add(str(day + timedelta(days=j)))
                ovulation_start = day + timedelta(days=14)
                for j in range(5):
                    ovulation_days.add(str(ovulation_start + timedelta(days=j)))

    calendars = []
    for month_offset in range(6):
        date = (today.replace(day=1) + timedelta(days=32 * month_offset)).replace(day=1)
        cal = calendar.Calendar().monthdayscalendar(date.year, date.month)
        calendars.append({
            'year': date.year,
            'month': date.month,
            'month_name': date.strftime('%B'),
            'weeks': cal
        })

    return render_template('result.html',
                           calendars=calendars,
                           period_days=period_days,
                           ovulation_days=ovulation_days,
                           today=str(today))

if __name__ == '__main__':
    if not os.path.exists(DB_NAME):
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_cycles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    last_period_date DATE NOT NULL,
                    cycle_length INTEGER NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')
            conn.commit()
    app.run(debug=True)




























































































































































































































































































































































































































































































































