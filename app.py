from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import boto3
import pandas as pd
import plotly.express as px

app = Flask(__name__)

# Configura los detalles de tu base de datos RDs
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
        chart_html = upload_dynamo(None)
        return render_template('chart.html', chart_html=chart_html)

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

    # Convertir el valor Decimal a un tipo numérico
    df['distancia'] = df['payload'].apply(lambda x: float(x['Distancia']) if isinstance(x['Distancia'], decimal.Decimal) else x['Distancia'])

    # Convertir 'mac_Id' a timestamp UNIX
    df['fecha'] = pd.to_datetime(df['mac_Id'], unit='ms')  # 'ms' indica que el timestamp está en milisegundos

    # Filtrar los datos para tomar valores cada minuto o cuando la distancia supere los 30 cm
    df_filtered = df[(df['distancia'] > 30) | (df['fecha'].diff() >= pd.Timedelta(minutes=1))]

    # Imprimir información sobre los grupos
    print("Información sobre los grupos:")
    for day, group in df_filtered.groupby(df_filtered['fecha'].dt.date):
        print(f"Fecha: {day}, Cantidad de registros: {len(group)}")

        # Crear una gráfica de líneas para cada día con Plotly
        chart_html = generate_plotly_chart(group)
        return chart_html  # Cambiamos para devolver el código HTML del gráfico

def generate_plotly_chart(df):
    fig = px.line(df, x='fecha', y='distancia', title='Gráfico de Nivel del Agua')
    chart_html = fig.to_html(full_html=False)
    return chart_html

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
