from flask import Flask, render_template
import mysql.connector

app = Flask(__name__)

# Configura los detalles de tu base de datos RDS
host = 'basetesis.cexq7m1jqe1w.us-east-2.rds.amazonaws.com'
user = 'admin'
password = 'Tesis12345+'
database = 'coladeras'

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
