from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
import boto3
import pandas as pd
import decimal
from google.visualization.data import DataTable

app = Flask(__name__)

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
        return render_template('chart.html', distance_counts=distance_counts, chart_html=chart_html)


@app.route('/login', methods=['GET', 'POST'])
def login():
    # (código existente)

@app.route('/obtener_datos', methods=['GET'])
def obtener_datos():
    # (código existente)

def upload_dynamo(data):
    # (código existente)

    # Crear el código HTML para el gráfico de Google Charts
    chart_html = generate_google_chart(df_filtered)

    # Devolver tanto el código HTML del gráfico como los datos
    return chart_html, df['payload'], df['distancia'].value_counts()

def generate_google_chart(df):
    # (código existente)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)