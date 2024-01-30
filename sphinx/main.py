import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def cargar_datos_cohorte(dir_archivo, nombre_hoja, columna_id_cliente, columna_fecha_transaccion, columna_datos):
    """
    Extrae y transforma los datos de transacciones de un archivo Excel en una matriz de cohortes.
    La función carga la hoja especificada, prepara los datos y crea una matriz donde cada fila
    representa una cohorte (mes de la primera compra) y cada columna los meses desde la primera compra.
    Los valores en la matriz muestran el número de clientes únicos que realizaron una compra en ese
    mes particular desde su primera compra.

    :type dir_archivo: str
    :param dir_archivo: Directorio del archivo Excel que contiene los datos de transacciones

    :type nombre_hoja: str
    :param nombre_hoja: Nombre de la hoja en el archivo Excel a procesar

    :type columna_id_cliente: str
    :param columna_id_cliente: Nombre de la columna que contiene los ID de los clientes

    :type columna_fecha_transaccion: str
    :param columna_fecha_transaccion: Nombre de la columna que contiene las fechas de las transacciones

    :type columna_datos: str
    :param columna_datos: Nombre de la columna que contiene los datos a analizar

    :returns: Un DataFrame que representa la matriz de cohortes
    :rtype: pandas.DataFrame
    """
    # Cargar la hoja especificada del archivo Excel
    transacciones = pd.read_excel(dir_archivo, sheet_name=nombre_hoja)

    # Asegurar que las columnas necesarias estén presentes
    if columna_id_cliente not in transacciones.columns or columna_fecha_transaccion not in transacciones.columns or columna_datos not in transacciones.columns:
        raise ValueError("Las columnas especificadas no se encuentran en los datos")

    # Formatear y limpiar los datos
    transacciones = transacciones[[columna_id_cliente, columna_fecha_transaccion, columna_datos]]
    transacciones = transacciones.dropna()
    transacciones[columna_fecha_transaccion] = pd.to_datetime(transacciones[columna_fecha_transaccion])
    transacciones['mes_transaccion'] = transacciones[columna_fecha_transaccion].dt.to_period('M')

    # Determinar el grupo de cohorte para cada cliente
    primera_transaccion = transacciones.groupby(columna_id_cliente)['mes_transaccion'].min()
    primera_transaccion.name = 'cohorte'
    transacciones = transacciones.merge(primera_transaccion.reset_index(), on=columna_id_cliente)

    # Calcular la diferencia en meses para cada transacción
    transacciones['diferencia_mes'] = transacciones.apply(lambda x: (x['mes_transaccion'] - x['cohorte']).n, axis=1)

    # Crear la matriz de cohorte
    matriz_cohorte = transacciones.groupby(['cohorte', 'diferencia_mes']).agg(n_clientes=(columna_id_cliente, 'nunique')).reset_index()
    matriz_cohorte = matriz_cohorte.pivot(index='cohorte', columns='diferencia_mes', values='n_clientes')

    return matriz_cohorte


def graficar_matriz_cohorte(matriz_cohorte, colormap='Reds'):
    """
    Grafica una matriz de cohortes utilizando los datos desde `cargar_datos_cohorte`.
    Cada celda en el mapa de calor muestra el número de clientes únicos que realizaron una compra
    en un mes determinado desde su primera compra.

    :type matriz_cohorte: pandas.DataFrame
    :param matriz_cohorte: DataFrame que representa la matriz de cohortes

    :returns: No retorna nada, solo muestra un gráfico.
    """

    fig, ax = plt.subplots(figsize=(15, 8))

    cax = ax.matshow(matriz_cohorte, interpolation='nearest', cmap=colormap)

    plt.title('Análisis de Cohortes')
    plt.ylabel('Cohorte (Mes de Primera Compra)')
    plt.xlabel('Meses Desde la Primera Compra')

    # Nombre de los cohortes
    ax.set_yticks(np.arange(matriz_cohorte.shape[0]))
    ax.set_yticklabels(matriz_cohorte.index.strftime('%Y-%m'))

    # Meses desde la compra
    ax.set_xticks(np.arange(matriz_cohorte.shape[1]))
    ax.set_xticklabels(matriz_cohorte.columns)
    ax.xaxis.set_ticks_position('bottom')

    # Agregar valores
    for (i, j), val in np.ndenumerate(matriz_cohorte):
        ax.text(j, i, int(val) if not np.isnan(val) else '', ha='center', va='center')

    plt.show()