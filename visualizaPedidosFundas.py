import streamlit as st
import pandas as pd
import json
import boto3
import os
import io
import datetime
from config import cargar_configuracion

# Obtener credenciales
aws_access_key, aws_secret_key, region_name, bucket_name = cargar_configuracion()

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

    # Agregar un campo para ingresar el idPedido
    id_pedido_editar = st.text_input("Ingrese el ID del pedido que desea editar:")

    if id_pedido_editar:
        # Descargar el archivo CSV desde S3 y cargarlo en un DataFrame
        csv_file_key = 'pedidos.csv'
        csv_obj = s3.get_object(Bucket=bucket_name, Key=csv_file_key)
        pedidos_df = pd.read_csv(io.BytesIO(csv_obj['Body'].read()), dtype={'contacto': str, 'idPedido': int, 'montoSeña': int}).applymap(lambda x: str(x).replace(',', '') if pd.notna(x) else x)

        # Filtrar el DataFrame para obtener el pedido específico por ID
        pedido_editar_df = pedidos_df[pedidos_df['idPedido'].astype(str) == str(id_pedido_editar)]

        # Verificar si el usuario es admin o si la edición es del día actual
        if st.session_state.user_rol == "admin":
            if not pedido_editar_df.empty:
                # Mostrar la información actual del pedido
                st.write("Información actual del pedido:")
                st.dataframe(pedido_editar_df)

                # Mostrar campos para editar cada variable
                for column in pedido_editar_df.columns:
                    # No permitir editar idPedido
                    if column not in ['idPedido']:
                        if column == "estado":
                            nuevo_valor = st.selectbox(f"Nuevo valor para {column}", ["Señado", "Sin Seña", "Pedido", "Avisado", "Entregado", "Cancelado"], index=["Señado", "Sin Seña", "Pedido", "Avisado", "Entregado", "Cancelado"].index(pedido_editar_df.iloc[0][column]))
                        else:
                            nuevo_valor = st.text_input(f"Nuevo valor para {column}", value=pedido_editar_df.iloc[0][column])
                            pedido_editar_df.at[pedido_editar_df.index[0], column] = nuevo_valor

                # Botón para guardar los cambios
                if st.button("Guardar modificacion"):
                    # Actualizar el DataFrame original con los cambios realizados
                    pedidos_df.update(pedido_editar_df)

                    # Guardar el DataFrame actualizado en S3
                    with io.StringIO() as csv_buffer:
                        pedidos_df.to_csv(csv_buffer, index=False)
                        s3.put_object(Body=csv_buffer.getvalue(), Bucket=bucket_name, Key=csv_file_key)

                    st.success("¡Pedido actualizado correctamente!")

            else:
                st.warning(f"No se encontró ningún pedido con el ID {id_pedido_editar}")

        else:
            # Verificar si la edición es del día actual
            fecha_pedido_actual = pedido_editar_df.iloc[0]['fecha']  # Asumiendo que tienes una columna llamada 'fechaPedido'
            fecha_actual = datetime.datetime.now().strftime("%Y-%m-%d")

            if fecha_pedido_actual == fecha_actual:
                # Permitir editar solo si el pedido es del día actual
                st.write("Información actual del pedido:")
                st.dataframe(pedido_editar_df)

                # Mostrar campos para editar cada variable
                for column in pedido_editar_df.columns:
                    # No permitir editar idPedido, fecha y nombreUsuario
                    if column not in ['idPedido', 'fecha', 'nombreUsuario']:
                        if column == "estado":
                            nuevo_valor = st.selectbox(f"Nuevo valor para {column}", ["Señado", "Sin Seña", "Pedido", "Avisado", "Entregado", "Cancelado"], index=["Señado", "Sin Seña", "Pedido", "Avisado", "Entregado", "Cancelado"].index(pedido_editar_df.iloc[0][column]))
                        else:
                            nuevo_valor = st.text_input(f"Nuevo valor para {column}", value=pedido_editar_df.iloc[0][column])
                            pedido_editar_df.at[pedido_editar_df.index[0], column] = nuevo_valor

                # Botón para guardar los cambios
                if st.button("Guardar modificacion"):
                    # Actualizar el DataFrame original con los cambios realizados
                    pedidos_df.update(pedido_editar_df)

                    # Guardar el DataFrame actualizado en S3
                    with io.StringIO() as csv_buffer:
                        pedidos_df.to_csv(csv_buffer, index=False)
                        s3.put_object(Body=csv_buffer.getvalue(), Bucket=bucket_name, Key=csv_file_key)

                    st.success("¡Pedido actualizado correctamente!")
            else:
                st.warning("No tienes permisos para editar pedidos que no sean del día actual.")

def visualiza_pedidos_fundas():
    st.title("""Visualizar Pedidos \n * Visualice todos los pedidos y filtre por estado \n * Edite el estado del pedido ingresando el ID correspondiente. \n * Para editar un pedido, solo para administradores, ingrese el ID del pedido, modifique los campos y presione 'Guardar cambios'.""")

    st.header("Pedidos")

    # Cargar el archivo pedidosFundas.csv desde S3
    s3_csv_key = 'pedidos.csv'
    csv_obj = s3.get_object(Bucket=bucket_name, Key=s3_csv_key)
    pedidos_df = pd.read_csv(io.BytesIO(csv_obj['Body'].read()), dtype={'contacto': str, 'idPedido': int, 'montoSeña': float}).applymap(lambda x: str(x).replace(',', '') if pd.notna(x) else x)

    # Cambiar los nombres de las columnas
    pedidos_df.columns = ["ID", "Fecha", "Pedido", "Nombre del Cliente", "Contacto", "Estado", "Monto Seña", "Nombre de Usuario"]

    # Convertir la columna "Monto Seña" a tipo cadena y eliminar las comas
    pedidos_df['Monto Seña'] = pedidos_df['Monto Seña'].astype(str).str.replace(',', '')

    # Agregar un filtro por estado
    estados = pedidos_df['Estado'].unique()
    filtro_estado = st.selectbox("Filtrar por Estado:", ["Todos"] + list(estados))

    if filtro_estado != "Todos":
        pedidos_df = pedidos_df[pedidos_df['Estado'] == filtro_estado]

    # Convertir la columna "ID" a tipo int
    pedidos_df['ID'] = pedidos_df['ID'].astype(int)

    # Ordenar el DataFrame por 'idVenta' en orden descendente
    pedidos_df = pedidos_df.sort_values(by='ID', ascending=False)

    # Convertir la columna "ID" a tipo cadena y eliminar las comas
    pedidos_df['ID'] = pedidos_df['ID'].astype(str).str.replace(',', '')

    # Mostrar la tabla de pedidos de fundas
    st.dataframe(pedidos_df)

def main():
    visualiza_pedidos_fundas()

    editar_estado_pedido()

    editar_pedido()

if __name__ == "__main__":
    main()