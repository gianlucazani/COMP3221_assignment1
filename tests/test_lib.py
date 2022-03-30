from unittest import TestCase

import numpy as np
import pandas as pd

from assignment1.lib import extract_path, received_new_information, remove_failed


class Test(TestCase):
    def test_extract_path(self):
        self.assertEqual(extract_path(
            {'A': (0.0, 'A'), 'B': (2.0, 'A'), 'C': (1.0, 'A'), 'D': (2.0, 'C'), 'E': (3.0, 'B'), 'F': (5.0, 'D')}, "A",
            "F"), "ACDF")

    def test_new_information(self):
        dataframe1 = pd.DataFrame({'A': ["x", "x", "x"]},
                                  index=['A', 'D', 'E'])

        dataframe2 = pd.DataFrame({'B': ["y", "y", "y"],
                                   'D': ["y", "y", "y"],
                                   'F': ["y", "y", "y"]},
                                  index=['A', 'B', 'E'])

        dataframe3 = pd.DataFrame({'B': ["y", "y", "y"],
                                   'D': ["y", "y", "y"],
                                   'F': ["y", "y", "y"]},
                                  index=['A', 'B', 'E'])

        self.assertEqual(received_new_information(dataframe2, dataframe1), True)
        self.assertEqual(received_new_information(dataframe1, dataframe2), True)
        self.assertEqual(received_new_information(dataframe2, dataframe3), False)

    def test_received_new_information(self):
        dataframe1 = pd.DataFrame({'B': [0.0, 0.0, 0.0],
                                   'D': [0.0, np.nan, np.nan],
                                   'F': [0.0, np.nan, 0.0]},
                                  index=['A', 'B', 'E'])

        dataframe2 = pd.DataFrame({'B': [100.0, 0.0, 0.0],
                                   'D': [0.0, np.nan, np.nan],
                                   'F': [0.0, np.nan, 0.0]},
                                  index=['A', 'B', 'E'])

        different_shape, different_cell = received_new_information(dataframe1, dataframe2.combine_first(dataframe1))
        self.assertEqual(different_shape, False)
        self.assertEqual(different_cell, True)

        dataframe1 = pd.DataFrame({'B': [0.0, 0.0, 0.0],
                                   'D': [0.0, np.nan, np.nan],
                                   'F': [0.0, np.nan, 0.0]},
                                  index=['A', 'B', 'E'])

        dataframe2 = pd.DataFrame({'B': [0.0, 0.0, 0.0],
                                   'D': [0.0, np.nan, np.nan],
                                   'F': [0.0, np.nan, 0.0]},
                                  index=['A', 'B', 'E'])

        different_shape, different_cell = received_new_information(dataframe1, dataframe2.combine_first(dataframe1))
        self.assertEqual(different_shape, False)
        self.assertEqual(different_cell, False)

    def test_remove_failed(self):
        dataframe1 = pd.DataFrame({'B': [0.0, np.inf, 0.0],
                                   'D': [np.inf, np.inf, np.inf],
                                   'F': [0.0, np.inf, 0.0]},
                                  index=['A', 'B', 'E'])

        dataframe2 = pd.DataFrame({'B': [0.0, 0.0],
                                   'F': [0.0, 0.0]},
                                  index=['A', 'E'])
        check1, check2 = received_new_information(remove_failed(dataframe1), dataframe2)
        self.assertEqual(check1, False)
        self.assertEqual(check2, False)
