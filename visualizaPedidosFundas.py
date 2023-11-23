import streamlit as st
import pyodbc
import pandas as pd
import json
import boto3
import os
import io

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

def editar_estado_pedido_funda(pedidos_df, id_pedido_funda, nuevo_estado):
    try:
        # Verificar si el ID del Pedido de Funda existe
        if id_pedido_funda not in pedidos_df['ID'].values:
            st.warning(f"El ID del Pedido de Funda {id_pedido_funda} no existe.")
            return

        # Actualizar el estado del Pedido de Funda en el DataFrame
        pedidos_df.loc[pedidos_df['ID'] == id_pedido_funda, 'Estado'] = nuevo_estado

        # Guardar el DataFrame modificado en S3
        s3_csv_key = 'pedidosFundas.csv'
        csv_buffer = io.StringIO()
        pedidos_df.to_csv(csv_buffer, index=False)
        s3.put_object(Body=csv_buffer.getvalue(), Bucket=bucket_name, Key=s3_csv_key)

        st.success(f"Estado del Pedido de Funda {id_pedido_funda} editado correctamente a: {nuevo_estado}")

    except Exception as e:
        st.error(f"Error al editar el estado del Pedido de Funda: {e}")

def visualiza_pedidos_fundas():
    st.title("Visualizar Pedidos de Fundas")

    # Cargar el archivo pedidosFundas.csv desde S3
    s3_csv_key = 'pedidosFundas.csv'
    csv_obj = s3.get_object(Bucket=bucket_name, Key=s3_csv_key)
    pedidos_df = pd.read_csv(csv_obj['Body'])

    # Imprimir la forma del DataFrame
    st.write(f"Forma del DataFrame: {pedidos_df.shape}")

    # Cambiar los nombres de las columnas
    pedidos_df.columns = ["ID", "Fecha", "Pedido", "Nombre del Cliente", "Contacto", "Estado", "Monto Seña", "Nombre de Usuario"]

    # Agregar un filtro por estado
    estados = pedidos_df['Estado'].unique()
    filtro_estado = st.selectbox("Filtrar por Estado:", ["Todos"] + list(estados))

    if filtro_estado != "Todos":
        pedidos_df = pedidos_df[pedidos_df['Estado'] == filtro_estado]

    # Mostrar la tabla de pedidos de fundas
    st.dataframe(pedidos_df)

    # Sección para la edición del estado de registros
    st.subheader("Editar Estado")
    id_pedido_funda = st.number_input("Ingrese el ID del Pedido de Funda que desea editar:", value=0)
    nuevo_estado = st.selectbox("Nuevo valor del campo estado:", ["Señado", "Pedido", "Avisado","Entregado", "Cancelado"])

    if st.button("Guardar"):
        editar_estado_pedido_funda(pedidos_df, id_pedido_funda, nuevo_estado)

def main():
    visualiza_pedidos_fundas()

if __name__ == "__main__":
    main()