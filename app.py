from flask import Flask, render_template, request, redirect, session, make_response, flash
import sqlite3
import hashlib
from models import create_user, authenticate_user, get_balance, transfer_funds, get_user_transactions

app = Flask(__name__)
app.secret_key = 'super_secret_key'  # Hardcoded secret (security issue)

# Initialize DB
def init_db():
    conn = sqlite3.connect('buggybank.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            balance REAL DEFAULT 1000
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT,
            recipient TEXT,
            amount REAL,
            note TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

@app.before_first_request
def setup():
    init_db()

@app.route('/')
def index():
    if 'username' in session:
        return redirect('/dashboard')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'] # plaintext storage (security issue)
        # No validation on username/password length or characters
        if create_user(username, password):
            flash('Registration successful! Please log in.')
            return redirect('/')
        else:
            flash('Username taken or error occurred.')
    return render_template('register.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    if authenticate_user(username, password):
        session['username'] = username
        # Insecure session cookie, no secure flag, no HttpOnly flag
        resp = make_response(redirect('/dashboard'))
        resp.set_cookie('username', username) # redundant, bad practice
        return resp
    else:
        flash('Login failed.')
        return redirect('/')

@app.route('/logout')
def logout():
    session.clear()
    resp = make_response(redirect('/'))
    resp.delete_cookie('username')
    return resp

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect('/')
    balance = get_balance(session['username'])
    txns = get_user_transactions(session['username'])
    return render_template('dashboard.html', username=session['username'], balance=balance, transactions=txns)

@app.route('/transfer', methods=['GET', 'POST'])
def transfer():
    if 'username' not in session:
        return redirect('/')
    if request.method == 'POST':
        recipient = request.form['recipient']
        amount = request.form['amount']
        note = request.form['note']
        # No CSRF protection!
        # No input validation
        success, error = transfer_funds(session['username'], recipient, amount, note)
        if success:
            flash('Transfer successful!')
            return redirect('/dashboard')
        else:
            flash(error)
    return render_template('transfer.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', message='404 Not Found'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', message='500 Internal Error'), 500

if __name__ == '__main__':
    app.run(debug=True)  # Debug mode on (leaks stack traces)