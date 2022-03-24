import queue
import threading
import socket
import time
import numpy as np
import pandas as pd
from itertools import count
from lib import extract_path, get_neighbours

HOST = "127.0.0.1"


class Timer(threading.Thread):
    def __init__(self, duration, action):
        super().__init__()
        self.duration = duration
        self.action = action

    def run(self):
        """
        After self.duration performs self.action
        """
        time.sleep(self.duration)
        self.action()


class PathFinder(threading.Thread):
    def __init__(self, node):
        super().__init__()
        self.node = node
        self.paused = True

    def run(self):  # runs Dijkstra shortest path algorithm
        """
        This thread runs the Dijkstra's shortest path finding algorithm
        """
        # ------- SET UP -------

        network_topology = self.node.network_topology.copy()  # save node network topology as a copy so that the original can be modified while the algorithm is running
        network_topology.fillna(np.inf, inplace=True)  # replace NaN values with +inf
        # print(network_topology)
        # DEL possible_destinations = network_topology.index  # save all possible destinations in a list as node ids, it will contain only the ids discovered so far
        unique_identifier = count()  # resolves ties when sorting dictionaries in priority queue
        shortest_paths = self.node.shortest_paths
        # shortest_paths = dict()  # (key = destination_node_id, value = (cost, unique_identifier, {"id": destination_id, "previous": previous_node}))

        # shortest_paths[self.node.node_id] = (0.0, self.node.node_id)
        # Initialize shortest_paths with node neighbours information
        # for destination in possible_destinations:
        #     previous = self.node.node_id
        #     if network_topology[self.node.node_id][destination] == np.inf:  # for non-neighbour nodes, set previous to empty string ""
        #         previous = ""
        #     # save information in shortest_path dictionary
        #     shortest_paths[destination] = (
        #         network_topology[self.node.node_id][destination], next(unique_identifier),
        #         {"id": destination, "previous": previous})

        # ----------------------

        # ------ DIJKSTRA ------
        # ------- set up -------

        #  initialize priority queue and shortes paths dictionary of node, where the result will be stored
        priority_queue = queue.PriorityQueue()  # priority queue where unexplored nodes will be stored. lower cost -> higher priority
        priority_queue.put((0.0, next(unique_identifier), {"id": self.node.node_id, "previous": self.node.node_id}))
        for node_id in network_topology.index:
            if node_id != self.node.node_id:
                shortest_paths[node_id] = (np.inf, None)
                # priority_queue.put((np.inf, next(unique_identifier), {'id': node_id, 'previous': None}))
        # fill priority queue, ties will be resolved thanks to the unique_identifier
        # for key in shortest_paths:
        #     priority_queue.put(shortest_paths[key])
        visited = set()  # set of visited nodes (contains ids)
        # visited.add(
        #     self.node.node_id)  # add "A" to visited nodes because we already inserted neighbours information in shortest_path dictionary (i.e. it is like we already explored it)

        # ----- algorithm -----

        # current_node = priority_queue.get()  # remove A from priority queue
        while not priority_queue.empty():
            # print(shortest_paths)
            current_node = priority_queue.get()  # take highest priority node (lowest cost)
            for neighbour in get_neighbours(
                    current_node[2]['id'],
                    network_topology):  # for each possible neighbour (i.e. indexes of the network topology)
                # print(f"Visiting neighbour {neighbour} of node {current_node[2]['id'] }")
                if not visited.__contains__(
                        neighbour):  # if the neighbour node (neighbour) has not been visited yet
                    distance_current_to_neighbour = network_topology[current_node[2]['id']][
                        neighbour]  # save distance from current node to the neighbour node
                    # print(f"Distance from {current_node[2]['id']} to {neighbour}: {distance_current_to_neighbour}")
                    distance_start_to_current = shortest_paths[current_node[2]['id']][
                        0]  # save value of distance from start to current node
                    priority_queue.put((distance_start_to_current, next(unique_identifier), {"id": neighbour,
                                                                                             "previous":
                                                                                                 current_node[2][
                                                                                                     "id"]}))  # insert neighbour with cost from start node in priority queue
                    # print(f"Distance from A to {current_node[2]['id']}: {distance_start_to_current}")
                    if (distance_start_to_current + distance_current_to_neighbour) < shortest_paths[neighbour][
                        0]:  # if distance to current + distance from current to neighbour is lower than the previously stored distance from start to neighbour, replace value
                        # replacing distance cost to neighbour node (neighbour) with the sum of going to current node + current to neighbour
                        shortest_paths[neighbour] = (
                            distance_start_to_current + distance_current_to_neighbour,  # distance
                            current_node[2]['id'])
                        #     (
                        # distance_start_to_current + distance_current_to_neighbour,  # distance
                        # self.node.shortest_paths[neighbour][1],  # keep the same unique_identifier
                        # {"id": neighbour,
                        #  "previous": current_node[2]['id']})  # update the previous node with the current node

            visited.add(current_node[2]['id'])  # add current node to visited

        # ----- end of algorithm ------

        self.node.shortest_paths = shortest_paths  # save dictionary into node attribute
        self.node.print_shortest_paths()

    def pause(self):
        self.paused = True

    def wake_up(self):
        self.paused = False


