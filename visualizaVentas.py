import streamlit as st
import boto3
import os
import pandas as pd
import io
from datetime import datetime, timedelta
import json

# # Cargar configuración desde el archivo config.json
# with open("../config.json") as config_file:
#     config = json.load(config_file)

# # Desempaquetar las credenciales desde el archivo de configuración
# aws_access_key = config["aws_access_key"]
# aws_secret_key = config["aws_secret_key"]
# region_name = config["region_name"]
# bucket_name = config["bucket_name"]

# Configura tus credenciales y la región de AWS desde variables de entorno
aws_access_key = os.getenv('aws_access_key_id')
aws_secret_key = os.getenv('aws_secret_access_key')
region_name = os.getenv('aws_region')
bucket_name = 'megatron-accesorios'

# Conecta a S3
s3 = boto3.client('s3', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key, region_name=region_name)

def visualiza_ventas():
    st.title("""Visualizar Ventas\n * Por defecto se muestran las ventas del día, para ver todas las ventas quite el filtro en el menu de la izquierda. \n * Para aplicar filtros adicionales, despliegue el menú de la izquierda. Puede filtrar por rango de fechas o por nombre de usuario. \n * Para editar las ventas ingrese el ID correspondiente y modifique los campos deseados. Luego, presione 'Guardar cambios'. Los usuarios sin permisos de administrador solo pueden editar las vetas del día actual.""")

    st.header("Ventas")

    # Descargar el archivo CSV desde S3 y cargarlo en un DataFrame
    csv_file_key = 'ventas.csv'  # Cambiado a minúsculas
    response = s3.get_object(Bucket=bucket_name, Key=csv_file_key)
    ventas_df = pd.read_csv(io.BytesIO(response['Body'].read()), dtype={'idVenta': int, 'precio': int}).applymap(lambda x: str(x).replace(',', '') if pd.notna(x) else x)

    # Renombrar columnas y cambiar el orden
    ventas_df.rename(columns={'idVenta': 'ID', 'fecha': 'Fecha', 'productoVendido': 'Producto Vendido', 'precio': 'Precio', 'metodoPago': 'Método de Pago', 'nombreUsuario': 'Nombre de Usuario'}, inplace=True)

    # Convertir la columna "Precio" a tipo cadena y eliminar las comas
    ventas_df['Precio'] = ventas_df['Precio'].astype(str).str.replace(',', '')

    # Filtros
    st.sidebar.header("Filtrar por Rango de Fechas")
    aplicar_filtro_rango_fechas = st.sidebar.checkbox("Aplicar filtro de rango de fechas", key="filtro_rango_fechas")

    if aplicar_filtro_rango_fechas:
        fecha_inicio = st.sidebar.date_input("Fecha de Inicio", datetime.today().replace(day=1))
        fecha_fin = st.sidebar.date_input("Fecha de Fin", datetime.today())
        rango_fechas_filtro = (fecha_inicio.strftime('%Y-%m-%d'), fecha_fin.strftime('%Y-%m-%d'))
        ventas_df['Fecha'] = pd.to_datetime(ventas_df['Fecha'])
        ventas_df = ventas_df[(ventas_df['Fecha'] >= rango_fechas_filtro[0]) & (ventas_df['Fecha'] <= rango_fechas_filtro[1])]

    # Aplicar los filtros
    fecha_filtro = None
    st.sidebar.header("Filtro de Ventas del dia")

    # Utilizar el argumento value para activar el checkbox por defecto
    if st.sidebar.checkbox("Aplicar Filtro de Ventas del día", value=True):
        fecha_seleccionada = st.sidebar.date_input("Seleccione la fecha", datetime.today())
        fecha_filtro = (fecha_seleccionada.strftime('%Y-%m-%d'), fecha_seleccionada.strftime('%Y-%m-%d'))

    st.sidebar.header("Filtrar por nombre de Usuario")
    nombre_usuario = st.sidebar.text_input("Nombre de Usuario", key="nombre_usuario")

    # Aplicar filtros
    if fecha_filtro:
        ventas_df['Fecha'] = pd.to_datetime(ventas_df['Fecha'])
        ventas_df = ventas_df[(ventas_df['Fecha'] >= fecha_filtro[0]) & (ventas_df['Fecha'] <= fecha_filtro[1])]

    if nombre_usuario:
        ventas_df = ventas_df[ventas_df['Nombre de Usuario'] == nombre_usuario]

    # Asegurarse de que la columna 'Fecha' sea de tipo datetime
    ventas_df['Fecha'] = pd.to_datetime(ventas_df['Fecha'])

    # Formatear las fechas antes de mostrar el DataFrame
    ventas_df['Fecha'] = ventas_df['Fecha'].dt.strftime('%Y-%m-%d')

    # Convertir la columna "ID" a tipo int
    ventas_df['ID'] = ventas_df['ID'].astype(int)

    # Ordenar el DataFrame por 'idVenta' en orden descendente
    ventas_df = ventas_df.sort_values(by='ID', ascending=False)

    # Convertir la columna "ID" a tipo cadena y eliminar las comas
    ventas_df['ID'] = ventas_df['ID'].astype(str).str.replace(',', '')

    # Mostrar la tabla de ventas
    st.dataframe(ventas_df)

    # Convertir la columna "Precio" a tipo numérico
    ventas_df['Precio'] = pd.to_numeric(ventas_df['Precio'], errors='coerce')

    # Verificar si se han aplicado filtros antes de mostrar estadísticas
    if aplicar_filtro_rango_fechas or fecha_filtro or nombre_usuario:
        # Calcular y mostrar estadísticas
        total_precios = int(ventas_df["Precio"].sum())  # Convertir a número entero
        st.subheader(f"Total de Ventas: ${total_precios}")

        for metodo_pago in ventas_df["Método de Pago"].unique():
            total_metodo_pago = ventas_df[ventas_df["Método de Pago"] == metodo_pago]["Precio"].sum()
            st.write(f"Total en {metodo_pago}: ${int(total_metodo_pago)}")  # Convertir a número entero

