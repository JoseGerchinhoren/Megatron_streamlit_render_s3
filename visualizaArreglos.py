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

# Conecta a S3
s3 = boto3.client('s3', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key, region_name=region_name)

def visualiza_arreglos_tecnicos():
    st.title("Visualizar Arreglos Técnicos")

    # Cargar el archivo arreglosTecnicos.csv desde S3
    s3_csv_key = 'arreglosTecnicos.csv'
    csv_obj = s3.get_object(Bucket=bucket_name, Key=s3_csv_key)
    arreglos_df = pd.read_csv(csv_obj['Body'])

    # Cambiar los nombres de las columnas según la modificación en el CSV
    arreglos_df.columns = ["ID", "Fecha", "Nombre del Cliente", "Contacto", "Modelo", "Falla", "Tipo de Desbloqueo",
                           "Contraseña", "Imagen del Patrón", "Estado", "Observaciones", "Nombre de Usuario"]

    # Agregar un filtro por estado
    estados = arreglos_df['Estado'].unique()
    filtro_estado = st.selectbox("Filtrar por Estado:", ["Todos"] + list(estados))

    if filtro_estado != "Todos":
        arreglos_df = arreglos_df[arreglos_df['Estado'] == filtro_estado]

    # Mostrar la tabla de arreglos técnicos
    st.dataframe(arreglos_df)

def editar_estado_arreglo_tecnico():
    st.title("Editar Estado de Arreglo Técnico")

    # Agregar un campo para ingresar el idArreglo
    id_arreglo_editar = st.text_input("Ingrese el ID del arreglo técnico que desea editar el estado:")

    if id_arreglo_editar:
        # Descargar el archivo CSV desde S3 y cargarlo en un DataFrame
        csv_file_key = 'arreglosTecnicos.csv'
        response = s3.get_object(Bucket=bucket_name, Key=csv_file_key)
        arreglos_df = pd.read_csv(response['Body'])

        # Filtrar el DataFrame para obtener el arreglo técnico específico por ID
        arreglos_editar_df = arreglos_df[arreglos_df['ID'] == int(id_arreglo_editar)]

        if not arreglos_editar_df.empty:
            # Mostrar campo para editar el estado
            nuevo_estado = st.selectbox("Nuevo valor para Estado:", ["En Proceso", "Terminado", "Cancelado"], index=0)
            arreglos_editar_df.loc[arreglos_editar_df.index[0], 'Estado'] = nuevo_estado

            # Botón para guardar los cambios
            if st.button("Guardar cambios"):
                # Actualizar el DataFrame original con los cambios realizados
                arreglos_df.update(arreglos_editar_df)

                # Guardar el DataFrame actualizado en S3
                with io.StringIO() as csv_buffer:
                    arreglos_df.to_csv(csv_buffer, index=False)
                    s3.put_object(Body=csv_buffer.getvalue(), Bucket=bucket_name, Key=csv_file_key)

                st.success("¡Estado del arreglo técnico actualizado correctamente!")

        else:
            st.warning(f"No se encontró ningun arreglo técnico con el ID {id_arreglo_editar}")

def main():
    visualiza_arreglos_tecnicos()

    editar_estado_arreglo_tecnico()

if __name__ == "__main__":
    main()
