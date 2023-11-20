import streamlit as st
import boto3
import os
import pandas as pd
import io
import json
from datetime import datetime

#

# Conecta a S3
s3 = boto3.client('s3', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key, region_name=region_name)

# Función para insertar una venta en la base de datos
def insertar_venta(fecha, producto, precio, metodo_pago, id_usuario):
    try:
        # Leer el archivo CSV desde S3
        csv_file_key = 'ventas.csv'
        response = s3.get_object(Bucket=bucket_name, Key=csv_file_key)
        ventas_df = pd.read_csv(io.BytesIO(response['Body'].read()))

        # Obtener el último idVenta
        ultimo_id = ventas_df['idVenta'].max()

        # Si no hay registros, asignar 1 como idVenta, de lo contrario, incrementar el último idVenta
        nuevo_id = 1 if pd.isna(ultimo_id) else int(ultimo_id) + 1

        # Crear una nueva fila como un diccionario
        nueva_fila = {'idVenta': nuevo_id, 'fecha': fecha, 'productoVendido': producto, 'precio': precio, 'metodoPago': metodo_pago, 'idUsuario': id_usuario}

        # Convertir el diccionario a DataFrame y concatenarlo al DataFrame existente
        ventas_df = pd.concat([ventas_df, pd.DataFrame([nueva_fila])], ignore_index=True)

        # Guardar el DataFrame actualizado de nuevo en S3
        with io.StringIO() as csv_buffer:
            ventas_df.to_csv(csv_buffer, index=False)
            s3.put_object(Body=csv_buffer.getvalue(), Bucket=bucket_name, Key=csv_file_key)

        st.success("Venta registrada exitosamente")

    except Exception as e:
        st.error(f"Error al registrar la venta: {e}")

def venta(id_usuario):
    
    st.title("Registrar Venta")

    # Campos para ingresar los datos de la venta
    fecha = st.date_input("Fecha de la venta:")
    producto = st.text_input("Producto vendido:")
    precio = st.text_input("Precio:")
    if precio:
        if precio.isdigit():
            precio = int(precio)
        else:
            st.warning("El precio debe ser un número entero.")
            precio = None
    else:
        precio = None
    metodo_pago = st.selectbox("Método de pago:", ["Efectivo", "Transferencia", "Tarjeta de Crédito", "Tarjeta de Débito", "Otro"])

    # Botón para registrar la venta
    if st.button("Registrar Venta"):
        if fecha and producto and precio is not None and metodo_pago:
            insertar_venta(fecha, producto, precio, metodo_pago, id_usuario)
        else:
            st.warning("Por favor, complete todos los campos.")

if __name__ == "__main__":
    venta(1)
