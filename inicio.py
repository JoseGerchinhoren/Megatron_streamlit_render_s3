import streamlit as st
import boto3
import pandas as pd
import json
import os
from ingresaVentas import venta
from visualizaVentas import main as visualiza_ventas
from ingresaPedidoFunda import ingresaPedidoFunda
from visualizaPedidosFundas import main as visualiza_pedidos_fundas

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
    st.title("Megatron Accesorios - Sistema de Gestión")

    if logged_in:
        st.sidebar.title("Menú")

        if user_rol == "admin":
            selected_option = st.sidebar.selectbox("Seleccione una opción:", ["Inicio", "Nueva Venta", "Visualizar Ventas", "Nuevo Pedido de Funda", "Visualizar Pedidos de Fundas", "Nuevo Servicio Tecnico", "Visualizar Servicios Tecnicos", "Crear Usuario", "Visualizar Usuarios"])
            if selected_option == "Nueva Venta":
                venta(st.session_state.user_nombre_apellido)
            # if selected_option == "Crear Usuario":
            #     crear_usuario()
            if selected_option == "Visualizar Ventas":
                visualiza_ventas()
            if selected_option == "Nuevo Pedido de Funda":
                ingresaPedidoFunda(st.session_state.user_nombre_apellido)
            if selected_option == "Visualizar Pedidos de Fundas":
                visualiza_pedidos_fundas()
            # if selected_option == "Nuevo Servicio Tecnico":
            #     ingresa_arreglo_tecnico(st.session_state.id_usuario)
            # if selected_option == "Visualizar Servicios Tecnicos":
            #     visualizar_arreglos()
            # if selected_option == "Visualizar Usuarios":
            #     visualizar_usuarios()

        else:
            selected_option = st.sidebar.selectbox("Seleccione una opción:", ["Inicio", "Nueva Venta", "Visualizar Ventas", "Nuevo Pedido de Funda", "Visualizar Pedidos de Fundas", "Nuevo Servicio Tecnico", "Visualizar Servicios Tecnicos"])
            if selected_option == "Nueva Venta":
                venta(st.session_state.user_nombre_apellido)
            if selected_option == "Visualizar Ventas":
                visualiza_ventas()
            if selected_option == "Nuevo Pedido de Funda":
                ingresaPedidoFunda(st.session_state.user_nombre_apellido)
            if selected_option == "Visualizar Pedidos de Fundas":
                visualiza_pedidos_fundas()
            # if selected_option == "Nuevo Servicio Tecnico":
            #     ingresa_arreglo_tecnico(st.session_state.id_usuario)
            # if selected_option == "Visualizar Servicios Tecnicos":
            #     visualizar_arreglos()      

        if selected_option == "Inicio":
            st.write(f"Bienvenido, {user_nombre_apellido}! - Megatron Accesorios - Sistema de Gestión")

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

if __name__ == "__main__":
    main()
