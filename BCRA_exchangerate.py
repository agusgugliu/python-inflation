import requests
import os

# Crear la subcarpeta "DATA_dolar" si no existe
folder_path = 'DATA_dolar'
if not os.path.exists(folder_path):
    os.makedirs(folder_path)

# Definir la ruta completa del archivo dentro de la subcarpeta
file_path = os.path.join(folder_path, 'DATA_BCRA_dolar.xls')

# URL del archivo
url = 'https://www.bcra.gob.ar/pdfs/publicacionesestadisticas/com3500.xls'

# Descargar el archivo sin verificar el SSL
response = requests.get(url, verify=False)

# Guardar el contenido del archivo en la subcarpeta
with open(file_path, 'wb') as file:
    file.write(response.content)

print(f"Archivo descargado con éxito en {file_path}")
