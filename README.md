# Megatron Streamlit Renderer with S3 Integration (en español)

¡Bienvenido al repositorio de Megatron Streamlit Renderer con Integración S3! Aquí encontrarás el código fuente y la información necesaria para implementar la versión mejorada de la aplicación de gestión interna desarrollada para Megatron Accesorios, ahora adaptada para ejecutarse en la web.

## Descripción del Proyecto

Este proyecto tiene como objetivo optimizar la gestión interna y mejorar la experiencia del cliente en la tienda de accesorios para celulares "Megatron Accesorios". La aplicación, originalmente diseñada para ejecutarse localmente, ha experimentado una transformación reciente para adaptarse a un entorno web. Ahora está alojada en la web mediante Streamlit, con la base de datos almacenada en S3 en archivos CSV.

### Características Clave
⚡ **Inicio de Sesión Seguro:**
- Validación de credenciales para garantizar un acceso seguro.
- Sesiones personalizadas para cada usuario.

⚡ **Menú Dinámico:**
- Menú interactivo adaptado al rol del usuario.
- Opciones específicas para administradores y usuarios estándar.

⚡ **Gestión de Ventas:**
- Registro y seguimiento de nuevas ventas.
- Visualización detallada de historial de ventas.

⚡ **Pedidos Personalizados:**
- Creación y seguimiento de pedidos personalizados.

⚡ **Servicio Técnico:**
- Registro de solicitudes de servicio técnico, incluida la opción de subir un dibujo de patrón de desbloqueo.
- Visualización detallada de servicios técnicos realizados.

⚡ **Usuarios:**
- Creación y gestión de cuentas de usuario.
- Búsqueda de usuarios por nombre.

⚡ **Configuración Personalizada:**
- Conexión a una base de datos AWS S3, con archivos CSV.
- Carga de configuración privada desde la página de Streamlit.

⚡ **Experiencia del Usuario:**
- Interfaz amigable y fácil de usar.
- Acceso rápido a las funciones principales.

Además, se ha agregado un manual detallado para los usuarios, proporcionando instrucciones claras sobre cómo aprovechar al máximo la aplicación.

## Instrucciones:

1. Abre una terminal de Git Bash y ejecuta el siguiente comando para clonar el repositorio en tu máquina local:
   ```bash
   git clone https://github.com/JoseGerchinhoren/Megatron_streamlit_render_s3
   ```

2. Crea un archivo `config.json` en este directorio con el siguiente contenido:
   ```json
   {
       "aws_access_key": "tu_clave_de_acceso_aws_s3",
       "aws_secret_key": "tu_clave_secreta_aws_s3",
       "region_name": "tu_región_aws",
       "bucket_name": "nombre_de_tu_bucket_s3"
   }
   ```
   
3. Navega al directorio principal del proyecto:
   ```bash
   cd Megatron_streamlit_render_s3
   ```

### Nota:
- **Credenciales de AWS S3:** Si no tienes credenciales de AWS S3, sigue los pasos a continuación para crearlas:
   - Inicia sesión en la [Consola de administración de AWS](https://aws.amazon.com/).
   - Ve al panel de control de **IAM (Identidad y acceso)**.
   - Crea un nuevo usuario con acceso programático y adjunta la política `AmazonS3FullAccess`.
   - Copia la clave de acceso y la clave secreta generadas para el nuevo usuario y úsalas en el archivo `config.json`.

5. Una vez que hayas configurado la aplicación local, puedes modificar los módulos según tus preferencias.

6. Si es necesario, sube tus cambios a GitHub.

7. En el repositorio de GitHub, ve al menú superior derecho y busca "Deploy".

8. Sigue los pasos de implementación y configura la sección de variables secretas.

9. ¡Tu aplicación está lista!

### Nota:
- **Ejecución Local:** Para ejecutar la aplicación localmente, necesitarás Python y Streamlit. Instala las dependencias con:
   ```bash
   pip install -r requirements.txt
   ```

- **Ejecución de Streamlit:** Ejecuta la aplicación con el siguiente comando:
   ```bash
   streamlit run app.py
   ```
   La aplicación estará disponible en tu navegador en [http://localhost:8501](http://localhost:8501).

- **Contribución:** Este proyecto está en desarrollo activo, y se aprecia cualquier contribución o comentario para mejorarlo. ¡Gracias por tu interés!

---

# Megatron Streamlit Renderer with S3 Integration (in English)

Welcome to the Megatron Streamlit Renderer with S3 Integration repository! Here you will find the source code and necessary information to implement the enhanced version of the internal management application developed for Megatron Accesorios, now adapted to run on the web.

## Project Description

This project aims to optimize internal management and enhance the customer experience at the "Megatron Accesorios" cellphone accessories store. The application, originally designed to run locally, has recently undergone a transformation to adapt to a web environment. It is now hosted on the web using Streamlit, with the database stored in S3 in CSV files.

### Key Features
⚡ **Secure Login:**
- Credential validation for secure access.
- Custom sessions for each user.

⚡ **Dynamic Menu:**
- Interactive menu adapted to the user's role.
- Specific options for administrators and standard users.

⚡ **Sales Management:**
- Registration and tracking of new sales.
- Detailed visualization of sales history.

⚡ **Custom Case Orders:**
- Creation and tracking of custom case orders.

⚡ **Technical Service:**
- Registration of technical service requests, including the option to upload a lock pattern drawing.
- Detailed visualization of completed technical services.

⚡ **Users:**
- Creation and management of user accounts.
- User search by name.

⚡ **Custom Configuration:**
- Connection to an AWS S3 database, with CSV files.
- Loading private configuration from the Streamlit page.

⚡ **User Experience:**
- User-friendly and easy-to-use interface.
- Quick access to key functions.

In addition, a detailed user guide has been added to provide clear instructions on maximizing the application's potential.

## Instructions:

1. Open a Git Bash terminal and run the following command to clone the repository to your local machine:
   ```bash
   git clone https://github.com/JoseGerchinhoren/Megatron_streamlit_render_s3
   ```

2. Move one level up to ensure you are outside the main directory:
   ```bash
   cd ..
   ```

3. Create a `config.json` file in this upper directory with the following content:
   ```json
   {
       "aws_access_key": "your_aws_s3_access_key",
       "aws_secret_key": "your_aws_s3_secret_key",
       "region_name": "your_aws_region",
       "bucket_name": "your_s3_bucket_name"
   }
   ```

4. Navigate to the project's main directory:
   ```bash
   cd Megatron_streamlit_render_s3
   ```

### Note:
- **AWS S3 Credentials:** If you don't have AWS S3 credentials, follow the steps below to create them:
   - Log in to the [AWS Management Console](https://aws.amazon.com/).
   - Navigate to the **IAM (Identity and Access Management)** dashboard.
   - Create a new user with programmatic access and attach the `AmazonS3FullAccess` policy.
   - Copy the access key and secret key generated for the new user and use them in the `config.json` file.

5. Once you have configured the local settings, you can modify the modules according to your preferences.

6. If necessary, push your changes to GitHub.

7. In the GitHub repository, navigate to the upper right menu and find "Deploy".

8. Follow the deployment steps and configure the secret variables section.

9. Your application is now ready!

### Note:
- **Local Execution:** Running the application locally requires Python and Streamlit. Install dependencies using:
   ```bash
   pip install -r requirements.txt
   ```

- **Streamlit Execution:** Execute the application using the following command:
   ```bash
   streamlit run app.py
   ```
   The application will be available in your browser at [http://localhost:8501](http://localhost:8501).

- **Contribution:** This project is actively under development, and any contributions or feedback to improve it are appreciated. Thank you for your interest!