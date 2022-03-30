from unittest import TestCase

import numpy as np
import pandas as pd
from assignment1.lib import received_new_information


def seen_before(network_topology_history, update):
    for nt in network_topology_history:
        different_shape, link_cost_changed = received_new_information(nt, update)
        if not different_shape and not link_cost_changed:
            return True
    return False


class TestNode(TestCase):

    def test_seen_before(self):

        dataframe1 = pd.DataFrame({'B': [1.0, 0.0, 0.0],
                                   'D': [0.0, np.nan, np.nan],
                                   'F': [0.0, np.nan, 0.0]},
                                  index=['A', 'B', 'E'])

        dataframe2 = pd.DataFrame({'B': [100.0, 0.0, 0.0],
                                   'D': [0.0, np.nan, np.nan],
                                   'F': [0.0, np.nan, 0.0]},
                                  index=['A', 'B', 'E'])

        dataframe3 = pd.DataFrame({'B': [0.0, 0.0, 0.0],
                                   'D': [0.0, np.nan, np.nan],
                                   'F': [0.0, np.nan, 0.0]},
                                  index=['A', 'B', 'E'])

        dataframe4 = pd.DataFrame({'B': [1.0, 0.0, 0.0],
                                   'D': [0.0, np.nan, np.nan],
                                   'F': [0.0, np.nan, 0.0]},
                                  index=['A', 'B', 'E'])

        history = list()
        history.append(dataframe1)
        history.append(dataframe2)

        self.assertEqual(seen_before(history, dataframe3), False)
        self.assertEqual(seen_before(history, dataframe4), True)


        update1
