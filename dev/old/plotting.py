import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64


def get_plot(df, size=(15,3), title=''):
    img = BytesIO()
    plt.figure(figsize=size)
    plt.title(title)
    plt.plot(df)
    plt.legend(df.columns, loc='upper right', prop={'size': 8})
    plt.savefig(img, format='png')
    plt.close()
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')
    return plot_url