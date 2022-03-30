import queue
import threading
import socket
import time
import numpy as np
import pandas as pd
from itertools import count
from lib import extract_path, get_neighbours, received_new_information, remove_failed

HOST = "127.0.0.1"
# Global variable for letting listener thread know that the first 60 seconds elapsed
# and so from now on the routing algorithm will be started each updated packet received
# while the first time the routing algorithm is started is when 60 seconds elapse since node is started
ELAPSED_60_SECONDS = False


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
        global ELAPSED_60_SECONDS
        ELAPSED_60_SECONDS = True
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
        network_topology.replace(np.nan, np.inf)
        network_topology = remove_failed(network_topology)
        # We want to compute shortest paths only from alive nodes and to alive nodes
        all_nodes = list(
            network_topology.index.values)  # list of all nodes built from neighbour information of alive nodes (we cannot assume that all of them are reachable)
        nodes_alive = list(network_topology)  # list of actually alive nodes that
        nodes_to_work_with = list(set(all_nodes) - set(nodes_alive))
        network_topology.drop(labels=nodes_to_work_with,
                              inplace=True)  # remove lines corresponding to neighbours of alive nodes that are not alive themselves
        unique_identifier = count()  # resolves ties when sorting dictionaries in priority queue
        shortest_paths = dict()  # shortest_paths dictionary which will be store the result for shortest paths (same format as node.shortest_paths)
        shortest_paths[self.node.node_id] = (
            0.0, self.node.node_id)  # initialize shortest path with current node information
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
                            round(cost_start_to_current + cost_current_to_neighbour, 2),  # distance
                            current_node[2]['id'])

            visited.add(current_node[2]['id'])  # add current node to visited

        # ----- end of algorithm ------

        # save and print computed shortest paths only if it is different from the previous stored
        if self.node.shortest_paths != shortest_paths:
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
        connected_for_first_time = dict()  # ( key = port_number, value = (neighbour_id, boolean))
        alive = dict()

        for key in self.node.neighbours_ports.keys():
            port = self.node.neighbours_ports[key]
            connected_for_first_time[port] = [key, False]
            alive[port] = [key, False]
        while not self.paused:  # try to send data until the thread is not stopped, if not stopped it will pass through exceptions without stopping
            try:
                while 1:
                    time.sleep(10)
                    to_send = self.node.network_topology.to_json()  # converts network_topology DataFrame to json
                    # print(f"{self.node.node_id} wants to send: \n {self.node.network_topology}")
                    for destination_port in list(self.node.neighbours_ports.values()):  # send data to all neighbours

                        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                            # print(f"Port to send: {port_to_send}")

                            try:
                                s.connect((HOST, int(destination_port)))
                                s.sendall(bytes(to_send, encoding="utf-8"))
                                s.close()
                                connected_for_first_time[destination_port][1] = True
                                alive[destination_port][1] = True
                                # print(connected_for_first_time)
                                # print(alive)
                            except Exception as e:
                                if connected_for_first_time[destination_port][1] and alive[destination_port][1]:  # if i managed to connect to the node in the past but now I cannot, it means it is broken
                                    print(f"Node {connected_for_first_time[destination_port][0]} failed")
                                    alive[destination_port][1] = False
                                    self.node.neighbour_failed(connected_for_first_time[destination_port][
                                                                   0])  # node will update its network topology
                                    continue
                                else:
                                    continue
            except Exception as e:
                continue
                # print(f"Sender {self.node.node_id} error when communicating with port {destination_port}: {e}")

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
                        different_shape, link_cost_changed = received_new_information(self.node.network_topology, update)
                        if different_shape or link_cost_changed:
                            # print(f"{self.node.node_id} received: \n {update}")
                            self.node.update_network_topology(
                                update)  # will update only if the update packet brings new information
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

        Attributes:
            neighbours_ports (dictionary): Stores neighbours port number in format (key = neighbour id, value = port number)
            shortest_paths (dictionary): Stores shortest paths for each node in the network in format (key = destination, value = (path cost, previous node))
            network_topology (pandas.DataFrame): Stores network topology known by the node, the columns correspond to 'from' nodes and rows are 'to' nodes
            network_topology_history (list): list of DataFrames (network_topologies). Stores the various versions of the network_topology without repetition.
                                            This helps for not overwriting the current network topology with a version already stored in the past.
                                            It is particularly helpful when a link cost changes, the node stores the new value but the network_topology
                                            gets overwritten by other neighbours with older information before the new cost has the chance to get propagated.
            sender (Thread): Thread which manages the sending of packets
            listener (Thread): Listens for new update packets
            path_finder (Thread): runs Dijkstra's algorithm
            timer (Thread): runs path_finder after 60 seconds since start
        """

        # ATTRIBUTES
        self.node_id = node_id
        self.port_no = port_no
        self.config_file = config_file
        self.neighbours_ports = dict()
        self.shortest_paths = dict()
        self.network_topology = pd.DataFrame(data=[0.0], index=[self.node_id], columns=[self.node_id])
        self.network_topology_history = list()
        self.network_topology_history.append(self.network_topology)

        # Threads
        self.sender = Sender(self)
        self.listener = Listener(self)
        self.path_finder = PathFinder(self)
        self.timer = Timer(60, self.path_finder.run)

    def config(self):
        """
        Runs the configuration process where the node take the knowledge of its neighbours (id, cost, port)
        Initializes network topology DataFrame with information about neighbours
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
                    costs.append(float(info[1]))
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
        Updates node known network topology:
            - The resulting network topology DataFrame will be a union of the old one and the update one (new rows and columns will be added if missing in the old),
                common values will be updated with update values.
            - Doesn't let other nodes update self column.
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

        Before updating the network topology checks if the new package actually brings new information or not and if the package has been seen before
        by the node (avoiding cases where newer information get replace by older ones)

        :param update: DataFrame representing network topology sent by a neighbour
        """
        different_shape, link_cost_changed = received_new_information(self.network_topology, update)
        if (different_shape or link_cost_changed) and not self.seen_before(update):
            self.network_topology_history.append(update)
            do_not_update = dict()
            for key in self.neighbours_ports:
                do_not_update[key] = self.network_topology[self.node_id][key]
            update.replace(np.nan, -1, inplace=True)
            self.network_topology = update.combine_first(self.network_topology)
            update.replace(-1, np.nan, inplace=True)
            self.network_topology.replace(-1, np.nan, inplace=True)
            for key in do_not_update:
                to_replace = self.network_topology[self.node_id][key]
                if to_replace == to_replace:  # i.e. to_replace is not NaN
                    self.network_topology[self.node_id][key] = do_not_update[key]
            self.network_topology_history.append(self.network_topology)
            if link_cost_changed and ELAPSED_60_SECONDS:
                self.path_finder.run()
                return
            if ELAPSED_60_SECONDS:
                self.path_finder.run()
                return

    def seen_before(self, update):
        """
        This method check whether the current update combined with current network topology has been seen before or not
        This method is for managing cases where a node gets updates with link cost changes and then gets overwritten by others with old information
        so that it cannot spread the right information (with link cost changes) to others because it gets immediately overwritten
        :param update: new packet arrived from neighbours
        :returns True if the packet has been seen before by the node, False otherwise
        """
        for nt in self.network_topology_history:
            different_shape, link_cost_changed = received_new_information(nt, update)
            if not different_shape and not link_cost_changed:
                # print("------ SEEN BEFORE -------")
                return True
        # print("------ NOT SEEN BEFORE -------")
        return False

    def print_shortest_paths(self):
        """
        Prints assignment desired output with all shortest paths and cost for reaching each node in the network
        """
        print(f"I am node {self.node_id}")
        for destination in self.shortest_paths.keys():  # print only for nodes for which the shortest path has been found (i.e. reachable nodes)
            if destination != self.node_id:  # and self.shortest_paths[destination][0] != np.inf:  # the second condition is for coping with unreachable nodes (e.g. a node that used to exist in the network but then failed)
                print(
                    f"Least cost path from {self.node_id} to {destination}: {extract_path(self.shortest_paths, self.node_id, destination)}, link cost: {self.shortest_paths[destination][0]} ")

    def neighbour_failed(self, neighbour_id):
        self.network_topology_history.append(self.network_topology)
        self.network_topology[
            neighbour_id] = np.nan  # replaces all values in the column of neighbour_id with NaN values (states that a node is not alive anymore)
        for col in self.network_topology:
            self.network_topology[col][
                neighbour_id] = np.nan  # replaces all values in the column of neighbour_id with NaN values (states that the node is not reachable anymore)
        print(f"topology after failure {self.network_topology}")
        self.network_topology_history.append(self.network_topology)
        if ELAPSED_60_SECONDS:
            self.path_finder.run()

    def start(self):
        """
        Turns on the node starting threads
        """
        # self.failure_detector.start()
        self.sender.start()
        self.listener.start()
        self.timer.start()

    def change_link_cost(self, _to, cost):
        try:
            if not list(self.neighbours_ports.keys()).__contains__(_to):
                return f"{_to} node is not a neighbour of mine ({self.node_id})"
            if not float(cost) > 0:
                return f"{cost} not valid, please insert a valid cost (> 0)"

            self.network_topology.at[_to, self.node_id] = float(cost)
            print(f"New network topology: {self.network_topology}")
            return "Link cost changed, you will notice the update in few seconds"
        except Exception as e:
            return "Wrong input format"

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
