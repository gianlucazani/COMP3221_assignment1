import numpy as np


def received_new_information(network_topology, update):
    """
    Check whether the update packet brings real updates or it is just a redundant DataFrame that contains no more information
    than the node network_topology
    :param network_topology: Node network topology before the update
    :param update: Update packet sent by neighbours
    :return: Two booleans, the first is true if the two DataFrames are different in shape (i.e. different columns and rows index), the second
    is true if the two DataFrames are equal in shape but differ for one or more cell values (this occurs when a link cost is changed after first convergence)
    """
    # the DataFrame.compare() method returns a DataFrame containing the differences, so if it is empty, no new information arrived
    updated = update.combine_first(network_topology)
    updated_cols = list(updated.columns)
    updated_rows = list(updated.index.values)
    old_cols = list(network_topology.columns)
    old_rows = list(network_topology.index.values)
    different_shape = updated_cols != old_cols or updated_rows != old_rows
    if not different_shape:

        for col in updated_cols:
            for row in updated_rows:
                if not (np.isnan(network_topology[col][row]) and np.isnan(updated[col][row])) \
                        and (np.isnan(network_topology[col][row]) or np.isnan(updated[col][row])) \
                        and network_topology[col][row] != updated[col][row]:
                    return False, True
        return True, False
        # rows_with_not_matching_cells = update.combine_first(network_topology)[network_topology.ne(update.combine_first(network_topology)).any(axis=1)]
        # print(rows_with_not_matching_cells)
        # return not rows_with_not_matching_cells.empty
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
