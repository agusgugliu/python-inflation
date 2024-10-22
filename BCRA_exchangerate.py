import requests
import os
import pandas as pd
import sqlite3
import shutil
import matplotlib.pyplot as plt
from datetime import datetime
import argparse

# Configurar argparse para manejar los argumentos de línea de comandos
parser = argparse.ArgumentParser(description='Script to analyze the daily evolution of the Dollar exchange rate.')
parser.add_argument('date_from', type=str, help='Start date in the format YYYY-MM-DD')
parser.add_argument('date_until', type=str, help='End date in the format YYYY-MM-DD')
args = parser.parse_args()

# Asignar los argumentos a variables
date_from = args.date_from
date_until = args.date_until

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

# Filtrar el DataFrame según el rango de fechas proporcionado
df_filtered = df[(df['ID_tie_date'] >= pd.to_datetime(date_from).date()) & (df['ID_tie_date'] <= pd.to_datetime(date_until).date())]

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
for row in df_filtered.itertuples(index=False):
    cursor.execute('INSERT INTO FT_BCRA_dolar (ID_tie_date, F_bcra_dolar) VALUES (?, ?)', (row.ID_tie_date, row.F_bcra_dolar))

# Confirmar los cambios y cerrar la conexión
conn.commit()
conn.close()

print("Datos insertados con éxito en la tabla FT_BCRA_dolar")

# Eliminar la carpeta DATA_dolar y su contenido si existe
if os.path.exists(folder_path):
    shutil.rmtree(folder_path)
    print(f"Carpeta {folder_path} eliminada con éxito")

# Graficar la evolución diaria del tipo de cambio del dólar
plt.figure(figsize=(12, 8))
plt.plot(df_filtered['ID_tie_date'], df_filtered['F_bcra_dolar'], marker='x', markersize=3, linestyle='-', color='lightblue', linewidth=1.5, label='Tipo de Cambio del Dólar')

# Añadir línea vertical para el inicio del año actual
current_year_start = pd.to_datetime(f"{datetime.now().year}-01-01").date()
plt.axvline(x=current_year_start, color='red', linestyle='--', linewidth=1, label='Inicio del Año Actual')

# Añadir anotaciones para el valor máximo, mínimo y último valor
max_value = df_filtered['F_bcra_dolar'].max()
min_value = df_filtered['F_bcra_dolar'].min()
last_value = df_filtered['F_bcra_dolar'].iloc[-1]
last_date = df_filtered['ID_tie_date'].iloc[-1]

plt.scatter(df_filtered['ID_tie_date'][df_filtered['F_bcra_dolar'] == max_value], max_value, color='green', zorder=5)
plt.scatter(df_filtered['ID_tie_date'][df_filtered['F_bcra_dolar'] == min_value], min_value, color='red', zorder=5)
plt.scatter(last_date, last_value, color='blue', zorder=5)

plt.text(df_filtered['ID_tie_date'][df_filtered['F_bcra_dolar'] == max_value].values[0], max_value, f'Max: {max_value:.2f}', fontsize=10, verticalalignment='bottom', color='green')
plt.text(df_filtered['ID_tie_date'][df_filtered['F_bcra_dolar'] == min_value].values[0], min_value, f'Min: {min_value:.2f}', fontsize=10, verticalalignment='top', color='red')
plt.text(last_date, last_value, f'Last: {last_value:.2f}', fontsize=10, verticalalignment='bottom', color='blue')

plt.xlabel('Fecha', fontsize=12)
plt.ylabel('Tipo de Cambio del Dólar', fontsize=12)
plt.title('Evolución Diaria del Tipo de Cambio del Dólar', fontsize=16, fontweight='bold')
plt.legend(fontsize=12)
plt.grid(True, linestyle='--', alpha=0.6)

# Crear la carpeta images si no existe
image_folder = 'images'
if not os.path.exists(image_folder):
    os.makedirs(image_folder)

# Guardar el gráfico como imagen en PNG
image_path = os.path.join(image_folder, 'dollar_graph.png')
plt.savefig(image_path, format='png', dpi=300, bbox_inches='tight')

print(f"El gráfico se ha guardado en {image_path}")