import streamlit as st
import boto3
import pandas as pd
import io
import json

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

def visualizar_usuarios():
    st.title("Visualizar Usuarios")

    # Cargar el archivo usuarios.csv desde S3
    s3_csv_key = 'usuarios.csv'
    csv_obj = s3.get_object(Bucket=bucket_name, Key=s3_csv_key)
    usuarios_df = pd.read_csv(io.BytesIO(csv_obj['Body'].read()))

    # Cambiar los nombres de las columnas si es necesario
    usuarios_df.columns = ["ID", "Nombre y Apellido", "Email", "contraseña", "Fecha de Nacimiento", "DNI", "Domicilio", "Fecha de Creacion", "Rol"]

    # Cambiar el orden de las columnas según el nuevo orden deseado
    usuarios_df = usuarios_df[["ID", "Nombre y Apellido", "Email", "Fecha de Nacimiento", "DNI", "Domicilio", "Fecha de Creacion", "Rol"]]

    # Ordenar el DataFrame por 'idVenta' en orden descendente
    usuarios_df = usuarios_df.sort_values(by='ID', ascending=False)

    # Mostrar la tabla de usuarios
    st.dataframe(usuarios_df)

def editar_usuario():
    st.title("Editar Usuario")

    # Campo para ingresar el idUsuario del usuario que se desea editar
    id_usuario_editar = st.text_input("Ingrese el ID del usuario que desea editar:")

    if id_usuario_editar:
        # Descargar el archivo CSV desde S3 y cargarlo en un DataFrame
        csv_file_key = 'usuarios.csv'
        response = s3.get_object(Bucket=bucket_name, Key=csv_file_key)
        usuarios_df = pd.read_csv(io.BytesIO(response['Body'].read()))

        # Filtrar el DataFrame para obtener el usuario específico por ID
        usuario_editar_df = usuarios_df[usuarios_df['idUsuario'] == int(id_usuario_editar)]

        # Verificar si se encontró un usuario con el ID proporcionado
        if not usuario_editar_df.empty:
            # Mostrar la información actual del usuario
            st.write("Información actual del usuario:")
            st.dataframe(usuario_editar_df)

            # Mostrar campos para editar cada variable
            for column in usuario_editar_df.columns:
                if column != 'idUsuario' and column != 'fechaCreacion' and column != 'contraseña':  # Evitar editar estos campos
                    nuevo_valor = st.text_input(f"Nuevo valor para {column}", value=usuario_editar_df.iloc[0][column])
                    usuario_editar_df.at[usuario_editar_df.index[0], column] = nuevo_valor

            # Botón para guardar los cambios
            if st.button("Guardar cambios"):
                # Actualizar el DataFrame original con los cambios realizados
                usuarios_df.update(usuario_editar_df)

                # Guardar el DataFrame actualizado en S3
                with io.StringIO() as csv_buffer:
                    usuarios_df.to_csv(csv_buffer, index=False)
                    s3.put_object(Body=csv_buffer.getvalue(), Bucket=bucket_name, Key=csv_file_key)

                st.success("¡Usuario actualizado correctamente!")

        else:
            st.warning(f"No se encontró ningún usuario con el ID {id_usuario_editar}")

def main():
    visualizar_usuarios()

    editar_usuario()

if __name__ == "__main__":
    main()
