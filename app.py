from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
import boto3
import pandas as pd
import matplotlib.pyplot as plt
from decimal import Decimal

app = Flask(__name__)



# Configura los detalles de tu base de datos RDS
host = 'basetesis.cexq7m1jqe1w.us-east-2.rds.amazonaws.com'
user = 'admin'
password = 'Tesis12345+'
database = 'coladeras'
session = boto3.Session(
    aws_access_key_id="AKIAXBJD2EULQEJYEKUL",
    aws_secret_access_key="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",
    region_name="us-east-2"
    )

@app.route('/mostrardatos', methods=['GET'])
def datos():
    if request.method == 'GET':
        # Llamar a la función con algún dato (puedes ajustar esto según tus necesidades)
        upload_dynamo(None)

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
            host='basetesis.cexq7m1jqe1w.us-east-2.rds.amazonaws.com',
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
                   # session['user_id'] = user_data['id']
                    return redirect(url_for('obtener_datos'))
                else:
                    # Credenciales incorrectas, redirige a la página de inicio de sesión
                      return render_template('login.html')
        finally:
            connection.close()

       

    return render_template('login.html')


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
def upload_dynamo(data):

    # Creamos una instancia del cliente DynamoDb
    dynamodb = session.resource('dynamodb')

    # Nombre de la tabla
    table_name = 'Datos_Monitoreo'

    # Crear un objeto de la tabla
    table = dynamodb.Table(table_name)

    # Hacer un escaneo completo
    response = table.scan()

    # Extraer la información de la respuesta
    data = response['Items']

    # Convertir los datos en una tabla de Dynamo
    df = pd.DataFrame(data)

    # Imprimir los valores de la columna 'payload' para depuración
    print("Valores de la columna 'payload':")
    print(df['payload'])

    # Convertir el valor Decimal a un tipo numérico
    df['distancia'] = df['payload'].apply(lambda x: float(x['Distancia']) if isinstance(x['Distancia'], Decimal) else x['Distancia'])

    # Imprimir el recuento de valores para la columna 'distancia'
    print("Recuento de valores para la columna 'distancia':")
    print(df['distancia'].value_counts())

    # Convertir 'mac_Id' a timestamp UNIX
    df['fecha'] = pd.to_datetime(df['mac_Id'], unit='ms')  # 'ms' indica que el timestamp está en milisegundos

    # Filtrar los datos para tomar valores cada minuto o cuando la distancia supere los 30 cm
    df_filtered = df[(df['distancia'] > 30) | (df['fecha'].diff() >= pd.Timedelta(minutes=1))]

    # Imprimir información sobre los grupos
    print("Información sobre los grupos:")
    for day, group in df_filtered.groupby(df_filtered['fecha'].dt.date):
        print(f"Fecha: {day}, Cantidad de registros: {len(group)}")

        fig, ax = plt.subplots()

        # Crear una gráfica de líneas para cada día
        group.plot(x='fecha', y='distancia', marker='o', linestyle='-', legend=True, ax=ax)

        # Establecer las etiquetas
        ax.set_xlabel('Fecha')
        ax.set_ylabel('Nivel del agua (cm)')

        # Establecer el título de la tabla en el gráfico
        ax.set_title(f"Día {day}")

        # Configurar el rango del eje y sin incluir el 0
        if not group['distancia'].empty:  # Verificar si la columna 'distancia' no está vacía
            min_distancia_non_zero = group[group['distancia'] != 0]['distancia'].min()
            max_distancia_non_zero = group[group['distancia'] != 0]['distancia'].max()

            if not pd.isna(min_distancia_non_zero) and not pd.isna(max_distancia_non_zero):
                ax.set_ylim(bottom=min_distancia_non_zero, top=max_distancia_non_zero)

        # Mostrar la leyenda
        ax.legend(title='Distancia')

        # Mostrar la gráfica
        plt.show()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

