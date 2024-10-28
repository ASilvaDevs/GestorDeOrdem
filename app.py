from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Função de conexão com o banco de dados
def get_db_connection():
    conn = sqlite3.connect('service_orders.db')
    conn.row_factory = sqlite3.Row
    return conn

# Inicializa o banco de dados
def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT NOT NULL
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT,
            start_time TEXT,
            end_time TEXT,
            FOREIGN KEY(order_id) REFERENCES orders(id)
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Rota para a página inicial
@app.route('/')
def index():
    conn = get_db_connection()
    orders = conn.execute('SELECT * FROM orders').fetchall()
    conn.close()
    return render_template('index.html', orders=orders)

# Rota para criar uma nova ordem de serviço
@app.route('/create_order', methods=['GET', 'POST'])
def create_order():
    if request.method == 'POST':
        order_id = request.form['order_id']
        title = request.form['title']
        description = request.form['description']

        conn = get_db_connection()
        conn.execute('INSERT INTO orders (id, title, description) VALUES (?, ?, ?)',
                     (order_id, title, description))
        conn.commit()
        conn.close()

        return redirect(url_for('index'))

    return render_template('create_order.html')

# Rota para exibir detalhes da ordem de serviço
@app.route('/order/<id>')
def order_details(id):
    conn = get_db_connection()
    order = conn.execute('SELECT * FROM orders WHERE id = ?', (id,)).fetchone()
    activities = conn.execute('SELECT * FROM activities WHERE order_id = ?', (id,)).fetchall()
    conn.close()
    return render_template('order_details.html', order=order, activities=activities)

# Rota para iniciar uma atividade
@app.route('/start_activity/<order_id>')
def start_activity(order_id):
    conn = get_db_connection()
    start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute('INSERT INTO activities (order_id, start_time) VALUES (?, ?)', (order_id, start_time))
    conn.commit()
    conn.close()
    return redirect(url_for('order_details', id=order_id))

# Rota para finalizar a última atividade
@app.route('/end_activity/<order_id>')
def end_activity(order_id):
    conn = get_db_connection()
    end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute('''
        UPDATE activities
        SET end_time = ?
        WHERE order_id = ? AND end_time IS NULL
    ''', (end_time, order_id))
    conn.commit()
    conn.close()
    return redirect(url_for('order_details', id=order_id))

# Rota para editar uma atividade específica
@app.route('/edit_activity/<int:activity_id>', methods=['GET', 'POST'])
def edit_activity(activity_id):
    conn = get_db_connection()
    activity = conn.execute('SELECT * FROM activities WHERE id = ?', (activity_id,)).fetchone()

    if request.method == 'POST':
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        conn.execute('''
            UPDATE activities
            SET start_time = ?, end_time = ?
            WHERE id = ?
        ''', (start_time, end_time, activity_id))
        conn.commit()
        conn.close()
        return redirect(url_for('order_details', id=activity['order_id']))

    conn.close()
    return render_template('edit_activity.html', activity=activity)

# Rota para deletar uma atividade
@app.route('/delete_activity/<int:activity_id>')
def delete_activity(activity_id):
    conn = get_db_connection()
    activity = conn.execute('SELECT * FROM activities WHERE id = ?', (activity_id,)).fetchone()
    conn.execute('DELETE FROM activities WHERE id = ?', (activity_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('order_details', id=activity['order_id']))

if __name__ == '__main__':
    app.run(debug=True)
