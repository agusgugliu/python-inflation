import requests
import os
import pandas as pd
import sqlite3
import shutil

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

# Leer el archivo Excel y extraer solo las columnas C y D, eliminando las primeras 4 filas
df = pd.read_excel(file_path, usecols="C:D", names=["ID_tie_date", "F_bcra_dolar"], skiprows=4)

# Convertir la columna ID_tie_date a formato de fecha y F_bcra_dolar a float
df['ID_tie_date'] = pd.to_datetime(df['ID_tie_date'], errors='coerce').dt.date
df['F_bcra_dolar'] = pd.to_numeric(df['F_bcra_dolar'], errors='coerce')

# Conectar a la base de datos SQLite
conn = sqlite3.connect('databases/social_indicators.db')
cursor = conn.cursor()

# Crear la tabla FT_BCRA_dolar si no existe
cursor.execute('''
CREATE TABLE IF NOT EXISTS FT_BCRA_dolar (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ID_tie_date DATE,
    F_bcra_dolar FLOAT
)
''')

# Truncar la tabla FT_BCRA_dolar antes de insertar nuevos datos
cursor.execute('DELETE FROM FT_BCRA_dolar')

# Insertar los datos filtrados en la tabla FT_BCRA_dolar
for row in df.itertuples(index=False):
    cursor.execute('INSERT INTO FT_BCRA_dolar (ID_tie_date, F_bcra_dolar) VALUES (?, ?)', (row.ID_tie_date, row.F_bcra_dolar))

# Confirmar los cambios y cerrar la conexión
conn.commit()
conn.close()

print("Datos insertados con éxito en la tabla FT_BCRA_dolar")

# Eliminar la carpeta DATA_dolar y su contenido si existe
if os.path.exists(folder_path):
    shutil.rmtree(folder_path)
    print(f"Carpeta {folder_path} eliminada con éxito")