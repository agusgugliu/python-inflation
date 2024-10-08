import requests
import zipfile
import io
import os
import pandas as pd
import matplotlib.pyplot as plt

#Selección de país a analizar
highlight_country = input('Ingrese país a resaltar:\t')
highlight_country = str(highlight_country)

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

    # Limpiar las columnas, eliminando las innecesarias y las que no contienen valores numéricos
    df_years = df.iloc[:, 4:-1]

    # Eliminar columnas con todos los valores NaN
    df_years_clean = df_years.dropna(axis=1, how='all')

    # Convertir los índices (años) a enteros y los valores a numéricos
    df_clean = df_years_clean.T.dropna(how='all')
    df_clean.columns = df['Country Name']

    # Calcular el promedio global anual (promedio por año)
    global_average = df_clean.mean(axis=1)

    # Crear el gráfico de la evolución anual del desempleo para todos los países
    plt.figure(figsize=(14, 8))

    # Graficar todos los países con líneas grises y sutiles
    for country in df_clean.columns:
        plt.plot(df_clean.index.astype(int), df_clean[country], color='lightgray', alpha=0.3, linewidth=0.5)

    # Resaltar la línea de Resaltado con marcadores y línea más gruesa
    if highlight_country in df_clean.columns:
        years = df_clean.index.astype(int)
        unemployment_rate_arg = df_clean[highlight_country]
        plt.plot(years, unemployment_rate_arg, marker="x", color='#74acdf', label=highlight_country, linewidth=1.5, markersize=4)

        # Mostrar los valores para Resaltado sobre cada punto
        for i, year in enumerate(years):
            plt.annotate(f'{unemployment_rate_arg[i]:.1f}', 
                         (year, unemployment_rate_arg[i]), 
                         textcoords="offset points", 
                         xytext=(0, 10),  # Desplazar el texto 10 puntos hacia arriba
                         ha='center', fontsize=9, color='#0e2246')

    # Graficar el promedio global anual con una línea punteada
    plt.plot(df_clean.index.astype(int), global_average, color='slategray', linestyle='--', label='Promedio Global', linewidth=1.2)

    # Mostrar los valores para el promedio global sobre cada punto
    for i, year in enumerate(years):
        plt.annotate(f'{global_average[i]:.1f}', 
                     (year, global_average[i]), 
                     textcoords="offset points", 
                     xytext=(0, -10),  # Desplazar el texto 10 puntos hacia abajo
                     ha='center', fontsize=9, color='slategray')

    # Personalizar el gráfico
    plt.title(f'Evolución del Desempleo en Todos los Países (%) \n(Resaltado: {highlight_country} y Promedio Global)', fontsize=18, fontweight='bold')
    plt.xlabel('Año', fontsize=14)
    plt.ylabel('Tasa de Desempleo (%)', fontsize=14)
    
    # Personalizar la cuadrícula
    plt.grid(True, which='both', linestyle=':', linewidth=0.3, alpha=0.7, color="#97c2dc")

    # Aumentar el tamaño de los ticks
    plt.xticks(rotation=45, fontsize=12)
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