import numpy as np


def received_new_information(network_topology, update):
    """
    Check whether the update packet brings real updates or it is just a redundant DataFrame that contains no more information
    than the node network_topology
    :param network_topology: Node network topology before the update
    :param update: Update packet sent by neighbours
    :return: True if new information contained in update, False if no new information
    """
    try:
        # the DataFrame.compare() method retruns a DataFrame containing the differences, so if it is empty, no new information arrived
        differences = network_topology.compare(update.combine_first(network_topology))
        return not differences.empty
    except ValueError as ve:
        # the DataFrame.compare() method raises ValueError if the two dataframes have not the same shape
        # In this scope, not having the same shape means that the updated dataframe contains more information than the old one
        # So return True
        return True


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


def extract_path(shortest_paths_dict, start, to):
    """
    Travels backwards from destination (to) to start node saving previous nodes until builds the complete path
    :param shortest_paths_dict: node dictionary containing shortest path information as (key: destination_id, value: (cost_to_dest, previous_node))
    :param start: start node we want to get the paths to destinations
    :param to: destination node id
    :return: string of subsequent nodes from starting node for reaching destination
    """
    if start == to:
        return start
    else:
        return extract_path(shortest_paths_dict, start, shortest_paths_dict[to][1]) + to
