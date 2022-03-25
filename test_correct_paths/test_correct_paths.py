import networkx as nx

G = nx.Graph()

G.add_edge("A", "B", weight=2.0)
G.add_edge("A", "C", weight=2.0)
G.add_edge("B", "E", weight=2.0)
G.add_edge("B", "G", weight=2.3)
G.add_edge("C", "D", weight=1.6)
G.add_edge("C", "F", weight=1.6)
G.add_edge("C", "H", weight=3.0)
G.add_edge("D", "F", weight=1.5)
G.add_edge("D", "G", weight=1.7)
G.add_edge("E", "G", weight=2.0)
G.add_edge("F", "H", weight=1.7)
G.add_edge("G", "H", weight=1.5)
G.add_edge("G", "J", weight=1.9)
G.add_edge("H", "J", weight=1.2)
G.add_edge("I", "J", weight=2.4)

shortest_paths = nx.shortest_path(G)
output = ""

for start in shortest_paths.keys():
    output += f"I am node {start} \n"
    for destination in shortest_paths[start].keys():
        if start != destination:
            output += f"Shortest path from {start} to {destination} is: {shortest_paths[start][destination]}, cost: {round(nx.shortest_path_length(G, start, destination, weight='weight'), 1)} \n"

    output += "\n\n"

with open('output.txt', 'w') as f:
    f.write(output)


