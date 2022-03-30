# COMP3221 Assignment 1: Routing Algorithm
<p align="center"><img src="https://user-images.githubusercontent.com/82953736/160226426-b151f6fb-5453-4c03-9069-5729491ad6dd.png" width="50%"></p>
The assignment topic is the realization of a routing algorithm, running in a simulated local network composed by 10 nodes and at least 15 connections linking them with random cost. The network topology I used for running simulations is in the image above and the routing algorithm I used is the Dijkstra's shortest path algorithm <br>

## Information
The following section will guide you thorugh the simulation of the network, by eplaining how to see results of the requirements and by stating some disclaimer for having a sure correct behaviour. 
Before diving into further informationm, here's a brief review of the implemented features:
<ul>
  <li>
    Each node has no information about the network but its neighbour information.
  </li>
  <li>
    The program runs in a loop forever (until it gets shutted down)
  </li>
  <li>
    Each node prints at terminal shortest paths to reach each node after 60 seconds.
  </li>
  <li>
    Each node can join the network at any moment and the network will converge again.
  </li>
  <li>
    Link costs can be changed at any moment during execution and the network will converge automatically.
  </li>
  <li>
    Changes made after the first 60 second will trigger the path finder thread which will find (eventual) new shortest paths for reaching nodes
  </li>
  <li>
    When a node fails (works only if performed after first 60 seconds) the network will automatically detect the failure and will act for convergence.
  </li>
</ul>

As last information, in the submitted .zip file you will find a ``` correct_paths.txt ``` file where all correct paths for each node are stored. The paths have been generated with the ``` networkx ``` python package by running the Dijkstra's algorithm and I used it for checking correct results.

## Environment and Dependencies

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
### Reminders for correct execution
During simulations I noticed that the system is most likely to behave correctly if we perform actions keeping in mind that:
<ul>
  <li>
    Any change that will modify the network topology (i.e. node joins later, link cost change) made <b>before</b> the first 60 seconds, has to be made with a decent time margin before the timeout (at least 2 sending periods before). Failures are not well detected during the first 60 seconds.
  </li>
  <li> 
    Any change that will modify the network topology (i.e. node joins later, link cost change, failures) made <b>after</b> the first 60 seconds, has to be made only when all the nodes have printed the shortest paths. In this case it would be better as well to wait at least one sending period before performing changes.
  </li>
  <li> 
    Any change that will modify the network topology (i.e. node joins later, link cost change, failures) made <b>after</b> a shortest paths output, has to be made after each nodes has printed again the result of shortest paths (i.e. after each node has reacted to changes).
  </li>
  <li> 
    Once a the Dijkstra's algorithm is triggered for any of the possible reasons, each node might have a slightly different time of computation and it might print the output few seconds late compared with others. Make sure that each node has printed the output before performing the above actions.
  </li>
  <li> 
    For how the newtwork is implemented, it will not react to changes that are reversions to previous configurartions seen within the same simulation (e.g. change a link cost from x to y and that bring it back to x, make a node fail and then make it alive again). This is a consequence of how I impemented the network: each node will store an history of all the versions he as seen of the network, and once a previous-seen configuration is received it gets ignored by the node. Unfortunately I figured this out too late during the project realisation and it hasn't been possible for me to start everything again for correcting this. If I had more time I would have provided each update packet with a timestamp and I would have given the highest priority to newer packets, and not just to the ones the node has never seen before.
  </li>
  </li> I left some debug print messages commented in the code. In case you wish to see some useful information printed at terinal, you can uncomment lines: ---------- . The information include: see which packet a node is sending, which packed a node receives and if it has seen the same packet before, see when a node detects a neighbour failure.
</ul>

### Requirements

#### Starting a node
As stated in the assignment sheet, the program starts by running the following shell command:
```
python COMP3221_DiVR.py <Node-id> <Port-no> <Node-config-file>
```
For simulation _n_ nodes network it is necessary to run the command on _n_ differnet instances at the same time, changing parameters each time for each node. <br>
A node can be started at everytime and the network will recompute the shortest paths taking care of the new comer. If a node is not started, the nodes which have that node as unique neighbour will not be reached by other nodes (e.g. if node _J_ in the network above is not started, node _I_(i) will not be reached by anyone).
#### Change link cost
Before explaining how the link cost can be performed, a disclaimer has to be made: once the link cost from a node X to a node Y is changed, reverting the operation will not be effective on the network (unless the network is restarted). 
##### Method 1
Once a node is started, after a brief presentation of the node, the following message will be prompted at terminal:
```
Do you want to change link costs for node <Node-id>? [Y or N]
```
If ``` Y ``` is typed and then ```enter``` is pressed, a new message will be prompted:
```
Type link cost to change in the format [TO] [NEW_COST]. (e.g. C 2.8)
```
By typing the link to change the cost at and in the specified format, the topology will be modified (but the config file will remain the same).<br>

It is important to remember that:
<ul>
  <li>
    Even if the first of the two messages is prompted at the start of the program and never again, you will still be able to change link cost by typing   Y during execution, since the program will keep listening for input during its entire execution time (then the second message will be prompted).    </li>
  <li> 
    <b> The link cost must be changed on both sides in order to be effective</b> (e.g. if we want to change link cost from G to D, we need to say to G that we want to change link cost with D and to D that we want to change the link cost with G).
  </li>
</ul>

