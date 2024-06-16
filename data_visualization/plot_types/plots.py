from seaborn import (
    scatterplot,
    histplot,
    boxplot,
    countplot,
    barplot,
)
from matplotlib.pyplot import Axes
from pandas import DataFrame
from typing import Any

class CustomPlots:
    """
    Provides custom plotting functions for histograms and counts,
    enhancing them with bar labels for better readability.
    """
    def histogram(data: DataFrame = None, x: str = None, y:str = None, hue: str = None) -> Axes:
        ax = histplot(data=data, x=x, y=y, hue=hue, multiple= 'stack')
        for container in ax.containers:
            ax.bar_label(container, label_type= 'center')
        return ax

    def count(data: DataFrame = None, x: str = None, y:str = None, hue: str = None) -> Axes:
        ax = countplot(data=data, x=x, y=y, hue=hue)
        for container in ax.containers:
            ax.bar_label(container, label_type= 'center')
        return ax

class Plots:
    """
    Provides a centralized interface for creating various plot types,
    delegating the actual plotting to appropriate functions.
    """

    _PLOTS: dict[str, Any] = {
        'Scatter': scatterplot,
        'Histogram': CustomPlots.histogram,
        'Box': boxplot,
        'Count': CustomPlots.count,
        'Bar': barplot,
    }

    def __init__(self, plot_type: str = None) -> None:
        self.plot_type = plot_type

    def plot(self, data: DataFrame, x: str = None, y: str = None, hue: str = None) -> Axes:
        """
        Creates the specified plot type using the provided data and arguments.

        Args:
            data: The DataFrame containing the data to plot.
            x: The name of the column for the x-axis.
            y: The name of the column for the y-axis.
            hue: The name of the column to use for grouping by hue.

        Returns:
            The Axes object containing the generated plot.
        """
        ax = self._PLOTS[self.plot_type](data= data, x= x, y= y, hue= hue)
        return ax


