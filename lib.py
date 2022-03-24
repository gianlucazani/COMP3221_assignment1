import numpy as np


def get_neighbours(node_id, network_topology):
    """
    :param node_id: node id of which we want to discover neighbours
    :param network_topology: DataFrame containing network topology
    :return: neighbours ids as a list
    """
    neighbours = network_topology.index[network_topology[node_id] != np.inf].tolist()  # returns indexes of nodes which distance from node_id is not +inf (i.e. neighbours)
    # print(f"Neighbours of {node_id}: {neighbours}")
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
