import boto3
import pandas as pd

def upload_dynamo(data):
    #configurando las credenciales de AWS
    session = boto3.Session(
        aws_access_key_id="AKIAXBJD2EULQEJYEKUL",
        aws_secret_access_key="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"
        region_name="us_east_1"

    )
#creamos una instancia del cliente DynamoDb
dynamodb = session.resourse('dynamodb')

#Nombre de la tabla
table_name = 'Datos_Monitoreo'

#crear un objeto de la tabla 
table= dynamodb.Table(table_name)

#Hacer un scaneo completo 
response= table.scan()

#Extraer la informacion de la respuesta
data= response['Items']

#convertir los datos en una tabla de dynamo
pf = pd.DataFrame(data)

print(df)

