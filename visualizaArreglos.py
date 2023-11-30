import streamlit as st
import pyodbc
import json
import boto3
import io
import pandas as pd
import os

# Cargar configuración desde el archivo config.json
with open("../config.json") as config_file:
    config = json.load(config_file)

# Desempaquetar las credenciales desde el archivo de configuración
aws_access_key = config["aws_access_key"]
aws_secret_key = config["aws_secret_key"]
region_name = config["region_name"]
bucket_name = config["bucket_name"]

# Conectar a S3
s3 = boto3.client('s3', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key, region_name=region_name)

def visualiza_servicios_tecnicos():
    st.title("Servicios Técnicos")

    # Cargar el archivo serviciosTecnicos.csv desde S3
    s3_csv_key = 'serviciosTecnicos.csv'
    csv_obj = s3.get_object(Bucket=bucket_name, Key=s3_csv_key)
    servicios_df = pd.read_csv(csv_obj['Body'])

    # Cambiar los nombres de las columnas según la modificación en el CSV
    servicios_df.columns = ["ID", "Fecha", "Nombre del Cliente", "Contacto", "Modelo", "Falla", "Tipo de Desbloqueo",
                           "Contraseña", "Estado", "Observaciones", "Nombre de Usuario","Imagen del Patrón"]

    # Convertir la columna "Contacto" a tipo cadena y eliminar las comas
    servicios_df['Contacto'] = servicios_df['Contacto'].astype(str).str.replace(',', '')

    # Cambiar el orden de las columnas según el nuevo orden deseado
    servicios_df = servicios_df[["ID", "Fecha", "Nombre del Cliente", "Contacto", "Modelo", "Falla",  "Estado", "Tipo de Desbloqueo",
                    "Contraseña", "Observaciones", "Nombre de Usuario"]]

    # Agregar un filtro por estado
    estados = servicios_df['Estado'].unique()
    filtro_estado = st.selectbox("Filtrar por Estado:", ["Todos"] + list(estados))

    if filtro_estado != "Todos":
        servicios_df = servicios_df[servicios_df['Estado'] == filtro_estado]

    # Ordenar el DataFrame por 'ID' en orden descendente
    servicios_df = servicios_df.sort_values(by='ID', ascending=False)

    # Convertir la columna "ID" a tipo cadena y eliminar las comas
    servicios_df['ID'] = servicios_df['ID'].astype(str).str.replace(',', '')

    # Mostrar la tabla de servicios técnicos
    st.dataframe(servicios_df)

    # Botón para ver la imagen del patrón de desbloqueo
    st.header("Ver Imagen de Patron de Desbloqueo")
    id_servicio_ver_imagen = st.text_input("Ingrese el ID del servicio técnico para ver la imagen del patrón:")
    if st.button("Ver Imagen del Patrón") and id_servicio_ver_imagen:
        mostrar_imagen_patron(int(id_servicio_ver_imagen))

def editar_estado_servicio_tecnico():
    st.header("Editar Estado de Servicio Técnico")

    # Agregar un campo para ingresar el ID del servicio
    id_servicio_editar = st.text_input("Ingrese el ID del servicio técnico que desea editar el estado:")

    if id_servicio_editar:
        # Descargar el archivo CSV desde S3 y cargarlo en un DataFrame
        csv_file_key = 'serviciosTecnicos.csv'
        response = s3.get_object(Bucket=bucket_name, Key=csv_file_key)
        servicios_df = pd.read_csv(response['Body'])

        # Filtrar el DataFrame para obtener el servicio técnico específico por ID
        servicios_editar_df = servicios_df[servicios_df['idServicio'] == int(id_servicio_editar)]

        if not servicios_editar_df.empty:
            # Mostrar campo para editar el estado
            nuevo_estado = st.selectbox("Nuevo valor para Estado:", ["Aceptado", "Consulta", "Tecnico", "Terminado", "Cancelado"], index=0)
            servicios_editar_df.loc[servicios_editar_df.index[0], 'estado'] = nuevo_estado

            # Botón para guardar los cambios
            if st.button("Guardar Estado"):
                # Actualizar el DataFrame original con los cambios realizados
                servicios_df.update(servicios_editar_df)

                # Guardar el DataFrame actualizado en S3
                with io.StringIO() as csv_buffer:
                    servicios_df.to_csv(csv_buffer, index=False)
                    s3.put_object(Body=csv_buffer.getvalue(), Bucket=bucket_name, Key=csv_file_key)

                st.success("¡Estado del servicio técnico actualizado correctamente!")

        else:
            st.warning(f"No se encontró ningún servicio técnico con el ID {id_servicio_editar}")