def editar_ventas():
    st.header("Editar Ventas")

    # Agregar un campo para ingresar el idVenta
    id_venta_editar = st.text_input("Ingrese el ID de la Venta que desea editar:")

    if id_venta_editar:
        # Descargar el archivo CSV desde S3 y cargarlo en un DataFrame
        csv_file_key = 'ventas.csv'  # Cambiado a minúsculas
        response = s3.get_object(Bucket=bucket_name, Key=csv_file_key)
        ventas_df = pd.read_csv(io.BytesIO(response['Body'].read()), dtype={'idVenta': int, 'precio': int}).applymap(lambda x: str(x).replace(',', '') if pd.notna(x) else x)

        # Filtrar el DataFrame para obtener el pedido específico por ID
        venta_editar_df = ventas_df[ventas_df['idVenta'].astype(str) == str(id_venta_editar)]

        # Verificar si el usuario es admin
        if st.session_state.user_rol == "admin":
            if not venta_editar_df.empty:
                # Mostrar la información actual de la venta
                st.write("Información actual de la venta:")
                st.dataframe(venta_editar_df)

                # Mostrar campos para editar cada variable
                for column in venta_editar_df.columns:
                    if column != 'idVenta' and column != 'nombreUsuario' and column != 'fecha':
                        valor_actual = venta_editar_df.iloc[0][column]
                        
                        if column == "metodoPago":
                            opciones_metodo_pago = ["Efectivo", "Transferencia", "Tarjeta de Crédito", "Tarjeta de Débito", "Otro"]
                            index_actual = opciones_metodo_pago.index(valor_actual) if valor_actual in opciones_metodo_pago else 0
                            nuevo_valor = st.selectbox(f"Nuevo valor para {column}", opciones_metodo_pago, index=index_actual)
                        else:
                            nuevo_valor = st.text_input(f"Nuevo valor para {column}", value=valor_actual) if valor_actual is not None else st.text_input(f"Nuevo valor para {column}")

                        venta_editar_df.at[venta_editar_df.index[0], column] = nuevo_valor


                # Botón para guardar los cambios
                if st.button("Guardar modificacion"):
                    # Actualizar el DataFrame original con los cambios realizados
                    ventas_df.update(venta_editar_df)

                    # Guardar el DataFrame actualizado en S3
                    with io.StringIO() as csv_buffer:
                        ventas_df.to_csv(csv_buffer, index=False)
                        s3.put_object(Body=csv_buffer.getvalue(), Bucket=bucket_name, Key=csv_file_key)

                    st.success("¡Venta actualizada correctamente!")

            else:
                st.warning(f"No se encontró ninguna venta con el ID {id_venta_editar}")
        else:
            # Verificar si la venta se realizó en el día actual
            fecha_venta_actual = venta_editar_df.iloc[0]['fecha']  # Asumiendo que tienes una columna llamada 'fechaVenta'
            fecha_actual = datetime.now().strftime("%Y-%m-%d")

            if fecha_venta_actual == fecha_actual:
                # Permitir editar solo si la venta es del día actual
                st.write("Información actual de la venta:")
                st.dataframe(venta_editar_df)

                # Mostrar campos para editar cada variable
                for column in venta_editar_df.columns:
                    if column != 'idVenta' and column != 'nombreUsuario' and column != 'fecha':
                        if column == "metodoPago":
                            nuevo_valor = st.selectbox(f"Nuevo valor para {column}", ["Efectivo", "Transferencia", "Tarjeta de Crédito", "Tarjeta de Débito", "Otro"], index=["Efectivo", "Transferencia", "Tarjeta de Crédito", "Tarjeta de Débito", "Otro"].index(venta_editar_df.iloc[0][column]))
                        else:
                            nuevo_valor = st.text_input(f"Nuevo valor para {column}", value=venta_editar_df.iloc[0][column])

                        venta_editar_df.at[venta_editar_df.index[0], column] = nuevo_valor

                # Botón para guardar los cambios
                if st.button("Guardar modificacion"):
                    # Actualizar el DataFrame original con los cambios realizados
                    ventas_df.update(venta_editar_df)

                    # Guardar el DataFrame actualizado en S3
                    with io.StringIO() as csv_buffer:
                        ventas_df.to_csv(csv_buffer, index=False)
                        s3.put_object(Body=csv_buffer.getvalue(), Bucket=bucket_name, Key=csv_file_key)

                    st.success("¡Venta actualizada correctamente!")
            else:
                st.warning("No tienes permisos para editar ventas que no sean del día actual.")

def main():
    visualiza_ventas()  # Mostrar sección de visualización para todos los usuarios

    editar_ventas()

if __name__ == "__main__":
    main()