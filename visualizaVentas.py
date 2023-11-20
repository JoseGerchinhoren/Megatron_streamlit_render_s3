import streamlit as st
import boto3
import os
import pandas as pd
import io
from datetime import datetime

#

# Conecta a S3
s3 = boto3.client('s3', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key, region_name=region_name)

def visualiza_ventas():
    st.title("Visualizar Ventas")

    # Descargar el archivo CSV desde S3 y cargarlo en un DataFrame
    csv_file_key = 'ventas.csv'  # Cambiado a minúsculas
    response = s3.get_object(Bucket=bucket_name, Key=csv_file_key)
    ventas_df = pd.read_csv(response['Body'])

    # Construir la expresión booleana en función de los filtros
    fecha_filtro = None
    if st.sidebar.checkbox("Ventas del día"):
        fecha_filtro = (datetime.today().strftime('%Y-%m-%d'), datetime.today().strftime('%Y-%m-%d'))
    elif st.sidebar.checkbox("Ventas del mes"):
        first_day_of_month = datetime.today().replace(day=1).strftime('%Y-%m-%d')
        last_day_of_month = (datetime.today().replace(day=1, month=datetime.today().month + 1) - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        fecha_filtro = (first_day_of_month, last_day_of_month)

    id_usuario = st.sidebar.text_input("Filtrar por ID de Usuario", key="id_usuario")

    # Aplicar filtros
    if fecha_filtro:
        ventas_df['fecha'] = pd.to_datetime(ventas_df['fecha'])
        ventas_df = ventas_df[(ventas_df['fecha'] >= fecha_filtro[0]) & (ventas_df['fecha'] <= fecha_filtro[1])]

    if id_usuario:
        ventas_df['idUsuario'] = ventas_df['idUsuario'].astype(int)
        ventas_df = ventas_df[ventas_df['idUsuario'] == int(id_usuario)]

    # Mostrar la tabla de ventas
    st.dataframe(ventas_df)

    # Calcular y mostrar estadísticas
    total_precios = ventas_df["precio"].sum()
    st.title(f"Total de Ventas: ${total_precios:}")

    for metodo_pago in ventas_df["metodoPago"].unique():
        total_metodo_pago = ventas_df[ventas_df["metodoPago"] == metodo_pago]["precio"].sum()
        st.write(f"Total en {metodo_pago}: ${total_metodo_pago}")

def editar_ventas():
    st.title("Editar Ventas")

    # Agregar un campo para ingresar el idVenta
    id_venta_editar = st.text_input("Ingrese el ID de la Venta que desea editar:")

    if id_venta_editar:
        # Descargar el archivo CSV desde S3 y cargarlo en un DataFrame
        csv_file_key = 'ventas.csv'  # Cambiado a minúsculas
        response = s3.get_object(Bucket=bucket_name, Key=csv_file_key)
        ventas_df = pd.read_csv(response['Body'])

        # Filtrar el DataFrame para obtener la venta específica por ID
        venta_editar_df = ventas_df[ventas_df['idVenta'] == int(id_venta_editar)]

        # Verificar si el usuario es admin
        if st.session_state.user_rol == "admin":
            if not venta_editar_df.empty:
                # Mostrar la información actual de la venta
                st.write("Información actual de la venta:")
                st.dataframe(venta_editar_df)

                # Mostrar campos para editar cada variable
                for column in venta_editar_df.columns:
                    nuevo_valor = st.text_input(f"Nuevo valor para {column}", value=venta_editar_df.iloc[0][column])
                    venta_editar_df.at[venta_editar_df.index[0], column] = nuevo_valor

                # Botón para guardar los cambios
                if st.button("Guardar cambios"):
                    # Guardar el DataFrame actualizado en S3
                    with io.StringIO() as csv_buffer:
                        ventas_df.to_csv(csv_buffer, index=False)
                        s3.put_object(Body=csv_buffer.getvalue(), Bucket=bucket_name, Key=csv_file_key)

                    st.success("¡Venta actualizada correctamente!")

            else:
                st.warning(f"No se encontró ninguna venta con el ID {id_venta_editar}")
        
        if not st.session_state.user_rol == "admin":
            if not venta_editar_df.empty:
                # Mostrar la información actual de la venta
                st.write("Campos que puede modificar:")
                st.dataframe(venta_editar_df)

                # Mostrar campos para editar cada variable
                for column in venta_editar_df.columns:
                    nuevo_valor = st.text_input(f"Nuevo valor para {column}", value=venta_editar_df.iloc[0][column])
                    venta_editar_df.at[venta_editar_df.index[0], column] = nuevo_valor

                # Botón para guardar los cambios
                if st.button("Guardar cambios"):
                    # Guardar el DataFrame actualizado en S3
                    with io.StringIO() as csv_buffer:
                        ventas_df.to_csv(csv_buffer, index=False)
                        s3.put_object(Body=csv_buffer.getvalue(), Bucket=bucket_name, Key=csv_file_key)

                    st.success("¡Venta actualizada correctamente!")

            else:
                st.warning(f"No se encontró ninguna venta con el ID {id_venta_editar}")

def main():
    visualiza_ventas()  # Mostrar sección de visualización para todos los usuarios

    editar_ventas()  # Mostrar sección de edición solo para admin

if __name__ == "__main__":
    main()
