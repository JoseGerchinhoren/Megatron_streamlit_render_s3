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

# # Configura tus credenciales y la región de AWS desde variables de entorno
# aws_access_key = os.getenv('aws_access_key_id')
# aws_secret_key = os.getenv('aws_secret_access_key')
# region_name = os.getenv('aws_region')
# bucket_name = 'megatron-accesorios'

# Conecta a S3
s3 = boto3.client('s3', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key, region_name=region_name)

# Función para insertar un servicio técnico en la base de datos
def insertar_servicio_tecnico(fecha, nombre_cliente, contacto, modelo, falla, tipo_desbloqueo, contraseña, imagen_patron, estado, observaciones, nombre_usuario):
    try:
        # Leer el archivo CSV desde S3
        csv_file_key = 'arreglosTecnicos.csv'
        response = s3.get_object(Bucket=bucket_name, Key=csv_file_key)
        servicios_df = pd.read_csv(io.BytesIO(response['Body'].read()))

        # Obtener el último idArreglo
        ultimo_id = servicios_df['idArreglo'].max()

        # Si no hay registros, asignar 1 como idArreglo, de lo contrario, incrementar el último idArreglo
        nuevo_id = 1 if pd.isna(ultimo_id) else int(ultimo_id) + 1

        # Crear una nueva fila como un diccionario
        nueva_fila = {'idArreglo': nuevo_id, 'fecha': fecha, 'nombreCliente': nombre_cliente, 'contacto': contacto,
                      'modelo': modelo, 'falla': falla, 'tipoDesbloqueo': tipo_desbloqueo, 'contraseña': contraseña,
                      'imagenPatron': imagen_patron, 'estado': estado, 'observaciones': observaciones,
                      'nombreUsuario': nombre_usuario}

        # Convertir el diccionario a DataFrame y concatenarlo al DataFrame existente
        servicios_df = pd.concat([servicios_df, pd.DataFrame([nueva_fila])], ignore_index=True)

        # Guardar el DataFrame actualizado de nuevo en S3
        with io.StringIO() as csv_buffer:
            servicios_df.to_csv(csv_buffer, index=False)
            s3.put_object(Body=csv_buffer.getvalue(), Bucket=bucket_name, Key=csv_file_key)

        st.success("Servicio técnico registrado exitosamente")

    except Exception as e:
        st.error(f"Error al registrar el servicio técnico: {e}")

def ingresa_servicio_tecnico(nombre_usuario):
    st.title("Registrar Servicio Técnico")

    # Campos para ingresar los datos del servicio técnico
    fecha = st.date_input("Fecha del Servicio Técnico:")
    nombre_cliente = st.text_input("Nombre del Cliente:")
    contacto = st.text_input("Contacto:")
    modelo = st.text_input("Modelo:")
    falla = st.text_input("Falla:")
    
    # Opciones para el tipo de desbloqueo
    opciones_tipo_desbloqueo = ["Sin Contraseña", "Contraseña o Pin", "Patron"]
    tipo_desbloqueo = st.selectbox("Tipo de Desbloqueo:", opciones_tipo_desbloqueo)

    # Campo adicional para la contraseña o pin si se selecciona la opción correspondiente
    contraseña = None
    if tipo_desbloqueo == "Contraseña o Pin":
        contraseña = st.text_input("Contraseña o Pin:")

    # Campo adicional para el patrón de desbloqueo si se selecciona la opción correspondiente
    imagen_patron = None
    if tipo_desbloqueo == "Patron":
        imagen_patron = st.file_uploader("Imagen del Patrón:")

    estado = st.selectbox("Estado:", ["Aceptado", "Consulta", "Tecnico", "Terminado", "Cancelado"])
    observaciones = st.text_area("Observaciones:")

    # Botón para registrar el servicio técnico
    if st.button("Registrar Servicio Técnico"):
        if fecha and nombre_cliente and contacto and modelo and falla and tipo_desbloqueo and estado:
            # Ajuste para manejar la contraseña y el patrón
            if tipo_desbloqueo == "Sin Contraseña":
                insertar_servicio_tecnico(fecha, nombre_cliente, contacto, modelo, falla, tipo_desbloqueo,
                                          None, None, estado, observaciones, nombre_usuario)
            elif tipo_desbloqueo == "Contraseña o Pin":
                insertar_servicio_tecnico(fecha, nombre_cliente, contacto, modelo, falla, tipo_desbloqueo,
                                          contraseña, None, estado, observaciones, nombre_usuario)
            elif tipo_desbloqueo == "Patron":
                if imagen_patron:
                    imagen_patron_url = guardar_imagen_s3(imagen_patron, nombre_cliente)
                    insertar_servicio_tecnico(fecha, nombre_cliente, contacto, modelo, falla, tipo_desbloqueo,
                                              None, imagen_patron_url, estado, observaciones, nombre_usuario)
                else:
                    st.warning("Por favor, cargue una imagen del patrón.")
        else:
            st.warning("Por favor, complete todos los campos.")

def guardar_imagen_s3(imagen, nombre_cliente):
    try:
        bucket_key = f'imagenes/{nombre_cliente}_patron.png'
        s3.put_object(Body=imagen.read(), Bucket=bucket_name, Key=bucket_key, ContentType='image/png')
        return f'https://{bucket_name}.s3.{region_name}.amazonaws.com/{bucket_key}'
    except Exception as e:
        st.error(f"Error al subir la imagen a S3: {e}")

if __name__ == "__main__":
    ingresa_servicio_tecnico("nombre_de_usuario")