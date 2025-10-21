# 在 core/processor/gaf_processor.py

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class GAFProcessor:
    def __init__(self, column_name='Close'):
        """
        Initialize the GAFProcessor with the specific column to be used for GAF transformation.
        """
        self.column_name = column_name

    @staticmethod
    def _normalize_data(data):
        """ Normalize the data to the range [-1, 1]. """
        max_val = np.max(data)
        min_val = np.min(data)
        return 2 * (data - min_val) / (max_val - min_val) - 1

    @staticmethod
    def _polar_coordinates(data):
        """ Convert the data to polar coordinates. """
        return np.arccos(data), np.arange(len(data))

    @staticmethod
    def _gaf_transformation(data):
        """ Perform the GAF transformation. """
        cos_values, theta = GAFProcessor._polar_coordinates(data)
        gaf = np.outer(cos_values, cos_values)
        return gaf

    def process_data(self, df: pd.DataFrame):
        """
        Processes the input DataFrame using GAF transformation and returns the transformed data.
        """
        if self.column_name in df.columns:
            data = df[self.column_name].values
            normalized_data = self._normalize_data(data)
            gaf = self._gaf_transformation(normalized_data)

            # Optional: Plotting the GAF (for visualization and debugging)
            plt.imshow(gaf, cmap='hot', interpolation='nearest')
            plt.title(f'Gramian Angular Field')
            plt.show()
            plt.close()

            return gaf
        else:
            print(f'No "{self.column_name}" column found in DataFrame')
            return None
