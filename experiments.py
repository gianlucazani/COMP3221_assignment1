import math
import queue

import numpy as np
import pandas as pd
import heapq as hq
from itertools import count

df2 = pd.DataFrame({'A': [0, 1, np.nan],
                    'B': [1.5, 0, np.nan],
                    'C': [0.5, 1, np.nan]},
                   index=['A', 'B', 'C'])

new = pd.Series(data=[1, 2, 3], index=['A', 'B', 'D'], name="D")
new_index = new.index.union(df2.index)
# new_df = df2.reindex(new_index, fill_value=np.nan)
# new_df[new.name] = new
# print(new_df)
# print(new_df["D"]["C"])
# print(new_df["D"])


dataframe1 = pd.DataFrame({'A': ["x", "x", "x"]},
                          index=['A', 'D', 'E'])

dataframe2 = pd.DataFrame({'B': ["y", "y", "y"],
                           'D': ["y", "y", "y"],
                           'F': ["y", "y", "y"]},
                          index=['A', 'D', 'E'])

dataframe3 = pd.DataFrame({'A': ["y", "y", "y"],
                           'D': ["y", "y", "y"],
                           'F': ["y", "y", "y"]},
                          index=['A', 'B', 'G'])

# print(dataframe1.compare(dataframe2))
print(dataframe1.combine_first(dataframe3))
print(list(set(dataframe2.index) - set(dataframe3.index)))


# # s = pd.Series(data=["z", "z", "z", "z", "z"], index=['A', 'B', 'E', 'G', 'H'])
# # dataframeresult = dataframe2.combine_first(dataframe1)
# # print(dataframeresult)
# # dataframeresult.fillna(np.inf, inplace=True)
# # print(dataframeresult)
#
#
# # DIJKSTRA
#
# network_topology = pd.DataFrame({'A': [0.0, 2.0, 1.0, np.inf, np.inf, np.inf],
#                                  'B': [2.0, 0.0, 2.0, 3.0, 1.0, np.inf],
#                                  'C': [1.0, 2.0, 0.0, 1.0, 4.0, np.inf],
#                                  'D': [np.inf, 3.0, 1.0, 0.0, 1.0, 3.0],
#                                  'E': [np.inf, 1.0, 4.0, 1.0, 0.0, 2.0],
#                                  'F': [np.inf, np.inf, np.inf, 3.0, 2.0, 0.0]},
#                                 index=["A", "B", "C", "D", "E", "F"])
#
# print("Network topology:")
# print(network_topology)
# possible_destinations = network_topology.index
#
# # Calculate shortest paths for A to each other node
#
# shortest_paths = dict()  # (key = destination, value = (cost, unique_identifier, {"id": node_id, "previous": previous}))
# shortest_paths["A"] = (0, "A")
# unique = count()  # resolves ties of dictionaries
# # initialize dictionary
# # for destination in possible_destinations:
# #    previous = "A"
# #    if network_topology["A"][destination] == np.inf:
# #        previous = ""
# #    shortest_paths[destination] = (
# #    network_topology["A"][destination], next(unique), {"id": destination, "previous": previous})
#
# print(shortest_paths)
#
# priority_queue = queue.PriorityQueue()  # priority queue initialization
# # fill priority queue, ties will be resolved thanks to the unique_identifier
#
# priority_queue.put((0.0, next(unique), {"id": "A", "previous": "A"}))
# for node_id in network_topology.index:
#     if node_id != "A":
#         shortest_paths[node_id] = (np.inf, None)
#         # priority_queue.put((np.inf, next(unique), {'id': node_id, 'previous': None}))
#
#
#
#
#
# # for key in shortest_paths:
#     # priority_queue.put(shortest_paths[key])
# visited = set()  # set of visited nodes (contains ids)
# # visited.add(
#     # "A")  # add "A" to visited nodes because in the priority queue its neighbours already have the distance from A, so it is like we already expanded A (in the initialization of the dictionary)
# print(priority_queue)
#
# # current_node = priority_queue.get()  # remove A from priority queue
# def get_neighbours(node_id):
#     return network_topology.index[network_topology[node_id] != np.inf].tolist()
#
#
# while not priority_queue.empty():
#     current_node = priority_queue.get()  # take highest priority node (lowest cost)
#     for neighbour in get_neighbours(current_node[2]['id']):  # for each possible destination (i.e. indexes of the network topology)
#         if not visited.__contains__(neighbour):  # if the destination node (value) has not been visited yet
#             distance_current_to_destination = network_topology[current_node[2]['id']][
#                 neighbour]  # save distance from current node to the destination node
#             # print(f"Distance from {current_node[2]['id']} to {neighbour}: {distance_current_to_destination}")
#             distance_start_to_current = shortest_paths[current_node[2]['id']][
#                 0]  # save value of distance from start to current node
#             priority_queue.put((distance_start_to_current, next(unique), {"id": neighbour, "previous": current_node[2]['id']}))
#             # print(f"Distance from A to {current_node[2]['id']}: {distance_start_to_current}")
#             if (distance_start_to_current + distance_current_to_destination) < shortest_paths[neighbour][0]:  # if distance to current + dustance from current to destination is lower than the previously stored distance from start to destination, replace value
#                 # replacing distance cost to destination node (value) with the sum of going to current node + current to destination
#                 shortest_paths[neighbour] = (
#                     distance_start_to_current + distance_current_to_destination, # distance
#                     current_node[2]['id'])
#                     # shortest_paths[neighbour][1],  # keep the unique identifier
#                     # {"id": neighbour,
#                     # "previous": current_node[2]['id']})  # update the previous node with the current node
#
#     visited.add(current_node[2]['id'])  # add current node to visited
#
# print(shortest_paths)
#
#
# def extract_path(shortest_paths_dict, start, to):
#     current_dest = to
#     result = ""
#     while shortest_paths_dict[current_dest][1] != start:
#         result = shortest_paths_dict[current_dest][1] + result
#         current_dest = shortest_paths_dict[current_dest][1]
#
#     return start + result + to
#
#
# for destination in possible_destinations:
#     if shortest_paths[destination][0] != np.inf:
#         print(f"Shortest path from A to {destination}: {shortest_paths[destination][0]} {extract_path(shortest_paths, 'A', destination)}")



