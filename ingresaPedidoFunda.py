import streamlit as st
import boto3
import io
import pandas as pd
from config import cargar_configuracion
from horario import obtener_fecha_argentina

# Obtener credenciales
aws_access_key, aws_secret_key, region_name, bucket_name = cargar_configuracion()

# Conecta a S3
s3 = boto3.client('s3', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key, region_name=region_name)

# Función para insertar un pedido en la base de datos
def insertar_pedido(pedido, nombreCliente, contacto, estado, montoSeña, nombre_usuario):
    try:
        # Leer el archivo CSV desde S3
        csv_file_key = 'pedidos.csv'
        response = s3.get_object(Bucket=bucket_name, Key=csv_file_key)
        pedidos_df = pd.read_csv(io.BytesIO(response['Body'].read()))

        # Obtener el último idPedido
        ultimo_id = pedidos_df['idPedido'].max()

        # Si no hay registros, asignar 1 como idPedido, de lo contrario, incrementar el último idPedido
        nuevo_id = 1 if pd.isna(ultimo_id) else int(ultimo_id) + 1

        # Obtener la fecha actual en Argentina
        fecha_actual_argentina = obtener_fecha_argentina()
        fecha_str = fecha_actual_argentina.strftime("%Y-%m-%d")

        # Crear una nueva fila como un diccionario
        nueva_fila = {'idPedido': nuevo_id, 'fecha': fecha_str, 'pedido': pedido, 'nombreCliente': nombreCliente, 'contacto': contacto, 'estado': estado, 'montoSeña': montoSeña, 'nombreUsuario': nombre_usuario}

        # Convertir el diccionario a DataFrame y concatenarlo al DataFrame existente
        pedidos_df = pd.concat([pedidos_df, pd.DataFrame([nueva_fila])], ignore_index=True)

        # Guardar el DataFrame actualizado de nuevo en S3
        with io.StringIO() as csv_buffer:
            pedidos_df.to_csv(csv_buffer, index=False)
            s3.put_object(Body=csv_buffer.getvalue(), Bucket=bucket_name, Key=csv_file_key)

        st.success("Pedido registrado exitosamente")

    except Exception as e:
        st.error(f"Error al registrar el pedido: {e}")

def ingresaPedidoFunda(nombre_usuario):
    st.title("""Nuevo Pedido \n * Ingrese la descripción del pedido, el nombre del cliente, un numero o email de contacto y seleccione el estado del pedido. \n * Si el estado es 'Señado', ingrese el monto de la seña.""")

    # Campos para ingresar los datos del pedido de funda
    pedido = st.text_input("Pedido:")
    nombreCliente = st.text_input("Nombre del Cliente:")
    contacto = st.text_input("Contacto:")
    estado = st.selectbox("Estado:", ["Señado", "Sin Seña", "Pedido", "Avisado", "Entregado", "Cancelado"])

    # Campo adicional para el monto de señal si el estado es "Señado"
    monto_sena = None
    if estado == "Señado":
        monto_sena = st.text_input("Monto de seña:")
    if monto_sena:
        if monto_sena.isdigit():
            monto_sena = int(monto_sena)
        else:
            st.warning("El monto debe ser un número entero.")
            monto_sena = None
    else:
        monto_sena = None

    # Botón para registrar el pedido de funda
    if st.button("Registrar Pedido"):
        if pedido and nombreCliente and contacto and estado:
            insertar_pedido(pedido, nombreCliente, contacto, estado, monto_sena, nombre_usuario)
        else:
            st.warning("Por favor, complete todos los campos.")

if __name__ == "__main__":
    ingresaPedidoFunda()
