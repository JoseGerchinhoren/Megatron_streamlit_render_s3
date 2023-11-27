import streamlit as st
from streamlit_drawable_canvas import st_canvas
import numpy as np

# Configuración inicial de Streamlit
st.set_page_config(page_title="Dibujo en Streamlit", layout="wide")

# Configuración del lienzo
canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.3)",  # Color de fondo del lienzo
    stroke_width=10,  # Ancho del trazo
    stroke_color="rgb(255, 165, 0)",  # Color del trazo
    background_color="#fff",  # Color de fondo de la aplicación
    height=400,  # Altura del lienzo en píxeles
    width=800,  # Ancho del lienzo en píxeles
    drawing_mode="freedraw",  # Modo de dibujo (freedraw o polyline)
    key="canvas",
)

# Botón para limpiar el lienzo
if st.button("Limpiar lienzo"):
    canvas_result.json_data["objects"] = []

# Obtener el dibujo como un array de Numpy
if st.button("Obtener dibujo como array"):
    st.write("Dibujo en forma de array:")
    st.json(canvas_result.json_data)

# Mostrar el dibujo resultante
st.write("Dibujo en tiempo real:")
st.write(canvas_result.json_data)
