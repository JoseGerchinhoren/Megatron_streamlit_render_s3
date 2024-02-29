import streamlit as st
import boto3
import pandas as pd
import io
from config import cargar_configuracion
from horario import obtener_fecha_argentina

# Obtener credenciales
aws_access_key, aws_secret_key, region_name, bucket_name = cargar_configuracion()

# Conecta a S3
s3 = boto3.client('s3', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key, region_name=region_name)

def visualiza_cierre_caja():
    st.title("Cierre de Caja")

    # Descargar el archivo CSV desde S3 y cargarlo en un DataFrame
    csv_file_key = 'cierreCaja.csv'
    response = s3.get_object(Bucket=bucket_name, Key=csv_file_key)
    cierreCaja_df = pd.read_csv(io.BytesIO(response['Body'].read())).applymap(lambda x: str(x).replace(',', '') if pd.notna(x) else x)

    # Ordenar el DataFrame por 'idCierreVenta' en orden descendente
    cierreCaja_df = cierreCaja_df.sort_values(by='idCierre', ascending=False)

    # Convertir la columna "idCierre" a tipo cadena y eliminar las comas
    cierreCaja_df['idCierre'] = cierreCaja_df['idCierre'].astype(str).str.replace(',', '')

    # Mostrar la tabla de ventas
    st.dataframe(cierreCaja_df)

def main():
    visualiza_cierre_caja()  # Mostrar sección de visualización para todos los usuarios

if __name__ == "__main__":
    main()