from flask import Flask, render_template, request, redirect, url_for, send_file
import sqlite3
from datetime import datetime
import pdfkit  # Biblioteca para gerar PDF (instale com `pip install pdfkit`)
import pdfkit

path_to_wkhtmltopdf = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"  # Caminho do wkhtmltopdf no Windows



app = Flask(__name__)

# Função para conectar ao banco de dados
def get_db_connection():
    conn = sqlite3.connect('service_orders.db')
    conn.row_factory = sqlite3.Row
    return conn

# Inicializar o banco de dados
def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            start_time TEXT,
            end_time TEXT,
            FOREIGN KEY (order_id) REFERENCES orders (id)
        )
    ''')
    conn.commit()
    conn.close()

# Rota principal para listar ordens
@app.route('/', methods=['GET', 'POST'])
def index():
    conn = get_db_connection()
    orders = conn.execute('SELECT * FROM orders').fetchall()
    
    # Filtro de datas
    filtered_activities = []
    if request.method == 'POST':
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        
        filtered_activities = conn.execute('''
            SELECT orders.id, orders.title, orders.description, activities.start_time, activities.end_time
            FROM orders
            JOIN activities ON orders.id = activities.order_id
            WHERE DATE(activities.start_time) BETWEEN ? AND ?
            ''', (start_date, end_date)).fetchall()
        
    conn.close()
    return render_template('index.html', orders=orders, filtered_activities=filtered_activities)

# Rota para criar nova ordem de serviço
@app.route('/create_order', methods=['GET', 'POST'])
def create_order():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        
        conn = get_db_connection()
        conn.execute('INSERT INTO orders (title, description) VALUES (?, ?)', (title, description))
        conn.commit()
        conn.close()
        
        return redirect(url_for('index'))
    
    return render_template('create_order.html')

# Rota para visualizar detalhes da ordem de serviço
@app.route('/order/<int:id>')
def order_details(id):
    conn = get_db_connection()
    order = conn.execute('SELECT * FROM orders WHERE id = ?', (id,)).fetchone()
    activities = conn.execute('SELECT * FROM activities WHERE order_id = ?', (id,)).fetchall()
    conn.close()
    return render_template('order_details.html', order=order, activities=activities)

# Rota para iniciar atividade
@app.route('/order/<int:id>/start', methods=['POST'])
def start_activity(id):
    start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    conn = get_db_connection()
    conn.execute('INSERT INTO activities (order_id, start_time) VALUES (?, ?)', (id, start_time))
    conn.commit()
    conn.close()
    
    return redirect(url_for('order_details', id=id))

# Rota para finalizar atividade
@app.route('/order/<int:id>/end/<int:activity_id>', methods=['POST'])
def end_activity(id, activity_id):
    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    conn = get_db_connection()
    conn.execute('UPDATE activities SET end_time = ? WHERE id = ?', (end_time, activity_id))
    conn.commit()
    conn.close()
    
    return redirect(url_for('order_details', id=id))

# Rota para gerar PDF do filtro de datas
@app.route('/generate_pdf', methods=['POST'])
def generate_pdf():
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    
    conn = get_db_connection()
    activities = conn.execute('''
        SELECT orders.id, orders.title, orders.description, activities.start_time, activities.end_time
        FROM orders
        JOIN activities ON orders.id = activities.order_id
        WHERE DATE(activities.start_time) BETWEEN ? AND ?
    ''', (start_date, end_date)).fetchall()
    conn.close()

    rendered = render_template('report.html', activities=activities)
    pdf = pdfkit.from_string(rendered, False, configuration=pdfkit.configuration(wkhtmltopdf=path_to_wkhtmltopdf))
    # Em generate_pdf:


    
    response = send_file(pdf, as_attachment=True, download_name='Relatorio_Ordens_Servico.pdf', mimetype='application/pdf')
    return response

# Inicializar o banco de dados ao iniciar a aplicação
init_db()

if __name__ == '__main__':
    app.run(debug=True)
