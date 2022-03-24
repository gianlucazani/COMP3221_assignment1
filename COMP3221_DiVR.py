"""
Accepts following argument at terminal: python COMP3221_DiVR.py <Node-id> <Port-no> <Node-config-file>
@param Node-id: the ID of a node in the net topology (A, B, C, etc...).
@param Port-no: the port number of a node listening to the information update packets. Mapped([A, ..., K], [6000, ..., 6009])
@param Node-config-file: <Node-id>config.txt is the configuration file for Node with <Node-id>

Config file example (Fconfig.txt):

4               -> Number of neighbours of node F
A 2.3 6000      -> (neighbour id, distance from F (float), neighbour listening port)
C 3.2 6002
E 2.8 6004
K 5.4 6009

Other information:
    - the link costs will be consistent in both directions, i.e., if the cost from F to A is similar to the cost from A to F.
    - Node F must not have global knowledge

Questions:
1) Is said that links must be generated randomly, but actually links depend on how you create the config.txt file. So?
2) Do we have to actually implement a routing algorithm or we can use the networkx?
3) How can we provide an interface for link cost change/failure if the program is running?
4) Does each node know the number of nodes in the network?

"""


import sys

from classes import Node

arguments = sys.argv[1:]
node = Node(arguments[0], arguments[1], arguments[2])
node.config()
node.start()
#node.say_hello()
