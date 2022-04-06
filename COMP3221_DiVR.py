"""
Accepts following argument at terminal: python COMP3221_DiVR.py <Node-id> <Port-no> <Node-config-file>
@param Node-id: the ID of a node in the net topology (A, B, C, etc...).
@param Port-no: the port number of a node listening to the information update packets. Mapped([A, ..., K], [6000, ..., 6009])
@param Node-config-file: <Node-id>config.txt is the configuration file for Node with <Node-id>
"""


import sys

from classes import Node

arguments = sys.argv[1:]
node = Node(arguments[0], arguments[1], arguments[2])
node.config()
node.start()
#node.say_hi()
print(f"Do you want to change link costs for node {arguments[0]}? [Y or N]")
change_link_cost = input()
if change_link_cost == "Y":
    print("Type link cost to change in the format [TO] [NEW_COST]. (e.g. C 2.8)")
    change_request = input().strip().split(" ")  # change_request = [TO, NEW_COST]
    print(node.change_link_cost(change_request[0], change_request[1]))

