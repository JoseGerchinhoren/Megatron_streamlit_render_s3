import json
import os

def cargar_configuracion():
    # # Cargar configuración desde el archivo config.json
    # with open("../config.json") as config_file:
    #     config = json.load(config_file)

    # # Desempaquetar las credenciales desde el archivo de configuración
    # aws_access_key = config["aws_access_key"]
    # aws_secret_key = config["aws_secret_key"]
    # region_name = config["region_name"]
    # bucket_name = config["bucket_name"]

    # Configura tus credenciales y la región de AWS desde variables de entorno
    aws_access_key = os.getenv('aws_access_key_id')
    aws_secret_key = os.getenv('aws_secret_access_key')
    region_name = os.getenv('aws_region')
    bucket_name = 'megatron-accesorios'

    return aws_access_key, aws_secret_key, region_name, bucket_name
