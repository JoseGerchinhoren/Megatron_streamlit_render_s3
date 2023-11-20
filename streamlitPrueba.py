import os
import streamlit as st
import pandas as pd
import boto3
from io import StringIO

# Configura tus credenciales y la región de AWS desde variables de entorno
aws_access_key = os.getenv('aws_access_key_id')
aws_secret_key = os.getenv('aws_secret_access_key')
region_name = os.getenv('aws_region')
bucket_name = 'megatron-ventas'
csv_file_key = 'usuarios.csv'  # Nombre del archivo CSV en S3

# Conecta a S3
s3 = boto3.client('s3', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key, region_name=region_name)

# Función para escribir datos en el archivo CSV en S3
def escribir_en_s3(data):
    csv_data = StringIO()
    data.to_csv(csv_data, index=False)
    s3.put_object(Bucket=bucket_name, Key=csv_file_key, Body=csv_data.getvalue())

# Función para leer datos desde el archivo CSV en S3
def leer_desde_s3():
    response = s3.get_object(Bucket=bucket_name, Key=csv_file_key)
    data = pd.read_csv(response['Body'])
    return data

# Título de la aplicación Streamlit
st.title("Streamlit con S3 - Ejemplo de Escritura y Lectura de CSV")

# Sección para escribir datos en S3
st.header("Escribir Datos en S3")

# Ejemplo de datos para escribir en S3
datos_para_escribir = pd.DataFrame({
    'ID': [1, 2, 3],
    'Nombre': ['Usuario1', 'Usuario2', 'Usuario3'],
    'Edad': [25, 30, 24]
})

# Botón para escribir datos en S3
if st.button("Escribir Datos en S3"):
    escribir_en_s3(datos_para_escribir)
    st.success("Datos escritos exitosamente en S3!")

# Sección para leer datos desde S3
st.header("Leer Datos desde S3")

# Botón para leer datos desde S3
if st.button("Leer Datos desde S3"):
    datos_leidos = leer_desde_s3()
    st.write("Datos Leídos desde S3:")
    st.write(datos_leidos)
