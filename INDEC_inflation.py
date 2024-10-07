import requests
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Crear la subcarpeta "DATA_ipc" si no existe
folder_path = 'DATA_ipc'
if not os.path.exists(folder_path):
    os.makedirs(folder_path)

# Definir la ruta completa del archivo dentro de la subcarpeta
file_path = os.path.join(folder_path, 'DATA_indec_ipc.csv')

# URL del archivo CSV
url = 'https://www.indec.gob.ar/ftp/cuadros/economia/serie_ipc_divisiones.csv'

# Descargar el archivo CSV
response = requests.get(url)
csv_content = response.content.decode('latin1')

# Guardar el contenido del CSV en el archivo dentro de la subcarpeta
with open(file_path, 'w', encoding='latin1') as file:
    file.write(csv_content)

# Leer el archivo CSV con el delimitador correcto
df = pd.read_csv(file_path, encoding='latin1', delimiter=';')

# Solicitar al usuario ingresar el rango de periodos como texto
periodo_desde = input("Ingrese el periodo DESDE (formato YYYYMM): ")
periodo_hasta = input("Ingrese el periodo HASTA (formato YYYYMM): ")

# Solicitar al usuario cuántos períodos proyectar
num_periodos_proyeccion = int(input("¿Cuántos períodos desea proyectar hacia adelante? "))

# Asegurarse de que la columna "Periodo" esté en formato de texto
df['Periodo'] = df['Periodo'].astype(str)

# Filtrar los datos según los criterios: Descripcion = "NIVEL GENERAL", Region = "Nacional" y en el rango de periodos
df_filtered = df[
    (df['Descripcion'] == 'NIVEL GENERAL') & 
    (df['Region'] == 'Nacional') & 
    (df['Periodo'] >= periodo_desde) & 
    (df['Periodo'] <= periodo_hasta)
]

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
    image_path = 'world_data/static/inflation_graph.png'

    # Crear la carpeta static si no existe
    if not os.path.exists('world_data/static'):
        os.makedirs('world_data/static')

    # Guardar el gráfico como imagen en PNG, reemplazando si ya existe
    plt.savefig(image_path, format='png', dpi=300, bbox_inches='tight')

    # Mostrar un mensaje de confirmación
    print(f"El gráfico se ha guardado en {image_path}")


    # Mostrar el gráfico
    '''plt.show()'''
    
else:
    print("No se encontraron datos para los filtros aplicados.")