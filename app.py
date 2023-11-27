from flask import Flask, render_template
import boto3
import pandas as pd
import matplotlib.pyplot as plt
from decimal import Decimal
from io import BytesIO
import base64

app = Flask(__name__)

# Configura los detalles de tu base de datos RDS
host = 'basetesis.cexq7m1jqe1w.us-east-2.rds.amazonaws.com'
user = 'admin'
password = 'Tesis12345+'
database = 'coladeras'

def obtener_datos_dynamo():
    # Configurando las credenciales de AWS
    session = boto3.Session(
        aws_access_key_id="AKIAXBJD2EULQEJYEKUL",
        aws_secret_access_key="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",
        region_name="us-east-2"
    )

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

    # Convertir el valor Decimal a un tipo numérico
    df['distancia'] = df['payload'].apply(lambda x: float(x['Distancia']['N']))

    # Convertir 'mac_Id' a timestamp UNIX
    df['fecha'] = pd.to_datetime(df['mac_Id']['S'], unit='ms')  # 'ms' indica que el timestamp está en milisegundos

    # Filtrar los datos para tomar valores cada minuto o cuando la distancia supere los 30 cm
    df_filtered = df[(df['distancia'] > 30) | (df['fecha'].diff() >= pd.Timedelta(minutes=1))]

    # Almacenar la gráfica en un buffer de Bytes
    fig, ax = plt.subplots()
    for day, group in df_filtered.groupby(df_filtered['fecha'].dt.date):
        group.plot(x='fecha', y='distancia', marker='o', linestyle='-', legend=True, ax=ax)

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    # Codificar la imagen como base64 para mostrarla en HTML
    image_base64 = base64.b64encode(buffer.read()).decode('utf-8')

    # Cerrar la figura para liberar recursos
    plt.close()

    return image_base64

@app.route('/login', methods=['GET', 'POST'])
def login():
    # ... (tu código actual)

@app.route('/obtener_datos', methods=['GET'])
def obtener_datos():
    # Obtener la imagen codificada en base64
    imagen_base64 = obtener_datos_dynamo()

    # Pasar la imagen a la plantillasda y renderizarla
    
    return render_template('index.html', imagen_base64=imagen_base64)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)