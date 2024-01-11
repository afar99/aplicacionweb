from flask import Flask, render_template, render_template_string, request, redirect, url_for, session
import mysql.connector
import boto3
import pandas as pd
import decimal
from gviz_api import DataTable


app = Flask(_name_)

# Configura los detalles de tu base de datos RD
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
        chart_html, payload_data, distance_counts = upload_dynamo(None)
        try :
            print("payload_data:")
            print(payload_data)
            print("distance_counts:")
            print(distance_counts)
            print("chart_html:")
            print(chart_html)
        
        except:
            print("error; no se pudo obtener payload_data")
        return render_template_string(chart_html)

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
    # ... (código existente)

    # Crear una instancia del cliente DynamoDb
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
    df['distancia'] = df['payload'].apply(lambda x: float(x['Distancia']) if isinstance(x['Distancia'], decimal.Decimal) else x['Distancia'])

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
        # print(f"Fecha: {day}, Cantidad de registros: {len(group)}")

        # Crear una gráfica de líneas para cada día con Google Charts
        chart_html = generate_google_chart(group)
        chart_html = generate_google_chart(df_filtered)
        # Convertir la serie a un diccionario antes de devolverla
        distance_counts_dict = df['distancia'].value_counts().to_dict()
    return chart_html, df['payload'], df['distancia'].value_counts()  # Cambiamos para devolver el código HTML del gráfico

def generate_google_chart(df):
    # Crear la descripción del gráfico para gviz_api
    description = {"fecha": ("datetime", "Fecha"), "distancia": ("number", "Nivel del agua (cm)")}

    # Crear los datos para gviz_api
    data = []
    encabezado = ["Registro", "Nivel del agua (cm)"]
    data.append(encabezado)

    for _, row in df.iterrows():
        # element ={row['fecha'], row['distancia']}
        fecha = row['fecha'].strftime("%Y-%m-%d %H:%M:%S")
        element = [fecha, row['distancia']]
        data.append(element)

    # Crear el DataTable de gviz_api
    # print("Creando DataTable de gviz_api...")
    # data_table = DataTable(description)
    # data_table.LoadData(data)

    # Obtener el código JSON del DataTable
    # print("Obteniendo código JSON del DataTable...")
    # # chart_json = data_table.ToJSon(columns_order=("fecha", "distancia"), order_by="fecha")
    # print("chart_json obtenido")

    # Crear el código HTML para el ráfico de Google Charts
    chart_html = """
    <html>
      <head>
        <script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@1/css/pico.min.css">
        <title>Gráfico de Nivel del Agua</title>
        <script type="text/javascript">
          google.charts.load('current', {{'packages':['corechart']}});
          google.charts.setOnLoadCallback(drawChart);

          function drawChart() {{
            var data = new google.visualization.arrayToDataTable({});
            
            var options = {{
              title: 'Gráfico de Nivel del Agua',
              curveType: 'function',
              legend: {{ position: 'bottom' }}
            }};

            var chart = new google.visualization.LineChart(document.getElementById('chart_div'));
            chart.draw(data, options);
          }}
        </script>
      </head>
      <body>
        <main class="container">
            <h1>Gráfico de Nivel del Agua</h1>
            <div id="chart_div" style="width: 100%; height: 500px;"></div>
        </main>
      </body>
    </html>
    """.format(data)

    return chart_html

if _name_ == '_main_':
    app.run(host='0.0.0.0', port=5000)