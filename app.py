from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from model import predict_price

app = Flask(__name__)
app.secret_key = 'secret123'

# Credentials
users = {
    "admin": "Sahil123",
    "user1": "pass1"
}

booked_events = []

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
                existing_user = cursor.fetchone()

                if existing_user:
                    error = "Username already exists. Try logging in."
                else:
                    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
                    conn.commit()
                    success = "Account created successfully! You can now login."
            except Exception as e:
                error = f"Database error: {str(e)}"
            finally:
                conn.close()

    return render_template('signup.html', error=error, success=success)

@app.route('/logout')
def logout():
    return redirect('/')

@app.route('/landing')
def landing_page():
    return render_template('landing.html')

@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in users and users[username] == password:
            session['username'] = username
            if username == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('landing_page'))
        else:
            try:
                conn = sqlite3.connect('bookings.db')
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
                result = cursor.fetchone()
                if result:
                    session['username'] = username
                    return redirect(url_for('landing_page'))
                else:
                    error = 'Invalid credentials. Please try again.'
            except Exception as e:
                error = f"Database error: {str(e)}"
            finally:
                conn.close()

    return render_template('index.html', error=error)

@app.route('/admin-dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/predict', methods=['GET', 'POST'])
def event():
    price = None
    error = None
    event_data = None

    if request.method == 'POST':
        try:
            event_type = request.form['event_type']
            guest_count = int(request.form['guest_count'])
            venue_area = float(request.form['venue_area'])
            food_type = request.form['food_type']
            decoration = request.form['decoration']
            entertainment = request.form['entertainment']
            duration = float(request.form['duration'])
            event_date = request.form['event_date']

            price = predict_price(
                event_type, guest_count, venue_area,
                food_type, decoration, entertainment, duration
            )

            event_data = {
                'event_type': event_type,
                'guest_count': guest_count,
                'venue_area': venue_area,
                'food_type': food_type,
                'decoration': decoration,
                'entertainment': entertainment,
                'duration': duration,
                'price': price,
                'event_date': event_date
            }

            session['booking_data'] = event_data

        except Exception as e:
            error = f"Prediction error: {str(e)}"

    return render_template('admin.html', price=price, error=error, event_data=event_data)

@app.route('/billing')
def billing():
    try:
        base_price = float(request.args.get('price', 0))
        gst = base_price * 0.18
        total = base_price + gst
        return render_template('billing.html', base_price=base_price, gst=gst, total=total)
    except Exception as e:
        return f"Error in billing: {str(e)}"

@app.route('/payment', methods=['GET', 'POST'])
def payment_page():
    if request.method == 'POST':
        method = request.form['payment_method']
        event = {
            'event_type': request.form['event_type'],
            'guest_count': request.form['guest_count'],
            'venue_area': request.form['venue_area'],
            'food_type': request.form['food_type'],
            'decoration': request.form['decoration'],
            'entertainment': request.form['entertainment'],
            'duration': request.form['duration'],
            'price': request.form['price'],
            'event_date': request.form['event_date'],
            'payment_method': method
        }
        booked_events.append(event)
        return redirect(url_for('payment_success', method=method))
    return render_template('payment.html')

@app.route('/payment-success')
def payment_success():
    method = request.args.get('method', 'unknown')
    return f"<h2 style='text-align:center; margin-top: 40px;'>Payment via <strong>{method.upper()}</strong> successful! 🎉</h2>"

@app.route('/booked-events')
def booked_events_page():
    try:
        conn = sqlite3.connect('bookings.db')
        cursor = conn.cursor()
        cursor.execute("SELECT event_type, guest_count, venue_area, food_type, decoration, entertainment, duration, price, event_date FROM booked_events")
        rows = cursor.fetchall()
        events = [
            {
                'event_type': row[0],
                'guest_count': row[1],
                'venue_area': row[2],
                'food_type': row[3],
                'decoration': row[4],
                'entertainment': row[5],
                'duration': row[6],
                'price': row[7],
                'event_date': row[8]
            }
            for row in rows
        ]
        conn.close()
        return render_template('booked_events.html', events=events)
    except Exception as e:
        return f"Error fetching bookings: {str(e)}", 500

@app.route('/confirm-payment', methods=['POST'])
def confirm_payment():
    try:
        data = session.get('booking_data')
        username = session.get('username', 'unknown')

        if not data:
            return "No booking data found. Please try again.", 400

        conn = sqlite3.connect('bookings.db')
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO booked_events (
                username, event_type, guest_count, venue_area, food_type,
                decoration, entertainment, duration, price, event_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            username,
            data['event_type'],
            data['guest_count'],
            data['venue_area'],
            data['food_type'],
            data['decoration'],
            data['entertainment'],
            data['duration'],
            data['price'],
            data['event_date']
        ))
        conn.commit()
        conn.close()

        return render_template('success.html')

    except Exception as e:
        return f"Error saving booking: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True)