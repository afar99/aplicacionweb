from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector

app = Flask(__name__)

# Configura los detalles de tu base de datos RDS
host = 'basetesis.cexq7m1jqe1w.us-east-2.rds.amazonaws.com'
user = 'admin'
password = 'Tesis12345+'
database = 'coladeras'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Obtén los datos del formulario de inicio de sesión
        username = request.form['username']
        password1 = request.form['password']

        # Conéctate a la base de datos
        connection = mysql.connector.connect(
            user=user,
            password=password,
            host=host,
            database=database,
            port=3306
        )

        try:
            with connection.cursor(dictionary=True) as cursor:
                # Ejecuta tu consulta SQL
                sql = 'SELECT * FROM usuarios WHERE usuario = %s AND contrasena = %s'
                cursor.execute(sql, (username, password1))
                user_data = cursor.fetchone()

                if user_data:
                    # Inicio de sesión exitoso, guarda la información del usuario en la sesión
                    session['user_id'] = user_data['id']
                    return redirect(url_for('obtener_datos'))
                else:
                    # Credenciales incorrectas, redirige a la página de inicio de sesión
                    return render_template('login.html')
        finally:
            connection.close()

    return render_template('login.html')


@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        # Obtén los datos del formulario de registro
        numero_de_usuario = request.form['numero_de_usuario']
        username = request.form['username']
        password = request.form['password']
        nombre = request.form['nombre']
        correo = request.form['correo']

        # Conéctate a la base de datos
        connection = mysql.connector.connect(
            user=user,
            password=password,
            host=host,
            database=database,
            port=3306
        )

        try:
            with connection.cursor(dictionary=True) as cursor:
                # Inserta los datos en la tabla usuarios
                sql = 'INSERT INTO usuarios (numero_de_usuario, usuario, contrasena, nombre, correo) VALUES (%s, %s, %s, %s, %s)'
                cursor.execute(sql, (numero_de_usuario, username, password, nombre, correo))
                connection.commit()

                # Redirige a la página de inicio de sesión después del registro exitoso
                return redirect(url_for('login'))
        finally:
            connection.close()

    return render_template('registro.html')


@app.route('/obtener_datos', methods=['GET'])
def obtener_datos():
    # Conéctate a la base de datos
    connection = mysql.connector.connect(
        user=user,
        password=password,
        host=host,
        database=database,
        port=3306
    )

    try:
        with connection.cursor(dictionary=True) as cursor:
            # Ejecuta tu consulta SQL
            sql = 'SELECT * FROM coladera'  # Reemplaza con el nombre real de tu tabla
            cursor.execute(sql)
            result = cursor.fetchall()
    finally:
        connection.close()

    # Devuelve los datos como HTML usando una plantilla
    return render_template('index.html', result=result)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)