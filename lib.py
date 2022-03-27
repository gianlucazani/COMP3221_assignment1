import numpy as np


def received_new_information(old, new):
    """
    Check whether the update packet brings real updates or it is just a redundant DataFrame that contains no more information
    than the node network_topology. It will check both difference in chape (new nodes joined, new nodes can be reached, ...) and
    if there are differences in costs when shape is the same.
    :param old: Node network topology before the update
    :param new: Update packet sent by neighbours
    :return: Two booleans, the first is true if the two DataFrames are different in shape (i.e. different columns and rows index), the second
    is true if the two DataFrames are equal in shape but differ for one or more cell values (this occurs when a link cost is changed after first convergence)
    """
    new_cols = list(new.columns)
    new_rows = list(new.index.values)
    old_cols = list(old.columns)
    old_rows = list(old.index.values)
    different_shape = new_cols != old_cols or new_rows != old_rows
    if not different_shape:

        for col in new_cols:
            for row in new_rows:
                nt_value = old[col][row]
                up_value = new[col][row]
                if (nt_value == nt_value) or (up_value == up_value):
                    if nt_value != up_value:
                        return False, True
        return False, False
    else:
        return True, False


def get_neighbours(node_id, network_topology):
    """
    :param node_id: node id of which we want to discover neighbours
    :param network_topology: DataFrame containing network topology
    :return: neighbours ids as a list
    """
    neighbours = network_topology.index[network_topology[
                                            node_id] != np.inf].tolist()  # indexes of nodes which distance from node_id is not +inf (i.e. neighbours)
    if neighbours.__len__() > 1:
        neighbours.remove(node_id)
    return neighbours


def extract_path(shortest_paths_dict, _from, _to):
    """
    Travels backwards from destination (to) to start node saving previous nodes until builds the complete path
    :param shortest_paths_dict: node dictionary containing shortest path information as (key: destination_id, value: (cost_to_dest, previous_node))
    :param _from: start node we want to get the paths to destinations
    :param _to: destination node id
    :return: string of subsequent nodes from starting node for reaching destination
    """
    if _from == _to:
        return _from
    else:
        return extract_path(shortest_paths_dict, _from, shortest_paths_dict[_to][1]) + _to
