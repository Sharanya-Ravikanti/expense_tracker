from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "Flask server is running!"
@app.route('/init-db')
def init_db():
    import sqlite3
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    c.execute('DROP TABLE IF EXISTS expenses')
    c.execute('''CREATE TABLE expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        amount REAL NOT NULL,
        date TEXT NOT NULL,
        category TEXT NOT NULL
    )''')
    conn.commit()
    conn.close()
    return "Database initialized!"

@app.route('/add-expense', methods=['POST'])
def add_expense():
    data = request.get_json()
    title = data.get('title')
    amount = data.get('amount')
    date_str = data.get('date')
    category = data.get('category')
    # Input validation
    if not title or not isinstance(amount, (int, float)) or not date_str or not category:
        return jsonify({'error': 'Invalid input'}), 400
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        return jsonify({'error': 'Invalid date format, should be YYYY-MM-DD'}), 400
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    c.execute("INSERT INTO expenses (title, amount, date, category) VALUES (?, ?, ?, ?)", (title, amount, date_str, category))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Expense added!'})

@app.route('/expenses', methods=['GET'])
def get_expenses():
    category = request.args.get('category')
    date_filter = request.args.get('date')
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    query = "SELECT id, title, amount, date, category FROM expenses"
    params = []
    if category and date_filter:
        query += " WHERE category = ? AND date = ?"
        params = [category, date_filter]
    elif category:
        query += " WHERE category = ?"
        params = [category]
    elif date_filter:
        query += " WHERE date = ?"
        params = [date_filter]
    c.execute(query, params)
    expenses = c.fetchall()
    conn.close()
    return jsonify([
        {'id': row[0], 'title': row[1], 'amount': row[2], 'date': row[3], 'category': row[4]} for row in expenses
    ])

@app.route('/update-expense/<int:expense_id>', methods=['PUT'])
def update_expense(expense_id):
    data = request.get_json()
    title = data.get('title')
    amount = data.get('amount')
    date_str = data.get('date')
    category = data.get('category')
    if not title or not isinstance(amount, (int, float)) or not date_str or not category:
        return jsonify({'error': 'Invalid input'}), 400
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        return jsonify({'error': 'Invalid date format, should be YYYY-MM-DD'}), 400
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    c.execute("UPDATE expenses SET title = ?, amount = ?, date = ?, category = ? WHERE id = ?", (title, amount, date_str, category, expense_id))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Expense updated!'})

@app.route('/delete-expense/<int:expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    c.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Expense deleted!'})

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
