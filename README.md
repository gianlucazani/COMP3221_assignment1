# COMP3221 Assignment 1: Routing Algorithm
<img src="https://user-images.githubusercontent.com/82953736/160225605-6e980123-5cf8-48a5-a349-cb65692286d2.png" width="50%">
The assignment topic is the realization of a routing algorithm, running in a simulated local network composed by 10 nodes and at least 15 connections linking them with random cost. The network topology I used for running simulations is in the image above. <br>

## Environment and dependencies

This program runs on:

```
python 3.9.7
```
Packages needed for running:
```
pandas 1.4.1
numpy 1.22
```

## Usage

### Starting a node
As stated in the assignment sheet, the program starts by running the following shell command:
```
python COMP3221_DiVR.py <Node-id> <Port-no> <Node-config-file>
```
For simulation _n_ nodes network it is necessary to run the command on _n_ differnet instances at the same time, changing parameters each time for each node. <br>
A node can be started at everytime and the network will recompute the shortest paths taking care of the new comer. If a node is not started, the nodes which have that node as unique neighbour will not be reached by other nodes (e.g. if node _J_ in the network above is not started, node _I_ will not be reached by anyone.
### Change link cost
Once a node is started, after a brief presentation of the node, the following message will be prompted at terminal:
```
Do you want to change link costs for node <Node-id>? [Y or N]
```
If ```Y``` is typed and then ```enter``` is pressed, a new message will be prompted:
```
Type link cost to change in the format [TO] [NEW_COST]. (e.g. C 2.8)
```
By typing the link to change the cost at and in the specified format, the topology will be modified (but the config file will remain the same).<br>

It is important to remember that:
<ul><li>Even if the first of the two messages is prompted at the start of the program and never again, you will still be able to change link cost by tiping ```Y``` during execution, since the program will keep listening for input during its entire execution time (then the second message will be prompted).</li><li> <b> The link cost must be changed on both sides in order to be effective</b> (e.g. if we want to change link cost from G to D, we need to say to G that we want to change link cost with D and to D that we want to change the link cost with G). </li>
Note that 