def mostrar_imagen_patron(id_servicio):
    try:
        # Leer el archivo CSV desde S3
        csv_file_key = 'serviciosTecnicos.csv'
        response = s3.get_object(Bucket=bucket_name, Key=csv_file_key)
        servicios_df = pd.read_csv(io.BytesIO(response['Body'].read()))

        # Filtrar el DataFrame para obtener el servicio específico por ID
        servicio_seleccionado = servicios_df[servicios_df['idServicio'] == id_servicio].iloc[0]

        # Verificar si el servicio tiene un dibujo de patrón y el tipo de desbloqueo es "Patrón"
        tiene_patron = servicio_seleccionado['imagenPatron'] is not None
        es_patron = servicio_seleccionado['tipoDesbloqueo'] == 'Patron'

        if tiene_patron and es_patron:
            st.subheader("Dibujo del Patrón de Desbloqueo")
            try:
                # Mostrar el dibujo con un ancho personalizado
                ancho_columna = st.columns([0.2, 0.4])
                ancho_columna[0].image(servicio_seleccionado['imagenPatron'], caption="Dibujo del Patrón de Desbloqueo", use_column_width=True)
            except Exception as e:
                st.warning(f"No se pudo mostrar el dibujo del patrón: {e}")
        else:
            st.warning("Este servicio técnico no tiene un dibujo de patrón de desbloqueo o el tipo de desbloqueo no es 'Patrón'.")

    except Exception as e:
        st.error(f"Error al mostrar el dibujo de patrón: {e}")

def editar_servicio_tecnico():

    st.header("Editar Servicio Técnico")

    # Agregar un campo para ingresar el ID del servicio
    id_servicio_editar = st.text_input("Ingrese el ID del servicio técnico que desea editar:")

    if id_servicio_editar :
        # Descargar el archivo CSV desde S3 y cargarlo en un DataFrame
        csv_file_key = 'serviciosTecnicos.csv'
        response = s3.get_object(Bucket=bucket_name, Key=csv_file_key)
        servicios_df = pd.read_csv(response['Body'])

        # Filtrar el DataFrame para obtener el servicio técnico específico por ID
        servicios_editar_df = servicios_df[servicios_df['idServicio'] == int(id_servicio_editar)]

        if not servicios_editar_df.empty:
            # Mostrar la información actual del servicio técnico
            st.write("Información actual del servicio técnico:")
            st.dataframe(servicios_editar_df)

            # Mostrar campos para editar cada variable
            for column in servicios_editar_df.columns:
                nuevo_valor = st.text_input(f"Nuevo valor para {column}", value=servicios_editar_df.iloc[0][column])
                servicios_editar_df.at[servicios_editar_df.index[0], column] = nuevo_valor

            # Botón para guardar los cambios
            if st.button("Guardar cambios"):
                # Actualizar el DataFrame original con los cambios realizados
                servicios_df.update(servicios_editar_df)

                # Guardar el DataFrame actualizado en S3
                with io.StringIO() as csv_buffer:
                    servicios_df.to_csv(csv_buffer, index=False)
                    s3.put_object(Body=csv_buffer.getvalue(), Bucket=bucket_name, Key=csv_file_key)

                st.success("¡Servicio técnico actualizado correctamente!")

        else:
            st.warning(f"No se encontró ningún servicio técnico con el ID {id_servicio_editar}")

def main():
    visualiza_servicios_tecnicos()

    editar_estado_servicio_tecnico()

    # Verificar si el usuario es admin
    if st.session_state.user_rol == "admin":
        editar_servicio_tecnico()

if __name__ == "__main__":
    main()