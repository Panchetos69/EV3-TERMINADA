from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
import MySQLdb.cursors

app = Flask(__name__)

# Configuración de MariaDB
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'turismo'
app.config['MYSQL_PASSWORD'] = 'Panchetos1234'
app.config['MYSQL_DB'] = 'turismo'

mysql = MySQL(app)
app.secret_key = 'your_secret_key'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        rut = request.form['rut']
        nombre_completo = request.form['nombre_completo']
        direccion = request.form['direccion']
        telefono = request.form['telefono']
        correo_electronico = request.form['correo_electronico']
        
        # Asignar automáticamente la contraseña basada en la parte del correo antes de la "@"
        password = correo_electronico.split('@')[0]
        
        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO users (rut, nombre_completo, direccion, telefono, correo_electronico, password) VALUES (%s, %s, %s, %s, %s, %s)', (rut, nombre_completo, direccion, telefono, correo_electronico, password))
        mysql.connection.commit()
        cursor.close()
        
        return redirect(url_for('register_confirmation', rut=rut, nombre_completo=nombre_completo, direccion=direccion, telefono=telefono, correo_electronico=correo_electronico))
    return render_template('register.html')

@app.route('/register_confirmation')
def register_confirmation():
    return render_template('register_confirmation.html', rut=request.args.get('rut'), nombre_completo=request.args.get('nombre_completo'), direccion=request.args.get('direccion'), telefono=request.args.get('telefono'), correo_electronico=request.args.get('correo_electronico'))

@app.route('/suggestions', methods=['GET', 'POST'])
def suggestions():
    if request.method == 'POST':
        correo_electronico = request.form['correo_electronico']
        mensaje = request.form['mensaje']
        
        user_id = session.get('user_id')
        
        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO suggestions (correo_electronico, mensaje, user_id) VALUES (%s, %s, %s)', (correo_electronico, mensaje, user_id))
        mysql.connection.commit()
        cursor.close()
        
        return redirect(url_for('suggestion_confirmation', correo_electronico=correo_electronico, mensaje=mensaje))
    return render_template('suggestions.html')

@app.route('/suggestion_confirmation')
def suggestion_confirmation():
    return render_template('suggestion_confirmation.html', correo_electronico=request.args.get('correo_electronico'), mensaje=request.args.get('mensaje'))

@app.route('/catalog')
def catalog():
    return render_template('catalog.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        comentario = request.form['comentario']
        # Aquí puedes manejar el comentario como lo necesites
        flash('Comentario enviado', 'success')
    
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    
    cursor.execute('SELECT * FROM suggestions')
    suggestions = cursor.fetchall()
    
    return render_template('admin.html', users=users, suggestions=suggestions)

@app.route('/get_user/<int:id>', methods=['GET', 'POST'])
def get_user(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        rut = request.form['rut']
        nombre_completo = request.form['nombre_completo']
        direccion = request.form['direccion']
        telefono = request.form['telefono']
        correo_electronico = request.form['correo_electronico']
        
        cursor.execute('UPDATE users SET rut=%s, nombre_completo=%s, direccion=%s, telefono=%s, correo_electronico=%s WHERE id=%s', (rut, nombre_completo, direccion, telefono, correo_electronico, id))
        mysql.connection.commit()
        cursor.close()
        flash('Usuario actualizado correctamente', 'success')
        return redirect(url_for('admin'))
    
    cursor.execute('SELECT * FROM users WHERE id = %s', (id,))
    user = cursor.fetchone()
    cursor.close()
    return render_template('edit_user.html', user=user)

@app.route('/delete_user/<int:id>')
def delete_user(id):
    cursor = mysql.connection.cursor()
    cursor.execute('DELETE FROM users WHERE id = %s', (id,))
    mysql.connection.commit()
    cursor.close()
    flash('Usuario eliminado correctamente', 'success')
    return redirect(url_for('admin'))

@app.route('/delete_suggestion/<int:id>')
def delete_suggestion(id):
    cursor = mysql.connection.cursor()
    cursor.execute('DELETE FROM suggestions WHERE id = %s', (id,))
    mysql.connection.commit()
    cursor.close()
    flash('Sugerencia eliminada correctamente', 'success')
    return redirect(url_for('admin'))

@app.route('/respond_suggestion/<int:id>', methods=['GET', 'POST'])
def respond_suggestion(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        respuesta = request.form['respuesta']
        # Aquí puedes manejar la respuesta como lo necesites, por ejemplo, enviarla por correo electrónico
        
        flash('Respuesta enviada', 'success')
        return redirect(url_for('admin'))
    
    cursor.execute('SELECT * FROM suggestions WHERE id = %s', (id,))
    suggestion = cursor.fetchone()
    cursor.close()
    return render_template('respond_suggestion.html', suggestion=suggestion)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE correo_electronico = %s AND password = %s', (email, password))
        account = cursor.fetchone()
        
        if account:
            session['user_id'] = account['id']
            flash('Has iniciado sesión correctamente', 'success')
            return redirect(url_for('profile'))
        else:
            flash('Correo o contraseña incorrectos', 'danger')
    return render_template('login.html')

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        flash('Debes iniciar sesión primero', 'danger')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
    user = cursor.fetchone()
    
    cursor.execute('SELECT * FROM reservations WHERE user_id = %s', (user_id,))
    reservations = cursor.fetchall()
    
    cursor.execute('SELECT * FROM suggestions WHERE user_id = %s', (user_id,))
    suggestions = cursor.fetchall()
    
    return render_template('profile.html', user=user, reservations=reservations, suggestions=suggestions)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