##### Method 2
The link cost between two nodes can be changed also by modifying the `config.txt` file. Remeber that only when the file is modified before a node joins the network this kind of change will be effective (and not if you turn off a node, modify the file, and then turn on the node again).

#### Node failure
Node failure can be performed by simply shutting down the process at terminal, hence using the system keybinding for doing that ( ``` ctrl + C ``` on Windows and Mac systems). If no link cost change was performed on this node, the shut down command will need to be pressed twice (one will be interpretated as input from the link cost change prompt), otherwise only once.

Node failures are detected by neighbours: when a node is unable to send packets to neighbours that have been alive in the past (this information is maintained by each node) it marks them as failed and communicate that to other nodes in the network. 

Remember that node failures are not well correctly detected if the occure before the first 60 seconds.

## Examples

### Link cost change

#### Example 1 - After 60 seconds elapsed

Node F output before link cost changes:

```
I am node F
Least cost path from F to A: FCA, link cost: 3.6 
Least cost path from F to B: FDGB, link cost: 5.5 
Least cost path from F to C: FC, link cost: 1.6 
Least cost path from F to D: FD, link cost: 1.5 
Least cost path from F to E: FDGE, link cost: 5.2 
Least cost path from F to G: FDG, link cost: 3.2 
Least cost path from F to H: FH, link cost: 1.7 
Least cost path from F to I: FHJI, link cost: 5.3 
Least cost path from F to J: FHJ, link cost: 2.9
```

Node F output after cost E to G changed to 50.0:

```
I am node F
Least cost path from F to A: FCA, link cost: 3.6 
Least cost path from F to B: FDGB, link cost: 5.5 
Least cost path from F to C: FC, link cost: 1.6 
Least cost path from F to D: FD, link cost: 1.5 
Least cost path from F to E: FDGBE, link cost: 7.5 
Least cost path from F to G: FDG, link cost: 3.2 
Least cost path from F to H: FH, link cost: 1.7 
Least cost path from F to I: FHJI, link cost: 5.3 
Least cost path from F to J: FHJ, link cost: 2.9 
```

You can see that the shortest path for reaching E is changed and the more convinient now is FDGBE instead of FDGE.

#### Example 2 - Before 60 second elapsed

Here's what node F outputs for the first time after 60 second elapse. During those 60 seocnds link cost from H to J changed to 30.0:
```
I am node F
Least cost path from F to A: FCA, link cost: 3.6 
Least cost path from F to B: FDGB, link cost: 5.5 
Least cost path from F to C: FC, link cost: 1.6 
Least cost path from F to D: FD, link cost: 1.5 
Least cost path from F to E: FDGE, link cost: 5.2 
Least cost path from F to G: FDG, link cost: 3.2 
Least cost path from F to H: FH, link cost: 1.7 
Least cost path from F to I: FDGJI, link cost: 7.5 
Least cost path from F to J: FDGJ, link cost: 5.1
```

You can see that the path F -> H is not convinient anymore, for example going to J now costs less if we go for FDGJI.

### Node failure

#### Example 1 - Single failure

In this example we make node J fail and we will see how A output changes in response to the failure. Here is what A outputs before node J fails:

```
I am node A
Least cost path from A to B: AB, link cost: 2.0 
Least cost path from A to C: AC, link cost: 2.0 
Least cost path from A to D: ACD, link cost: 3.6 
Least cost path from A to E: ABE, link cost: 4.0 
Least cost path from A to F: ACF, link cost: 3.6 
Least cost path from A to G: ABG, link cost: 4.3 
Least cost path from A to H: ACH, link cost: 5.0 
Least cost path from A to I: ABGJI, link cost: 8.6 
Least cost path from A to J: ABGJ, link cost: 6.2 
```

And this is what A outputs once node J failed. As you can see both node I and node J are not reachable anymore (J is I's only neighbour):

```
I am node A
Least cost path from A to B: AB, link cost: 2.0 
Least cost path from A to C: AC, link cost: 2.0 
Least cost path from A to D: ACD, link cost: 3.6 
Least cost path from A to E: ABE, link cost: 4.0 
Least cost path from A to F: ACF, link cost: 3.6 
Least cost path from A to G: ABG, link cost: 4.3 
Least cost path from A to H: ACH, link cost: 5.0 
```

#### Example 2 - Multiple failures

By going on from Example 1 above, we can make other nodes fail after J. We will keep node A's output monitored and we'll see hopw the node responds to these failures. 

Node H fails:

```
I am node A
Least cost path from A to B: AB, link cost: 2.0 
Least cost path from A to C: AC, link cost: 2.0 
Least cost path from A to D: ACD, link cost: 3.6 
Least cost path from A to E: ABE, link cost: 4.0 
Least cost path from A to F: ACF, link cost: 3.6 
Least cost path from A to G: ABG, link cost: 4.3 
```

Then node B fails (node that paths to G and E change):

```
Least cost path from A to C: AC, link cost: 2.0 
Least cost path from A to D: ACD, link cost: 3.6 
Least cost path from A to E: ACDGE, link cost: 7.3 
Least cost path from A to F: ACF, link cost: 3.6 
Least cost path from A to G: ACDG, link cost: 5.3 
```

And finally we can make G fails, so that E becomes unreachable event if it is still alive (like node I):

```
I am node A
Least cost path from A to C: AC, link cost: 2.0 
Least cost path from A to D: ACD, link cost: 3.6 
```

