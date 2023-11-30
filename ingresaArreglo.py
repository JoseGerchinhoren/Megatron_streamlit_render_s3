import streamlit as st
import pyodbc
import json
import boto3
import io
import pandas as pd
import os
from streamlit_drawable_canvas import st_canvas
from PIL import Image

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

# Función para insertar un servicio técnico en la base de datos
def insertar_servicio_tecnico(fecha, nombre_cliente, contacto, modelo, falla, tipo_desbloqueo, contraseña, imagen_patron, estado, observaciones, nombre_usuario, precio=None, metodo_pago=None):
    try:
        # Leer el archivo CSV desde S3
        csv_file_key = 'serviciosTecnicos.csv'
        response = s3.get_object(Bucket=bucket_name, Key=csv_file_key)
        servicios_df = pd.read_csv(io.BytesIO(response['Body'].read()))

        # Obtener el último idServicio
        ultimo_id = servicios_df['idServicio'].max()

        # Si no hay registros, asignar 1 como idServicio, de lo contrario, incrementar el último idServicio
        nuevo_id = 1 if pd.isna(ultimo_id) else int(ultimo_id) + 1

        # Crear una nueva fila como un diccionario
        nueva_fila = {'idServicio': nuevo_id, 'fecha': fecha, 'nombreCliente': nombre_cliente, 'contacto': contacto,
                      'modelo': modelo, 'falla': falla, 'tipoDesbloqueo': tipo_desbloqueo, 'contraseña': contraseña,
                      'imagenPatron': imagen_patron, 'estado': estado, 'observaciones': observaciones,
                      'nombreUsuario': nombre_usuario, 'precio': precio, 'metodoPago': metodo_pago}

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
        st.warning("Dibuja el patrón:")
        imagen_patron = st_canvas(
            fill_color="rgb(0, 255, 255)",  # Cambia aquí al valor de celeste que prefieras
            stroke_width=10,
            stroke_color="rgb(0, 255, 255)",  # Cambia aquí al valor de celeste que prefieras
            background_color="rgb(0, 0, 0)",
            height=200,
            width=200,
            drawing_mode="freedraw",
            key="canvas",
        )

    estado = st.selectbox("Estado:", ["Aceptado", "Consulta", "Tecnico", "Terminado", "Cancelado"])

    # Verificar si el estado es "Terminado" para mostrar los campos adicionales
    if estado == "Terminado":
        precio = st.text_input("Precio:")
        if precio:
            if precio.isdigit():
                precio = int(precio)
            else:
                st.warning("El precio debe ser un número entero.")
                precio = None
        else:
            precio = None
        metodo_pago = st.selectbox("Método de Pago:", ["Efectivo", "Transferencia", "Tarjeta de Crédito", "Tarjeta de Débito", "Otro"])
    else:
        precio = None
        metodo_pago = None

    observaciones = st.text_area("Observaciones:")

    # Botón para registrar el servicio técnico
    if st.button("Registrar Servicio Técnico"):
        if fecha and nombre_cliente and contacto and modelo and falla and tipo_desbloqueo and estado:
            # Ajuste para manejar la contraseña, el patrón, el precio y el método de pago
            if tipo_desbloqueo == "Sin Contraseña":
                insertar_servicio_tecnico(fecha, nombre_cliente, contacto, modelo, falla, tipo_desbloqueo,
                                        None, None, estado, observaciones, nombre_usuario, precio, metodo_pago)
            elif tipo_desbloqueo == "Contraseña o Pin":
                insertar_servicio_tecnico(fecha, nombre_cliente, contacto, modelo, falla, tipo_desbloqueo,
                                        contraseña, None, estado, observaciones, nombre_usuario, precio, metodo_pago)
            elif tipo_desbloqueo == "Patron":
                if imagen_patron:
                    # Convertir el dibujo a una imagen y guardarla en S3
                    imagen_patron_url = guardar_dibujo_s3(imagen_patron, nombre_cliente)
                    insertar_servicio_tecnico(fecha, nombre_cliente, contacto, modelo, falla, tipo_desbloqueo,
                                            None, imagen_patron_url, estado, observaciones, nombre_usuario, precio, metodo_pago)
                else:
                    st.warning("Por favor, dibuja un patrón.")
        else:
            st.warning("Por favor, complete todos los campos.")

def guardar_dibujo_s3(dibujo, nombre_cliente):
    try:
        bucket_key = f'patrones/{nombre_cliente}_patron.png'
        # Convertir el dibujo a una imagen utilizando PIL
        imagen_pil = Image.fromarray(dibujo.image_data)
        # Guardar la imagen en S3
        with io.BytesIO() as image_buffer:
            imagen_pil.save(image_buffer, format="PNG")
            s3.put_object(Body=image_buffer.getvalue(), Bucket=bucket_name, Key=bucket_key, ContentType='image/png')
        return f'https://{bucket_name}.s3.{region_name}.amazonaws.com/{bucket_key}'
    except Exception as e:
        st.error(f"Error al subir el dibujo a S3: {e}")

if __name__ == "__main__":
    ingresa_servicio_tecnico("nombre_de_usuario")