import streamlit as st
import boto3
import pandas as pd
import io
import json
from datetime import datetime
import os

# Cargar configuración desde el archivo config.json
with open("../config.json") as config_file:
    config = json.load(config_file)

# Desempaquetar las credenciales desde el archivo de configuración
aws_access_key = config["aws_access_key"]
aws_secret_key = config["aws_secret_key"]
region_name = config["region_name"]
bucket_name = config["bucket_name"]

# # Configura tus credenciales y la región de AWS desde variables de entorno
# aws_access_key = os.getenv('aws_access_key_id')
# aws_secret_key = os.getenv('aws_secret_access_key')
# region_name = os.getenv('aws_region')
# bucket_name = 'megatron-accesorios'

# Conecta a S3
s3 = boto3.client('s3', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key, region_name=region_name)

# Función para insertar una venta en la base de datos
def insertar_venta(fecha, producto, precio, metodo_pago, nombre_usuario):
    try:
        # Leer el archivo CSV desde S3
        csv_file_key = 'ventas.csv'
        response = s3.get_object(Bucket=bucket_name, Key=csv_file_key)
        ventas_df = pd.read_csv(io.BytesIO(response['Body'].read()))

        # Forzar el tipo de dato de la columna 'precio' a enteros
        ventas_df['precio'] = ventas_df['precio'].astype(int, errors='ignore')

        # Obtener el último idVenta
        ultimo_id = ventas_df['idVenta'].max()

        # Si no hay registros, asignar 1 como idVenta, de lo contrario, incrementar el último idVenta
        nuevo_id = 1 if pd.isna(ultimo_id) else int(ultimo_id) + 1

        # Convertir la fecha a formato string (solo la parte de la fecha)
        fecha_str = fecha.strftime("%Y-%m-%d") if hasattr(fecha, 'strftime') else fecha

        # Crear una nueva fila como un diccionario
        nueva_fila = {'idVenta': nuevo_id, 'fecha': fecha_str, 'productoVendido': producto, 'precio': precio, 'metodoPago': metodo_pago, 'nombreUsuario': nombre_usuario}

        # Convertir el diccionario a DataFrame y concatenarlo al DataFrame existente
        ventas_df = pd.concat([ventas_df, pd.DataFrame([nueva_fila])], ignore_index=True)

        # Guardar el DataFrame actualizado de nuevo en S3
        with io.StringIO() as csv_buffer:
            ventas_df.to_csv(csv_buffer, index=False)
            s3.put_object(Body=csv_buffer.getvalue(), Bucket=bucket_name, Key=csv_file_key)

        st.success("Venta registrada exitosamente")

    except Exception as e:
        st.error(f"Error al registrar la venta: {e}")
        
def venta(nombre_usuario):
    st.title("""Registrar Venta \n * Ingrese el nombre del producto, el precio en números enteros y seleccione el método de pago.\n * Presione 'Registrar Venta' para guardar la información de la nueva venta.""")

    # Campos para ingresar los datos de la venta
    if st.session_state.user_rol == "admin":
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
        if st.session_state.user_rol == "admin":
            if fecha and producto and precio > 0 and metodo_pago:
                insertar_venta(fecha, producto, precio, metodo_pago, nombre_usuario)
            else:
                st.warning("Por favor, complete todos los campos.")
        else:
            if producto and precio > 0 and metodo_pago:
                insertar_venta(datetime.now(), producto, precio, metodo_pago, nombre_usuario)
            else:
                st.warning("Por favor, complete todos los campos.")

if __name__ == "__main__":
    venta()