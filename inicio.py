import streamlit as st
import boto3
import pandas as pd
import json
import os
from ingresaVentas import venta
from visualizaVentas import main as visualiza_ventas
from ingresaPedidoFunda import ingresaPedidoFunda
from visualizaPedidosFundas import main as visualiza_pedidos_fundas
from ingresaArreglo import ingresa_servicio_tecnico
from visualizaArreglos import main as visualiza_arreglos
from ingresaUsuarios import ingresa_usuario
from visualizaUsuarios import main as visualizar_usuarios
from PIL import Image

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

# Función para obtener usuarios desde el archivo CSV en S3
def buscar_usuarios(nombre_usuario_input):
    try:
        # Leer el archivo CSV desde S3
        csv_file_key = 'usuarios.csv'
        response = s3.get_object(Bucket=bucket_name, Key=csv_file_key)
        usuarios_df = pd.read_csv(response['Body'])

        # Filtrar por nombre de usuario
        usuarios_df = usuarios_df[usuarios_df['nombreApellido'].str.contains(nombre_usuario_input, case=False)]

        return usuarios_df

    except Exception as e:
        st.error(f"Error al buscar usuarios: {e}")
        return pd.DataFrame()

# Definir las variables para el estado de inicio de sesión
logged_in = st.session_state.get("logged_in", False)
user_nombre_apellido = st.session_state.get("user_nombre_apellido", "")
user_rol = st.session_state.get("user_rol", "")

# Función para verificar las credenciales y obtener el rol del usuario
def login(username, password):
    try:
        usuarios_df = buscar_usuarios(username)

        if not usuarios_df.empty:
            stored_password = usuarios_df.iloc[0]['contraseña']
            if password == stored_password:
                st.session_state.logged_in = True
                st.session_state.user_rol = usuarios_df.iloc[0]['rol']
                st.session_state.user_nombre_apellido = username
                st.session_state.id_usuario = usuarios_df.iloc[0]['idUsuario']
                st.experimental_rerun()
            else:
                st.error("Credenciales incorrectas. Inténtalo de nuevo")
        else:
            st.error("Usuario no encontrado")

    except Exception as e:
        st.error(f"Error al conectar a la base de datos: {e}")

# Función para cerrar sesión
def logout():
    st.session_state.logged_in = False
    st.session_state.user_rol = ""
    st.session_state.user_nombre_apellido = ""  # Limpiar el nombre y apellido al cerrar sesión
    st.success("Sesión cerrada exitosamente")

def main():
    st.title("Megatron Accesorios")

    if logged_in:
        st.sidebar.title("Menú")

        if user_rol == "admin":
            selected_option = st.sidebar.selectbox("Seleccione una opción:", ["Inicio", "Nueva Venta", "Visualizar Ventas", "Nuevo Pedido", "Visualizar Pedidos de Fundas", "Nuevo Servicio Tecnico", "Visualizar Servicios Tecnicos", "Crear Usuario", "Visualizar Usuarios"])
            if selected_option == "Nueva Venta":
                venta(st.session_state.user_nombre_apellido)
            if selected_option == "Visualizar Ventas":
                visualiza_ventas()
            if selected_option == "Nuevo Pedido":
                ingresaPedidoFunda(st.session_state.user_nombre_apellido)
            if selected_option == "Visualizar Pedidos de Fundas":
                visualiza_pedidos_fundas()
            if selected_option == "Nuevo Servicio Tecnico":
                ingresa_servicio_tecnico(st.session_state.user_nombre_apellido)
            if selected_option == "Visualizar Servicios Tecnicos":
                visualiza_arreglos()
            if selected_option == "Crear Usuario":
                ingresa_usuario()
            if selected_option == "Visualizar Usuarios":
                visualizar_usuarios()

            if selected_option == "Inicio":
                texto_inicio()

        else:
            selected_option = st.sidebar.selectbox("Seleccione una opción:", ["Inicio", "Nueva Venta", "Visualizar Ventas", "Nuevo Pedido", "Visualizar Pedidos de Fundas", "Nuevo Servicio Tecnico", "Visualizar Servicios Tecnicos"])
            if selected_option == "Nueva Venta":
                venta(st.session_state.user_nombre_apellido)
            if selected_option == "Visualizar Ventas":
                visualiza_ventas()
            if selected_option == "Nuevo Pedido":
                ingresaPedidoFunda(st.session_state.user_nombre_apellido)
            if selected_option == "Visualizar Pedidos de Fundas":
                visualiza_pedidos_fundas()
            if selected_option == "Nuevo Servicio Tecnico":
                ingresa_servicio_tecnico(st.session_state.user_nombre_apellido)
            if selected_option == "Visualizar Servicios Tecnicos":
                visualiza_arreglos()

            if selected_option == "Inicio":
                texto_inicio()

        st.write(f"Usuario: {user_nombre_apellido}")

    else:
        st.sidebar.title("Inicio de Sesión")

        with st.form(key="login_form"):
            username = st.text_input("Nombre de Usuario:")
            password = st.text_input("Contraseña:", type="password")

            login_submitted = st.form_submit_button("Iniciar Sesión")

            if login_submitted and username and password:
                login(username, password)

    if logged_in:
        st.sidebar.button("Cerrar Sesión", on_click=logout)

