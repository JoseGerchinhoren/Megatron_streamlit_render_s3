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

def visualiza_ventas():
    st.title("Visualizar Ventas")

    # Descargar el archivo CSV desde S3 y cargarlo en un DataFrame
    csv_file_key = 'ventas.csv'
    response = s3.get_object(Bucket=bucket_name, Key=csv_file_key)
    ventas_df = pd.read_csv(io.BytesIO(response['Body'].read())).applymap(lambda x: str(x).replace(',', '') if pd.notna(x) else x)

    # Renombrar columnas y cambiar el orden
    ventas_df.rename(columns={'idVenta': 'ID', 'fecha': 'Fecha', 'productoVendido': 'Producto Vendido', 'precio': 'Precio', 'metodoPago': 'Método de Pago', 'nombreUsuario': 'Nombre de Usuario'}, inplace=True)

    # Convertir la columna "Precio" a tipo cadena y eliminar las comas
    ventas_df['Precio'] = ventas_df['Precio'].astype(str).str.replace(',', '')

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

    # Filtros en el sidebar
    with st.sidebar:
        st.subheader("Filtrar por Rango de Fechas")
        aplicar_filtro_rango_fechas = st.checkbox("Aplicar filtro de rango de fechas", key="filtro_rango_fechas")

        fecha_filtro = None
        if aplicar_filtro_rango_fechas:
            fecha_inicio = st.date_input("Fecha de Inicio", obtener_fecha_argentina().replace(day=1))
            fecha_fin = st.date_input("Fecha de Fin", obtener_fecha_argentina())
            rango_fechas_filtro = (fecha_inicio.strftime('%Y-%m-%d'), fecha_fin.strftime('%Y-%m-%d'))
            ventas_df = ventas_df[(ventas_df['Fecha'] >= rango_fechas_filtro[0]) & (ventas_df['Fecha'] <= rango_fechas_filtro[1])]

        st.subheader("Filtro de Ventas del día")

        # Utilizar el argumento value para activar el checkbox por defecto
        aplicar_filtro_ventas_dia = st.checkbox("Aplicar Filtro de Ventas del día", value=True)

        if aplicar_filtro_ventas_dia:
            fecha_seleccionada = st.date_input("Seleccione la fecha", obtener_fecha_argentina())
            fecha_filtro = (fecha_seleccionada.strftime('%Y-%m-%d'), fecha_seleccionada.strftime('%Y-%m-%d'))

        if fecha_filtro:
            ventas_df = ventas_df[(ventas_df['Fecha'] >= fecha_filtro[0]) & (ventas_df['Fecha'] <= fecha_filtro[1])]

        st.subheader("Filtrar por nombre de Usuario")

        # Filtrar por nombre de Usuario
        nombres_usuarios = ventas_df['Nombre de Usuario'].unique().tolist()
        nombre_usuario_seleccionado = st.selectbox("Filtrar por nombre de Usuario", [""] + nombres_usuarios)

        if nombre_usuario_seleccionado:
            ventas_df = ventas_df[ventas_df['Nombre de Usuario'] == nombre_usuario_seleccionado]

    # Mostrar la tabla de ventas
    st.dataframe(ventas_df)

    # Convertir la columna "Precio" a tipo numérico
    ventas_df['Precio'] = pd.to_numeric(ventas_df['Precio'], errors='coerce')

    # Verificar si se han aplicado filtros antes de mostrar estadísticas
    if aplicar_filtro_rango_fechas or fecha_filtro or nombre_usuario_seleccionado:
        # Calcular y mostrar estadísticas
        total_precios = int(ventas_df["Precio"].sum())  # Convertir a número entero
        st.header(f"Total de Ventas: ${total_precios}")

        # Sumar las ventas por método de pago
        ventas_tarjeta = int(ventas_df[(ventas_df["Método de Pago"] == "Tarjeta de Crédito") | (ventas_df["Método de Pago"] == "Tarjeta de Débito") | (ventas_df["Método de Pago"] == "Codigo QR")]["Precio"].sum())  # Convertir a número entero
        ventas_transferencias = int(ventas_df[ventas_df["Método de Pago"] == "Transferencia"]["Precio"].sum())  # Convertir a número entero
        ventas_efectivo = int(ventas_df[ventas_df["Método de Pago"] == "Efectivo"]["Precio"].sum())  # Convertir a número entero
        ventas_otros = int(ventas_df[ventas_df["Método de Pago"] == "Otro"]["Precio"].sum())  # Convertir a número entero

        st.subheader(f"Efectivo: ${ventas_efectivo}")
        st.subheader(f"Tarjeta: ${ventas_tarjeta}")
        st.write(f"Tarjeta de Crédito: ${int(ventas_df[ventas_df['Método de Pago'] == 'Tarjeta de Crédito']['Precio'].sum())}")  # Convertir a número entero
        st.write(f"Tarjeta de Débito: ${int(ventas_df[ventas_df['Método de Pago'] == 'Tarjeta de Débito']['Precio'].sum())}")  # Convertir a número entero
        st.write(f"Codigo QR: ${int(ventas_df[ventas_df['Método de Pago'] == 'Codigo QR']['Precio'].sum())}")  # Convertir a número entero
        st.subheader(f"Transferencias: ${ventas_transferencias}")
        st.write(f"Otros: ${ventas_otros}")

def editar_ventas():
    st.header("Editar Ventas")

    # Agregar un campo para ingresar el idVenta
    id_venta_editar = st.text_input("Ingrese el ID de la Venta que desea editar:")

    if id_venta_editar:
        # Descargar el archivo CSV desde S3 y cargarlo en un DataFrame
        csv_file_key = 'ventas.csv'
        response = s3.get_object(Bucket=bucket_name, Key=csv_file_key)
        ventas_df = pd.read_csv(io.BytesIO(response['Body'].read())).applymap(lambda x: str(x).replace(',', '') if pd.notna(x) else x)

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
                    if column != 'idVenta' and column != 'nombreUsuario':
                        valor_actual = venta_editar_df.iloc[0][column]
                        
                        if column == "metodoPago":
                            opciones_metodo_pago = ["Efectivo", "Transferencia", "Tarjeta de Crédito", "Tarjeta de Débito", "Codigo QR", "Otro"]
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
            fecha_venta_actual = venta_editar_df.iloc[0]['fecha']
            fecha_actual_argentina = obtener_fecha_argentina()  # Obtener la fecha actual en Argentina

            if fecha_venta_actual == fecha_actual_argentina.strftime("%Y-%m-%d"):
                # Permitir editar solo si la venta es del día actual
                st.write("Información actual de la venta:")
                st.dataframe(venta_editar_df)

                # Mostrar campos para editar cada variable
                for column in venta_editar_df.columns:
                    if column != 'idVenta' and column != 'nombreUsuario' and column != 'fecha':
                        if column == "metodoPago":
                            nuevo_valor = st.selectbox(f"Nuevo valor para {column}", ["Efectivo", "Transferencia", "Tarjeta de Crédito", "Tarjeta de Débito", "Codigo QR", "Otro"], index=["Efectivo", "Transferencia", "Tarjeta de Crédito", "Tarjeta de Débito", "Codigo QR", "Otro"].index(venta_editar_df.iloc[0][column]))
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