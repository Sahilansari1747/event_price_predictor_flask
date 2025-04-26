from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from model import predict_price

app = Flask(__name__)
app.secret_key = 'secret123'

# Credentials (Admin only; users use signup/login from DB)
users = {
    "admin": "Sahil123"
}

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None
    success = None

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == 'admin':
            error = "You cannot register with the admin username."
        else:
            try:
                conn = sqlite3.connect('bookings.db')
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
                if cursor.fetchone():
                    error = "Username already exists."
                else:
                    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
                    conn.commit()
                    success = "Account created! You can now login."
            except Exception as e:
                error = f"Database error: {str(e)}"
            finally:
                conn.close()

    return render_template('signup.html', error=error, success=success)

@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == 'admin' and users[username] == password:
            session['username'] = username
            return redirect(url_for('admin_dashboard'))
        else:
            conn = sqlite3.connect('bookings.db')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
            user = cursor.fetchone()
            conn.close()
            if user:
                session['username'] = username
                return redirect(url_for('landing_page'))
            else:
                error = "Invalid credentials."

    return render_template('index.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/landing')
def landing_page():
    return render_template('landing.html')

@app.route('/predict', methods=['GET', 'POST'])
def event():
    if request.method == 'POST':
        form_type = request.form.get('form_type')

        if form_type == 'predict':
            try:
                session['event_details'] = {
                    'event_type': request.form['event_type'],
                    'guest_count': int(request.form['guest_count']),
                    'venue_area': float(request.form['venue_area']),
                    'food_type': request.form['food_type'],
                    'decoration': request.form['decoration'],
                    'entertainment': request.form['entertainment'],
                    'duration': float(request.form['duration']),
                    'event_date': request.form['event_date']
                }

                details = session['event_details']
                price = predict_price(
                    details['event_type'], details['guest_count'], details['venue_area'],
                    details['food_type'], details['decoration'], details['entertainment'], details['duration']
                )

                session['predicted_price'] = price
                return render_template('admin.html', price=price, show_confirm=True, **details)

            except Exception as e:
                return render_template('admin.html', error=f"Error: {str(e)}")

        elif form_type == 'confirm':
            try:
                username = session.get('username')
                details = session.get('event_details')
                price = session.get('predicted_price')

                if not username or not details or not price:
                    return redirect(url_for('login'))

                conn = sqlite3.connect('bookings.db')
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO booked_events (
                        username, event_type, guest_count, venue_area, food_type,
                        decoration, entertainment, duration, price, event_date
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    username, details['event_type'], details['guest_count'],
                    details['venue_area'], details['food_type'], details['decoration'],
                    details['entertainment'], details['duration'], price, details['event_date']
                ))
                conn.commit()
                conn.close()

                return render_template('success.html', price=price, event_date=details['event_date'])

            except Exception as e:
                return render_template('admin.html', error=f"Error: {str(e)}")

    return render_template('admin.html')

@app.route('/admin-dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/booked-events')
def booked_events_page():
    conn = sqlite3.connect('bookings.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM booked_events")
    events = cursor.fetchall()
    conn.close()
    return render_template('booked_events.html', events=events)

if __name__ == '__main__':
    app.run(debug=True)