class Sender(threading.Thread):
    def __init__(self, node):
        super().__init__()
        self.node = node
        self.paused = False

    def run(self):
        print(f"{self.node.node_id} sender started")
        while not self.paused:
            try:
                while 1:
                    to_send = self.node.network_topology.to_json()
                    time.sleep(5)
                    for destination_port in list(self.node.neighbours_ports.values()):
                        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                            # print(f"Port to send: {port_to_send}")
                            # print(f"{self.node.node_id} wants to send: {self.node.network_topology}")
                            s.connect((HOST, int(destination_port)))
                            s.sendall(bytes(to_send, encoding="utf-8"))
                            s.close()
            except Exception as e:
                print(f"Error: {e}")
                print(f"Sender {self.node.node_id}: Can't connect to the Socket port: {destination_port}")
                pass

    def pause(self):
        self.paused = True

    def wake_up(self):
        self.paused = False


class Listener(threading.Thread):
    def __init__(self, node):
        super().__init__()
        self.node = node
        self.paused = False

    def run(self):
        print(f"{self.node.node_id} listener started")
        while 1:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:  # create a new socket
                    s.bind((HOST, int(self.node.port_no)))  # connect to node port
                    while 1:
                        s.listen()  # listen for now messages
                        client, address = s.accept()  # accept connection request
                        received = client.recv(4096)  # get data from client
                        if not received:  # check data not empty
                            print("didn't get data")
                            client.close()
                            pass
                        update = pd.read_json(received.decode("utf-8"))
                        client.close()  # close the client connection
                        # print(f"{self.node.node_id} received: {update}")
                        self.node.update_network_topology(update)
                        print(f"{self.node.node_id} network topology now: {self.node.network_topology}")
            except Exception as e:
                print(f"Error: {e}")
                print(f"Listener {self.node.node_id}: Can't connect to the Socket")

    def pause(self):
        self.paused = True

    def wake_up(self):
        self.paused = False


