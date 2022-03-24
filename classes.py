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

    def run(self):
        """
        This thread runs the Dijkstra's shortest path finding algorithm
        """
        # ------- SET UP -------

        network_topology = self.node.network_topology.copy()  # save node network topology as a copy so that the original can be modified while the algorithm is running
        network_topology.fillna(np.inf, inplace=True)  # replace NaN values with +inf
        unique_identifier = count()  # resolves ties when sorting dictionaries in priority queue
        shortest_paths = self.node.shortest_paths  # save node shortest_paths dictionary as a copy so that the original can be modified while the algorithm is running

        # ----------------------

        # ------ DIJKSTRA ------
        # ------- set up -------

        #  initialize priority queue and shortest paths dictionary of node, where the result will be stored
        priority_queue = queue.PriorityQueue()  # priority queue where unexplored nodes will be stored. lower cost -> higher priority
        priority_queue.put((0.0, next(unique_identifier), {"id": self.node.node_id, "previous": self.node.node_id}))
        for node_id in network_topology.index:
            if node_id != self.node.node_id:
                shortest_paths[node_id] = (np.inf, None)

        visited = set()  # set of visited nodes (contains ids)

        # ----- algorithm -----

        while not priority_queue.empty():
            current_node = priority_queue.get()  # take highest priority node (lowest cost) and start visiting it
            for neighbour in get_neighbours(
                    current_node[2]['id'],
                    network_topology):  # for each current_node neighbour
                if not visited.__contains__(
                        neighbour):  # if the neighbour node (neighbour) has not been visited yet
                    cost_start_to_current = shortest_paths[current_node[2]['id']][
                        0]  # save distance from start node to current_node
                    cost_current_to_neighbour = network_topology[current_node[2]['id']][
                        neighbour]  # save distance from current_node to the neighbour of current_node
                    priority_queue.put((cost_start_to_current, next(unique_identifier), {"id": neighbour,
                                                                                         "previous":
                                                                                             current_node[2][
                                                                                                 "id"]}))  # insert neighbour with cost from start node in priority queue

                    # if the distance to reach the neighbour of the current visited node from the current visited node +
                    # the distance for reaching the current visited node from the start node is
                    # less than the stored distance for reaching the neighbor node from the start node
                    # then save the sum of the two previous mentioned distances as new distance from start to neighbour
                    # and save the current node as previous node in the path for reaching the neighbour from the start
                    if (cost_start_to_current + cost_current_to_neighbour) < shortest_paths[neighbour][0]:
                        shortest_paths[neighbour] = (
                            cost_start_to_current + cost_current_to_neighbour,  # distance
                            current_node[2]['id'])

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
        while not self.paused:  # try to send data until the thread is not stopped, if not stopped it will pass through exceptions without stopping
            try:
                while 1:
                    to_send = self.node.network_topology.to_json()  # converts network_topology DataFrame to json
                    time.sleep(5)
                    for destination_port in list(self.node.neighbours_ports.values()):  # send data to all neighbours
                        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                            # print(f"Port to send: {port_to_send}")
                            # print(f"{self.node.node_id} wants to send: {self.node.network_topology}")
                            s.connect((HOST, int(destination_port)))
                            s.sendall(bytes(to_send, encoding="utf-8"))
                            s.close()
            except Exception as e:
                print(f"Sender {self.node.node_id} error when communincating with port {destination_port}: {e}")

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
                        update = pd.read_json(
                            received.decode("utf-8"))  # update packet is a DataFrame and gets converted here from json
                        client.close()  # close the client connection
                        # print(f"{self.node.node_id} received: {update}")
                        self.node.update_network_topology(
                            update)  # update node network topology with the new update packet
                        print(f"{self.node.node_id} network topology now: {self.node.network_topology}")
            except Exception as e:
                print(f"Listener {self.node.node_id} Error: {e}")

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
        self.shortest_paths = dict()  # will store entries in the form: (key: destination_id, value: (cost_to_dest, previous_node))
        self.network_topology = pd.DataFrame(data=[0.0], index=[self.node_id], columns=[self.node_id])

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
                if index:  # skips first line and reads while new lines are present
                    info = line.replace("\n", "").strip().split(
                        " ")  # info = [neigh_id, path_cost to neigh, neigh_port_no]
                    ids.append(info[0])
                    costs.append(info[1])
                    self.neighbours_ports[info[0]] = info[2]

            neighbours_series = pd.Series(data=costs, index=ids)
            new_index = neighbours_series.index.union(self.network_topology.index)
            self.network_topology = self.network_topology.reindex(new_index, fill_value=np.nan)
            self.network_topology[self.node_id] = neighbours_series
            self.network_topology[self.node_id][self.node_id] = float(0)
            print(f"My starting network topology: \n {self.network_topology}")
        except Exception as e:
            print(f"{self.node_id} error in configuration: {e}")

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
        self.network_topology = update.combine_first(self.network_topology)

    def start(self):
        """
        Turns on the node and starts threads for sending, listening, computing shortest path and setting timer before routing algorithm is started for first time
        """
        listener = Listener(self)
        listener.start()
        sender = Sender(self)
        sender.start()
        path_finder = PathFinder(self)
        timer = Timer(60, path_finder.run)  # set timer after which the path finding algorithm will be run
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

    def say_hi(self):
        """
        Utility method for printing information about node
        """
        print("Hi! I'm node: ")
        print(self.node_id)
        print("My port number is: ")
        print(self.port_no)
        print("The config file is: ")
        print(self.config_file)
        print("My neighbours ports:")
        print(self.neighbours_ports)
        print("My network topology is: ")
        print(self.network_topology)
