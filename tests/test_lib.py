from unittest import TestCase

import pandas as pd

from assignment1.lib import extract_path, received_new_information


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
