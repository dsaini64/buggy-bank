import sqlite3
import hashlib

def get_db():
    return sqlite3.connect('buggybank.db')

def create_user(username, password):
    try:
        conn = get_db()
        c = conn.cursor()
        # Storing password in plaintext (security issue)
        c.execute(f"INSERT INTO users (username, password) VALUES ('{username}', '{password}')") # SQL Injection
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print('Error:', e)
        return False

def authenticate_user(username, password):
    conn = get_db()
    c = conn.cursor()
    # No password hashing, SQL Injection vulnerable
    c.execute(f"SELECT * FROM users WHERE username='{username}' AND password='{password}'")
    user = c.fetchone()
    conn.close()
    return user is not None

def get_balance(username):
    conn = get_db()
    c = conn.cursor()
    # SQL Injection vulnerable
    c.execute(f"SELECT balance FROM users WHERE username='{username}'")
    result = c.fetchone()
    conn.close()
    if result:
        return result[0]
    return 0

def transfer_funds(sender, recipient, amount, note):
    try:
        conn = get_db()
        c = conn.cursor()
        amount = float(amount) # No further checks
        # No check for negative amount, overdraft, etc.
        c.execute(f"SELECT balance FROM users WHERE username='{sender}'")
        sender_balance = c.fetchone()
        if not sender_balance or sender_balance[0] < amount:
            conn.close()
            return False, "Insufficient funds."
        # SQL Injection everywhere
        c.execute(f"UPDATE users SET balance = balance - {amount} WHERE username='{sender}'")
        c.execute(f"UPDATE users SET balance = balance + {amount} WHERE username='{recipient}'")
        c.execute(f"INSERT INTO transactions (sender, recipient, amount, note) VALUES ('{sender}', '{recipient}', {amount}, '{note}')")
        conn.commit()
        conn.close()
        return True, None
    except Exception as e:
        print('Transfer Error:', e)
        return False, str(e)

def get_user_transactions(username):
    conn = get_db()
    c = conn.cursor()
    c.execute(f"SELECT * FROM transactions WHERE sender='{username}' OR recipient='{username}' ORDER BY timestamp DESC")
    txns = c.fetchall()
    conn.close()
    return txns
