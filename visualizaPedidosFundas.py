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

def editar_estado_pedido():
    st.header("Editar Estado de Pedido")

    # Agregar un campo para ingresar el idPedido
    id_pedido_editar = st.text_input("Ingrese el ID del pedido del que desea editar el estado:")

    if id_pedido_editar:
        # Descargar el archivo CSV desde S3 y cargarlo en un DataFrame
        csv_file_key = 'pedidos.csv'
        response = s3.get_object(Bucket=bucket_name, Key=csv_file_key)
        pedidos_df = pd.read_csv(response['Body'])

        # Filtrar el DataFrame para obtener el pedido específico por ID
        pedidos_editar_df = pedidos_df[pedidos_df['idPedido'] == int(id_pedido_editar)]

        if not pedidos_editar_df.empty:
            # Mostrar campo para editar el estado
            nuevo_estado = st.selectbox("Nuevo valor para Estado:", ["Señado", "Pedido", "Avisado", "Entregado", "Cancelado"], index=0)
            pedidos_editar_df.loc[pedidos_editar_df.index[0], 'estado'] = nuevo_estado  # Cambiado 'Estado' a 'estado'

            # Botón para guardar los cambios
            if st.button("Guardar cambios"):
                # Actualizar el DataFrame original con los cambios realizados
                pedidos_df.update(pedidos_editar_df)

                # Guardar el DataFrame actualizado en S3
                with io.StringIO() as csv_buffer:
                    pedidos_df.to_csv(csv_buffer, index=False)
                    s3.put_object(Body=csv_buffer.getvalue(), Bucket=bucket_name, Key=csv_file_key)

                st.success("¡Estado del pedido actualizado correctamente!")

        else:
            st.warning(f"No se encontró ningun pedido con el ID {id_pedido_editar}")

def editar_pedido():
    st.header("Editar Pedido")

    # Agregar un campo para ingresar el idVenta
    id_pedido_editar = st.text_input("Ingrese el ID del pedido que desea editar:")

    if id_pedido_editar:
        # Descargar el archivo CSV desde S3 y cargarlo en un DataFrame
        csv_file_key = 'pedidos.csv'
        response = s3.get_object(Bucket=bucket_name, Key=csv_file_key)
        pedidos_df = pd.read_csv(response['Body'])

        # Filtrar el DataFrame para obtener la venta específica por ID
        pedidos_editar_df = pedidos_df[pedidos_df['idPedido'] == int(id_pedido_editar)]

        # Verificar si el usuario es admin
        if st.session_state.user_rol == "admin":
            if not pedidos_editar_df.empty:
                # Mostrar la información actual de la venta
                st.write("Información actual de la venta:")
                st.dataframe(pedidos_editar_df)

                # Mostrar campos para editar cada variable
                for column in pedidos_editar_df.columns:
                    nuevo_valor = st.text_input(f"Nuevo valor para {column}", value=pedidos_editar_df.iloc[0][column])
                    pedidos_editar_df.at[pedidos_editar_df.index[0], column] = nuevo_valor

                # Botón para guardar los cambios
                if st.button("Guardar cambios"):
                    # Actualizar el DataFrame original con los cambios realizados
                    pedidos_df.update(pedidos_editar_df)

                    # Guardar el DataFrame actualizado en S3
                    with io.StringIO() as csv_buffer:
                        pedidos_df.to_csv(csv_buffer, index=False)
                        s3.put_object(Body=csv_buffer.getvalue(), Bucket=bucket_name, Key=csv_file_key)

                    st.success("¡Pedido actualizado correctamente!")

            else:
                st.warning(f"No se encontró ningun pedido con el ID {id_pedido_editar}")
        else:
            st.warning("No tienes permisos para editar pedidos.")

def visualiza_pedidos_fundas():
    st.title("Pedidos de Fundas")

    # Cargar el archivo pedidosFundas.csv desde S3
    s3_csv_key = 'pedidos.csv'
    csv_obj = s3.get_object(Bucket=bucket_name, Key=s3_csv_key)
    pedidos_df = pd.read_csv(csv_obj['Body'])

    # Cambiar los nombres de las columnas
    pedidos_df.columns = ["ID", "Fecha", "Pedido", "Nombre del Cliente", "Contacto", "Estado", "Monto Seña", "Nombre de Usuario"]

    # Convertir la columna "Contacto" a tipo cadena y eliminar las comas
    pedidos_df['Contacto'] = pedidos_df['Contacto'].astype(str).str.replace(',', '')

    # Convertir la columna "Monto Seña" a tipo cadena y eliminar las comas
    pedidos_df['Monto Seña'] = pedidos_df['Monto Seña'].astype(str).str.replace(',', '')

    # Agregar un filtro por estado
    estados = pedidos_df['Estado'].unique()
    filtro_estado = st.selectbox("Filtrar por Estado:", ["Todos"] + list(estados))

    if filtro_estado != "Todos":
        pedidos_df = pedidos_df[pedidos_df['Estado'] == filtro_estado]

    # Ordenar el DataFrame por 'idVenta' en orden descendente
    pedidos_df = pedidos_df.sort_values(by='ID', ascending=False)

    # Convertir la columna "ID" a tipo cadena y eliminar las comas
    pedidos_df['ID'] = pedidos_df['ID'].astype(str).str.replace(',', '')

    # Mostrar la tabla de pedidos de fundas
    st.dataframe(pedidos_df)

def main():
    visualiza_pedidos_fundas()

    editar_estado_pedido()

    # Verificar si el usuario es admin
    if st.session_state.user_rol == "admin":
        editar_pedido()

if __name__ == "__main__":
    main()