class Node:
    def __init__(self, node_id, port_no, config_file):
        """
        Instantiates a new Node object
        :param node_id: id of the node in the network as a string in [A, J]
        :param port_no: port where the node will be listening for packets from neighbours
        :param config_file: txt file containing information about neighbours (id, cost, port number)
        """
        self.node_id = node_id
        self.port_no = port_no
        self.config_file = config_file
        self.neighbours_ports = dict()
        # self.network_topology = pd.DataFrame(data=np.nan, index=["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"],
        #                                     columns=["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"])
        self.network_topology = pd.DataFrame(data=[0.0], index=[self.node_id], columns=[self.node_id])
        self.shortest_paths = dict()  # will store entries in the form: (key: destination_id, value: (cost_to_dest, previous_node))

    def config(self):
        """
        Runs the configuration process where the node take the knowledge of its neighbours (id, cost, port)
        Initializes network topology DataFrame with informations about neighbours
        Initializes self.neighbours_port dictionary where neighbours port numbers are stored
        """
        self.neighbours_ports = dict()  # dictionary format: (key = neighbour_id, value = [cost_to_neighbour, Node(neighbour_id, port_no)])
        self.shortest_paths[self.node_id] = (0.0, self.node_id)  # initialize shortest path to self

        try:
            file = open(
                self.config_file, "r")
            ids = list()
            costs = list()
            for index, line in enumerate(file):
                if index:
                    info = line.replace("\n", "").strip().split(
                        " ")  # info = [neigh_id, path_cost to neigh, neigh_port_no]
                    ids.append(info[0])
                    costs.append(info[1])
                    self.neighbours_ports[info[0]] = info[2]
                    # self.network_topology[self.node_id][info[0]] = float(info[1])

            config = pd.Series(data=costs, index=ids)
            new_index = config.index.union(self.network_topology.index)
            self.network_topology = self.network_topology.reindex(new_index, fill_value=np.nan)
            self.network_topology[self.node_id] = config
            self.network_topology[self.node_id][self.node_id] = float(0)
            # update = pd.Series(data=costs, index=ids, name=self.node_id)
            # new_index = update.index.union(self.network_topology.index)
            # self.network_topology = self.network_topology.reindex(new_index, fill_value=np.nan)
            # self.network_topology.update(update)
            print(f"Network topology now: \n {self.network_topology}")
        except Exception as e:
            print(e)
            print(f"{self.node_id} Error in opening configuration file")

    def update_network_topology(self, update):
        """
        Updates node known network topology.
        The resulting network topology DataFrame will be a union of the old one and the update one (new rows and columns will be added if missing in the old),
        common values will be updated with update values
        Example (note that dash values in the result will be replaced by NaN):

            self.network_topology       |       update
                A   B   C               |       B   D   F
            A   x   x   x               |   A   y   y   y
            D   x   x   x               |   B   y   y   y
            E   x   x   x               |   E   y   y   y

                                Result
                           A   B   C   D   F
                        A  x   y   x   y   y
                        B  -   y   -   y   y
                        D  x   x   x   -   -
                        E  x   y   x   y   y


        :param update: DataFrame representing network topology sent by a neighbour
        """
        # self.network_topology = pd.concat((self.network_topology, update), axis=1)
        # updated = update.combine_first(self.network_topology).reindex(self.network_topology.index)
        # updated[self.node_id] = self.network_topology[self.node_id]
        # self.network_topology = updated
        self.network_topology = update.combine_first(self.network_topology)

    def start(self):
        listener = Listener(self)
        listener.start()
        sender = Sender(self)
        sender.start()
        path_finder = PathFinder(self)
        timer = Timer(60, path_finder.run)
        timer.start()

    def print_shortest_paths(self):
        """
        Prints assignment desired output with all shortest paths and relative cost for reaching each node in the network
        """
        print(f"I am node {self.node_id}")
        possible_destinations = self.network_topology.index
        for destination in possible_destinations:
            if destination != self.node_id:  # and self.shortest_paths[destination][0] != np.inf:  # the second condition is for coping with unreachable nodes (e.g. a node that used to exist in the network but then failed)
                print(
                    f"Least cost path from {self.node_id} to {destination}: {extract_path(self.shortest_paths, self.node_id, destination)}, link cost: {self.shortest_paths[destination][0]} ")

    def say_hello(self):
        print("Hi! I'm node: ")
        print(self.node_id)
        print("My port number is: ")
        print(self.port_no)
        print("The config file is: ")
        print(self.config_file)
        print("My neighbours are: ")
        for key in self.neighbours.keys():
            print(self.neighbours[key][1].node_id)
            print(self.neighbours[key][1].port_no)
            print(self.neighbours[key][0])
