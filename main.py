import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def cohort_matrix(data, column_id_client, column_purchase_date, column_purchase_id, date_format='%d/%m/%Y'):
    """
    Extracts and transforms transaction data from an Excel file into a cohort matrix.
    The function loads the specified sheet, prepares the data, and creates a matrix where each row
    represents a cohort (month of the first purchase) and each column the months since the first purchase.
    The values in the matrix show the number of unique customers who made a purchase in that
    particular month since their first purchase.

    :type column_id_client: str
    :param column_id_client: Name of the column containing the client IDs

    :type column_purchase_date: str
    :param column_purchase_date: Name of the column containing transaction dates

    :type column_purchase_id: str
    :param column_purchase_id: Name of the column containing the data to be analyzed

    :returns: A DataFrame representing the cohort matrix
    :rtype: pandas.DataFrame
    """

    # Check if columns exists
    if column_id_client not in data.columns or column_purchase_date not in data.columns or column_purchase_id not in data.columns:
        raise ValueError("Columns do not exist.")

    # Fomat and clean nans
    data = data[[column_id_client, column_purchase_date, column_purchase_id]]
    data = data.dropna()

    # Date format and cleaning
    data[column_purchase_date] = pd.to_datetime(data[column_purchase_date], errors='coerce', format=date_format)
    data = data.dropna(subset=[column_purchase_date])
    data['month_purchase'] = data[column_purchase_date].dt.to_period('M')

    # Sort cleints by cohort
    first_purchase = data.groupby(column_id_client)['month_purchase'].min()
    first_purchase.name = 'cohort'
    data = data.merge(first_purchase.reset_index(), on=column_id_client)

    # Month difference
    data['month_diff'] = data.apply(lambda x: (x['month_purchase'] - x['cohort']).n, axis=1)

    # Make matrix
    cohort_matrix = data.groupby(['cohort', 'month_diff']).agg(n_clients=(column_id_client, 'nunique')).reset_index()
    cohort_matrix = cohort_matrix.pivot(index='cohort', columns='month_diff', values='n_clients')

    return cohort_matrix


def plot(cohort_matrix, plot_title='Cohort Analysis', y_label='Cohort (Month of first Purchase)', x_label='Months since first purchase', fig_size=(15, 8), colormap='Reds'):
    """
    Plot the cohort matrix using data from `load_cohort_data`.
    Each cell in the heatmap shows the number of unique customers who made a purchase
    in a given month since their first purchase.

    :type cohort_matrix: pandas.DataFrame
    :param cohort_matrix: DataFrame representing the cohort matrix

    :type colormap: str
    :param colormap: Color map as available in `matplotlib`.

    :returns: Does not return anything, only plots.
    """

    fig, ax = plt.subplots(figsize=fig_size)

    cax = ax.matshow(cohort_matrix, interpolation='nearest', cmap=colormap)

    plt.title(plot_title)
    plt.ylabel(y_label)
    plt.xlabel(x_label)

    # Cohort names
    ax.set_yticks(np.arange(cohort_matrix.shape[0]))
    ax.set_yticklabels(cohort_matrix.index.strftime('%Y-%m'))

    # Months since purchase
    ax.set_xticks(np.arange(cohort_matrix.shape[1]))
    ax.set_xticklabels(cohort_matrix.columns)
    ax.xaxis.set_ticks_position('bottom')

    # Values
    for (i, j), val in np.ndenumerate(cohort_matrix):
        ax.text(j, i, int(val) if not np.isnan(val) else '', ha='center', va='center')

    plt.show()
