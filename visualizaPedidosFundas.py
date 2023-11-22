import streamlit as st
import pyodbc
import pandas as pd
import json

# Cargar configuración desde el archivo config.json
with open("../config.json") as config_file:
    config = json.load(config_file)

# Conexión a la base de datos SQL Server
db = pyodbc.connect(
    driver=config["driver"],
    server=config["server"],
    database=config["database"],
    uid=config["user"],
    pwd=config["password"]
)

def editar_estado_pedido_funda(pedidos_df, id_pedido_funda, nuevo_estado):
    try:
        # Crear un cursor para ejecutar comandos SQL
        cursor = db.cursor()

        # Verificar si el ID del Pedido de Funda existe
        if id_pedido_funda not in pedidos_df['ID'].values:
            st.warning(f"El ID del Pedido de Funda {id_pedido_funda} no existe.")
            return

        # Actualizar el estado del Pedido de Funda en la base de datos
        query = f"UPDATE pedidosFundas SET estado = '{nuevo_estado}' WHERE idPedidoFunda = {id_pedido_funda}"
        cursor.execute(query)
        db.commit()

        st.success(f"Estado del Pedido de Funda {id_pedido_funda} editado correctamente a: {nuevo_estado}")

    except Exception as e:
        st.error(f"Error al editar el estado del Pedido de Funda: {e}")

def visualiza_pedidos_fundas():
    st.title("Visualizar Pedidos de Fundas")

    # Construir la consulta SQL para obtener los pedidos de fundas
    query = "SELECT * FROM pedidosFundas ORDER BY idPedidoFunda DESC"

    # Ejecutar la consulta y obtener los resultados en un DataFrame
    pedidos_df = pd.read_sql(query, db)

    # Consulta SQL para obtener la información de los usuarios
    query_usuarios = "SELECT idUsuario, nombreApellido FROM Usuarios"
    usuarios_df = pd.read_sql(query_usuarios, db)

    # Fusionar (unir) el DataFrame de ventas con el DataFrame de usuarios
    pedidos_df = pd.merge(pedidos_df, usuarios_df, on="idUsuario", how="left")

    # Cambiar los nombres de las columnas
    pedidos_df.columns = ["ID", "Fecha", "Pedido", "Nombre del Cliente", "Contacto", "Estado", "Monto Seña","ID Usuario", "Nombre de Usuario"]

    # Cambiar el orden del DataFrame
    pedidos_df = pedidos_df[[
        "ID",
        "Fecha",
        "Pedido",
        "Estado",
        "Monto Seña",
        "Nombre del Cliente",
        "Contacto",
        "Nombre de Usuario"
    ]]

    # Agregar un filtro por estado
    estados = pedidos_df['Estado'].unique()
    filtro_estado = st.selectbox("Filtrar por Estado:", ["Todos"] + list(estados))

    if filtro_estado != "Todos":
        pedidos_df = pedidos_df[pedidos_df['Estado'] == filtro_estado]

    # Mostrar la tabla de pedidos de fundas
    st.dataframe(pedidos_df)

    # Sección para la edición del estado de registros
    st.subheader("Editar Estado")
    id_pedido_funda = st.number_input("Ingrese el ID del Pedido de Funda que desea editar:", value=0)
    nuevo_estado = st.selectbox("Nuevo valor del campo estado:", ["Señado", "Pedido", "Avisado","Entregado", "Cancelado"])

    if st.button("Guardar"):
        editar_estado_pedido_funda(pedidos_df, id_pedido_funda, nuevo_estado)

def main():
    visualiza_pedidos_fundas()

if __name__ == "__main__":
    main()
