import requests
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sqlite3
from io import StringIO
import shutil
import argparse

# Configurar argparse para manejar los argumentos de línea de comandos
parser = argparse.ArgumentParser(description='Script to analyze inflation data and project future periods.')
parser.add_argument('periodo_desde', type=str, help='Start period in the format YYYYMM')
parser.add_argument('periodo_hasta', type=str, help='End period in the format YYYYMM')
parser.add_argument('num_periodos_proyeccion', type=int, help='Number of periods to project forward')
args = parser.parse_args()

# Asignar los argumentos a variables
periodo_desde = args.periodo_desde
periodo_hasta = args.periodo_hasta
num_periodos_proyeccion = args.num_periodos_proyeccion

# URL del archivo CSV
url = 'https://www.indec.gob.ar/ftp/cuadros/economia/serie_ipc_divisiones.csv'

# Descargar el archivo CSV
response = requests.get(url)
csv_content = response.content.decode('latin1')

# Leer el contenido del CSV directamente en un DataFrame
df = pd.read_csv(StringIO(csv_content), encoding='latin1', delimiter=';')

# Conectar a la base de datos SQLite en la carpeta databases
db_path = os.path.join('databases', 'social_indicators.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Insertar los datos del DataFrame en la tabla FT_indec_ipc
df.to_sql('FT_indec_ipc', conn, if_exists='append', index=False)

# Confirmar la inserción
conn.commit()

# Eliminar la carpeta DATA_ipc y su contenido si existe
folder_path = 'DATA_ipc'
if os.path.exists(folder_path):
    shutil.rmtree(folder_path)

# Consultar los datos desde la base de datos
query = f"""
SELECT Periodo, Descripcion, Region, v_m_IPC
FROM FT_indec_ipc
WHERE Descripcion = 'NIVEL GENERAL'
AND Region = 'Nacional'
AND Periodo >= '{periodo_desde}'
AND Periodo <= '{periodo_hasta}'
"""
df_filtered = pd.read_sql_query(query, conn)

# Cerrar la conexión a la base de datos
conn.close()

# Asegurarse de que la columna "Periodo" esté en formato de texto
df_filtered['Periodo'] = df_filtered['Periodo'].astype(str)

# Ordenar el DataFrame por "Periodo"
df_filtered = df_filtered.sort_values(by='Periodo')

# Convertir la columna 'v_m_IPC' a numérico, manejando las comas como decimales y NaNs
df_filtered['v_m_IPC'] = df_filtered['v_m_IPC'].str.replace(',', '.').astype(float)

# Mostrar las primeras filas después del filtrado y conversión para verificación
print(df_filtered.head())

# Verificar si el DataFrame tiene datos
if not df_filtered.empty:
    # Cálculo de estadísticas
    promedio_total = df_filtered['v_m_IPC'].mean()
    minimo_total = df_filtered['v_m_IPC'].min()
    maximo_total = df_filtered['v_m_IPC'].max()

    # Generar una proyección sencilla basada en la tendencia de los últimos 6 períodos
    ultimos_periodos = df_filtered['v_m_IPC'].tail(6)
    pendiente = np.polyfit(range(6), ultimos_periodos, 1)[0]  # Calcula la pendiente de los últimos 6 períodos
    proyeccion = [ultimos_periodos.iloc[-1] + pendiente * i for i in range(1, num_periodos_proyeccion + 1)]  # Proyección de los próximos N períodos

    # Crear los próximos N períodos según la cantidad que el usuario haya solicitado
    ult_periodo = df_filtered['Periodo'].iloc[-1]
    anio = int(ult_periodo[:4])
    mes = int(ult_periodo[4:])

    proximos_periodos = []
    for i in range(1, num_periodos_proyeccion + 1):
        mes += 1
        if mes > 12:
            mes = 1
            anio += 1
        proximos_periodos.append(f'{anio}{mes:02d}')

    # Añadir la proyección al DataFrame original para graficar
    df_proyeccion = pd.DataFrame({
        'Periodo': proximos_periodos,
        'v_m_IPC': proyeccion
    })

    df_total = pd.concat([df_filtered, df_proyeccion])

    # Graficar la variación mensual del IPC (v_m_IPC) en el eje Y y el periodo en el eje X
    plt.figure(figsize=(10, 6))

    # Usar un color atractivo y un estilo de línea más suave
    plt.plot(df_filtered['Periodo'], df_filtered['v_m_IPC'], marker='x', color='#74acdf', linestyle='-', linewidth=1, label='IPC Observado')

    # Graficar la proyección con línea punteada y color diferente
    plt.plot(df_proyeccion['Periodo'], df_proyeccion['v_m_IPC'], marker='x', color='lightslategray', linestyle='--', linewidth=1, label='Proyección')

    # Agregar sombreado al área bajo la curva
    plt.fill_between(df_filtered['Periodo'], df_filtered['v_m_IPC'], color='#aec7e8', alpha=0.3)

    # Título con más detalle y fuente más grande
    plt.title(f'Variación Mensual del IPC - NIVEL GENERAL (Región: Nacional)\nPeríodo: {periodo_desde} a {periodo_hasta}', fontsize=14, fontweight='bold')

    # Etiquetas de los ejes
    plt.xlabel('Periodo', fontsize=12)
    plt.ylabel('Variación Mensual del IPC (%)', fontsize=12)

    # Rotar etiquetas del eje X para mejor legibilidad
    plt.xticks(rotation=45, fontsize=10)
    plt.yticks(fontsize=10)

    # Añadir una línea de referencia en el valor 0 (con mayor grosor)
    plt.axhline(0, color='black', linestyle='-', linewidth=1)  # Ajuste del grosor de la línea en 0

    # Mejorar el estilo de las cuadrículas
    plt.grid(True, which='both', linestyle='--', linewidth=0.25, alpha=0.25)

    # Añadir líneas horizontales para el promedio, mínimo y máximo de todo el período
    plt.axhline(y=maximo_total, color='#a84a54', linestyle='--', linewidth=1.5, label=f'Máximo Histórico: {maximo_total:.2f}%')
    plt.axhline(y=minimo_total, color='#97c2dc', linestyle='--', linewidth=1.5, label=f'Mínimo Histórico: {minimo_total:.2f}%')
    plt.axhline(y=promedio_total, color='darkgray', linestyle='--', linewidth=1.5, label=f'Promedio Histórico: {promedio_total:.2f}%')

    # Añadir anotaciones de los valores en los puntos del gráfico para el IPC observado
    for i, v in enumerate(df_filtered['v_m_IPC']):
        plt.annotate(f'{v:.2f}', (df_filtered['Periodo'].iloc[i], v), textcoords="offset points", xytext=(0,5), ha='center', fontsize=8, color='#2f4f4f')

    # Añadir anotaciones de los valores en los puntos del gráfico para la proyección
    for i, v in enumerate(df_proyeccion['v_m_IPC']):
        plt.annotate(f'{v:.2f}', (df_proyeccion['Periodo'].iloc[i], v), textcoords="offset points", xytext=(0,5), ha='center', fontsize=8, color='#2f4f4f')

    # Ajustar el layout para evitar recortes
    plt.tight_layout()

    # Añadir leyenda
    plt.legend()

    # Definir la ruta donde se guardará la imagen
    image_path = 'images/inflation_graph.png'

    # Crear la carpeta static si no existe
    if not os.path.exists('images'):
        os.makedirs('images')

    # Guardar el gráfico como imagen en PNG, reemplazando si ya existe
    plt.savefig(image_path, format='png', dpi=300, bbox_inches='tight')

    # Mostrar un mensaje de confirmación
    print(f"El gráfico se ha guardado en {image_path}")

    # Mostrar el gráfico
    '''plt.show()'''

else:
    print("No se encontraron datos para los filtros aplicados.")