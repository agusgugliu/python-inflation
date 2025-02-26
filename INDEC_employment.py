import requests
import zipfile
import io
import os
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
import shutil
import argparse

# Configurar argparse para manejar los argumentos de línea de comandos
parser = argparse.ArgumentParser(description='Script to analyze employment data and highlight a specific country.')
parser.add_argument('highlight_country', type=str, help='Country to highlight in the graph')
parser.add_argument('year_from', type=int, help='Start year for the graph (YYYY)')
parser.add_argument('year_until', type=int, help='End year for the graph (YYYY)')
args = parser.parse_args()

# Selección de país a analizar y rango de años
highlight_country = args.highlight_country
year_from = args.year_from
year_until = args.year_until

# Puedes usar cualquier estilo disponible en tu instalación de Matplotlib
plt.style.use('ggplot')  # O elimina esta línea si prefieres el estilo por defecto

# URL del archivo CSV comprimido
url = 'https://api.worldbank.org/v2/es/indicator/SL.UEM.TOTL.ZS?downloadformat=csv&_gl=1*1amqro9*_gcl_au*MTU3Njg1MzAxOS4xNzI2MTgzMTYy'

# Descargar el archivo ZIP
response = requests.get(url)

# Verificar si la descarga fue exitosa
if response.status_code == 200:
    # Obtener el directorio donde se encuentra el script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Crear un directorio temporal en la misma ubicación del script
    temp_dir = os.path.join(script_dir, 'DATA_empleo')
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    # Extraer el contenido del ZIP
    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        for file_name in z.namelist():
            # Renombrar los archivos para que empiecen con DATA_empleo
            new_file_name = f"DATA_empleo_{file_name}"
            if os.path.exists(os.path.join(temp_dir, new_file_name)):
                # Si el archivo ya existe, lo eliminamos
                os.remove(os.path.join(temp_dir, new_file_name))
            
            # Extraer y renombrar el archivo
            z.extract(file_name, temp_dir)
            os.rename(os.path.join(temp_dir, file_name), os.path.join(temp_dir, new_file_name))

    # Eliminar los archivos que contienen "Metadata"
    for file in os.listdir(temp_dir):
        if "Metadata" in file:
            os.remove(os.path.join(temp_dir, file))

    # Encontrar el archivo CSV que se extrajo, ignorando los archivos que contienen "Metadata"
    csv_file = [file for file in os.listdir(temp_dir) if file.startswith('DATA_empleo') and file.endswith('.csv') and 'Metadata' not in file][0]

    # Cargar el archivo CSV en un DataFrame
    df = pd.read_csv(os.path.join(temp_dir, csv_file), skiprows=4)

    # Conectar a la base de datos SQLite
    db_path = os.path.join('databases', 'social_indicators.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Crear la tabla FT_world_employment si no existe
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS FT_world_employment (
        Country_Name TEXT,
        Country_Code TEXT,
        Indicator_Name TEXT,
        Indicator_Code TEXT,
        Year INTEGER,
        Value REAL
    )
    ''')

    # Insertar los datos del DataFrame en la tabla FT_world_employment
    for index, row in df.iterrows():
        for year in range(1960, 2022):
            if not pd.isna(row[str(year)]):
                cursor.execute('''
                INSERT INTO FT_world_employment (Country_Name, Country_Code, Indicator_Name, Indicator_Code, Year, Value)
                VALUES (?, ?, ?, ?, ?, ?)
                ''', (row['Country Name'], row['Country Code'], row['Indicator Name'], row['Indicator Code'], year, row[str(year)]))

    # Confirmar la inserción
    conn.commit()

    # Cerrar la conexión a la base de datos
    conn.close()

    # Eliminar la carpeta DATA_empleo y su contenido si existe
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
        print(f"Carpeta {temp_dir} eliminada con éxito")

    # Limpiar las columnas, eliminando las innecesarias y las que no contienen valores numéricos
    df_years = df.iloc[:, 4:-1]

    # Eliminar columnas con todos los valores NaN
    df_years_clean = df_years.dropna(axis=1, how='all')

    # Convertir los índices (años) a enteros y los valores a numéricos
    df_clean = df_years_clean.T.dropna(how='all')
    df_clean.columns = df['Country Name']

    # Filtrar los datos según el rango de años proporcionado
    df_clean = df_clean.loc[str(year_from):str(year_until)]

    # Asegurarse de que los índices sean enteros
    df_clean.index = df_clean.index.astype(int)

    # Calcular el promedio global anual (promedio por año)
    global_average = df_clean.mean(axis=1)

    # Identificar el país con el índice de desempleo más alto en el último período
    last_year = df_clean.index[-1]
    max_unemployment_country = df_clean.loc[last_year].idxmax()
    max_unemployment_value = df_clean.loc[last_year].max()

    # Identificar el país con el índice de desempleo más bajo en el último período
    min_unemployment_country = df_clean.loc[last_year].idxmin()
    min_unemployment_value = df_clean.loc[last_year].min()

    # Crear el gráfico de la evolución anual del desempleo para todos los países
    plt.figure(figsize=(14, 8))

    # Graficar todos los países con líneas grises y sutiles
    for country in df_clean.columns:
        plt.plot(df_clean.index, df_clean[country], color='lightgray', alpha=0.3, linewidth=0.5)

    # Resaltar la línea de Resaltado con marcadores y línea más gruesa
    if highlight_country in df_clean.columns:
        years = df_clean.index
        unemployment_rate_arg = df_clean[highlight_country]
        plt.plot(years, unemployment_rate_arg, marker="x", color='#74acdf', label=highlight_country, linewidth=1.5, markersize=4)

        # Mostrar los valores para Resaltado sobre cada punto
        for i, year in enumerate(years):
            plt.annotate(f'{unemployment_rate_arg.iloc[i]:.1f}', 
                         (year, unemployment_rate_arg.iloc[i]), 
                         textcoords="offset points", 
                         xytext=(0, 10),  # Desplazar el texto 10 puntos hacia arriba
                         ha='center', fontsize=9, color='#0e2246')

    # Resaltar el país con el índice de desempleo más alto en el último período
    if max_unemployment_country in df_clean.columns:
        max_unemployment_rate = df_clean[max_unemployment_country]
        plt.plot(df_clean.index, max_unemployment_rate, marker="o", color='red', label=f'Peor Desempleo: {max_unemployment_country}', linewidth=2, markersize=6)

        # Mostrar los valores para el país con el peor desempleo sobre cada punto
        for i, year in enumerate(years):
            plt.annotate(f'{max_unemployment_rate.iloc[i]:.1f}', 
                         (year, max_unemployment_rate.iloc[i]), 
                         textcoords="offset points", 
                         xytext=(0, 10),  # Desplazar el texto 10 puntos hacia arriba
                         ha='center', fontsize=9, color='red')

    # Resaltar el país con el índice de desempleo más bajo en el último período
    if min_unemployment_country in df_clean.columns:
        min_unemployment_rate = df_clean[min_unemployment_country]
        plt.plot(df_clean.index, min_unemployment_rate, marker="o", color='green', label=f'Mejor Desempleo: {min_unemployment_country}', linewidth=2, markersize=6)

        # Mostrar los valores para el país con el mejor desempleo sobre cada punto
        for i, year in enumerate(years):
            plt.annotate(f'{min_unemployment_rate.iloc[i]:.1f}', 
                         (year, min_unemployment_rate.iloc[i]), 
                         textcoords="offset points", 
                         xytext=(0, 10),  # Desplazar el texto 10 puntos hacia arriba
                         ha='center', fontsize=9, color='green')

    # Graficar el promedio global anual con una línea punteada
    plt.plot(df_clean.index, global_average, color='slategray', linestyle='--', label='Promedio Global', linewidth=1.2)

    # Mostrar los valores para el promedio global sobre cada punto
    for i, year in enumerate(global_average.index):
        plt.annotate(f'{global_average.iloc[i]:.1f}', 
                     (year, global_average.iloc[i]), 
                     textcoords="offset points", 
                     xytext=(0, -10),  # Desplazar el texto 10 puntos hacia abajo
                     ha='center', fontsize=9, color='slategray')

    # Personalizar el gráfico
    plt.title(f'Evolución del Desempleo en Todos los Países (%) \n(Resaltado: {highlight_country}, Peor Desempleo: {max_unemployment_country}, Mejor Desempleo: {min_unemployment_country} y Promedio Global)', fontsize=18, fontweight='bold')
    plt.xlabel('Año', fontsize=14)
    plt.ylabel('Tasa de Desempleo (%)', fontsize=14)
    
    # Personalizar la cuadrícula
    plt.grid(True, which='both', linestyle=':', linewidth=0.3, alpha=0.7, color="#97c2dc")

    # Aumentar el tamaño de los ticks
    plt.xticks(rotation=90, fontsize=12)
    plt.yticks(fontsize=12)

    # Añadir sombra al gráfico
    plt.gca().patch.set_alpha(0.1)

    # Mostrar la leyenda
    plt.legend(fontsize=12)

    # Ajustar el diseño del gráfico
    plt.tight_layout()
    
    # Definir la ruta donde se guardará la imagen
    image_path = 'images/employment_graph.png'

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
    print("Error al descargar el archivo.")