def texto_inicio():
    st.write(f"Bienvenido, {user_nombre_apellido}! - Megatron Accesorios - Sistema de Gestión")
    st.subheader("""Nueva Venta\n * Acceda a la función haciendo clic en 'Nueva Venta'.\n * Ingrese el nombre del producto, el precio en números enteros y seleccione el método de pago.\n * Presione 'Registrar Venta' para guardar la información de la nueva venta.""")
    st.subheader("""Visualizar Ventas\n * Acceda a la función haciendo clic en 'Visualizar Ventas'. \n * Por defecto, se mostrarán las ventas del día. \n * Para aplicar filtros adicionales, despliegue el menú de la izquierda. Puede filtrar por rango de fechas o por nombre de usuario. \n * Para editar las ventas ingrese el ID correspondiente y modifique los campos deseados. Luego, presione 'Guardar cambios'. Los usuarios sin permisos de administrador solo pueden editar las vetas del día actual.""")
    st.subheader("""Nuevo Pedido \n * Acceda a la función haciendo clic en 'Nuevo Pedido'. \n * Ingrese la descripción del pedido, el nombre del cliente, el contacto y seleccione el estado del pedido. \n * Si el estado es 'Señado', ingrese el monto de la seña.""")
    st.subheader("""Visualizar Pedidos \n * Acceda a la función haciendo clic en 'Visualizar Pedidos'. \n * Visualice todos los pedidos y filtre por estado \n * Edite el estado del pedido ingresando el ID correspondiente. \n * Para editar un pedido, solo para administradores, ingrese el ID del pedido, modifique los campos y presione 'Guardar cambios'.""")
    st.subheader("""Nuevo Servicio Técnico \n * Acceda a la función haciendo clic en 'Nuevo Servicio Técnico'. \n * Ingrese los detalles del servicio técnico, incluyendo nombre del cliente, contacto, modelo, falla, tipo de desbloqueo y estado. \n * Complete la información requerida y presione 'Registrar Servicio Técnico'.""")
    st.subheader("""Visualizar Servicios Técnicos \n * Acceda a la función haciendo clic en 'Visualizar Servicios Técnicos'. \n * Visualice todos los servicios técnicos y filtre por estado. \n * Busque la imagen del patrón de desbloqueo ingresando el ID y presionando 'Ver Imagen del Patrón'. \n * Edite el estado del servicio técnico ingresando el ID correspondiente.""")
    if user_rol == "admin":
        st.subheader("""Crear Usuario \n * Haga clic en 'Crear Usuario' para registrar un nuevo usuario, función exclusiva para administradores. \n * Ingrese los datos del usuario, incluyendo nombre, apellido, email, contraseña, fecha de nacimiento, DNI, domicilio y rol (empleado o admin). \n * Presione 'Registrar Usuario' para guardar la información.""")
        st.subheader("""Visualizar Usuarios \n * Haga clic en 'Visualizar Usuarios' para ver la información de los usuarios (sin contraseñas, función exclusiva para administradores). \n * Edite la información del usuario ingresando el ID correspondiente y modifique los campos necesarios. \n * Presione 'Guardar cambios' para confirmar las modificaciones.""")

if __name__ == "__main__":
    main()