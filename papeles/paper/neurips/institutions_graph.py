import itertools
from collections import defaultdict
import json

import community
import networkx as nx
import matplotlib.pyplot as plt

from papeles.paper.neurips import institutions


def build_institutions_graph(file_lines, metadata, inst_counter, freq=None, year=None):
    """
    Build graph using two filters:
    - Frequency that the institution has across all periods of time
    - Year of publishing
    """
    filtered_institutions = set([x[0] for x in inst_counter.items() if x[1] > freq and x[0]])
    year_keys = defaultdict(list)
    for k, d in metadata.items():
        year_keys[d.get('year')].append(k)

    graph_node_files = defaultdict(set)
    graph = nx.Graph()
    for file, lines in list(file_lines.items()):
        if year and not (file in year_keys.get(year, {})):
            continue

        file_institutions = institutions.get_file_institutions(lines, filtered_institutions)

        unique_file_institutions = list(set(file_institutions))
        if len(unique_file_institutions) > 1:
            for i, j in itertools.combinations(unique_file_institutions, 2):
                if graph.has_edge(i, j):
                    graph[i][j]['weight'] += 1
                else:
                    graph.add_edge(i, j, weight=1)
                    graph.add_edge(j, i, weight=1)
                graph_node_files[i].add(file)
                graph_node_files[j].add(file)
        if len(unique_file_institutions) == 1:
            i = unique_file_institutions[0]
            graph.add_edge(i, i, weight=1)
    return graph, graph_node_files


def graph_to_d3js(graph):
    """
    Output graph compatible with D3.js network structure
    """
    output_graph = {'nodes': [], 'links': []}
    nodes = set()
    for e in graph.edges():
        output_graph['links'].append({'source': e[0], 'target': e[1], 'value': graph[e[0]][e[1]]['weight']})
        nodes.add(e[0])
        nodes.add(e[1])
    output_graph['nodes'] = [{'id': n, 'group': 1} for n in list(nodes)]
    with open('neurips_institutions.json', 'w') as f:
        json.dump(output_graph, f)


def dump_to_d3js_heb(graph, file: str) -> None:
    """
    Given a networkx graph save it to file in hierarchical edge bundling (heb) format

    Consider target/source dependency using the degree of a node:
        - Only include in edges nodes with lower degree than source node
    """
    output = []
    for node in graph.nodes():
        edges = graph.edges(node)
        targets = []
        for edge in edges:
            for e in edge:
                if e != node:
                    if graph.degree[e] < graph.degree[node]:
                        targets.append(e)
        output.append({'name': node, 'size': len(edges), 'edges': targets})
    with open(file, 'w') as f:
        json.dump(output, f)


def plot_graph(graph):
    node_size = []
    for node, degree in graph.degree():
        if degree < 5:
            node_size.append(10)
        elif 5 <= degree < 10:
            node_size.append(40)
        else:
            node_size.append(90)

    partition = community.best_partition(graph)

    edge_colors = []
    edge_width = []
    for i, j in graph.edges():
        if graph[i][j]['weight'] < 7:
            edge_colors.append('gray')
            edge_width.append(0.1)
        elif 7 <= graph[i][j]['weight'] < 15:
            edge_colors.append('black')
            edge_width.append(1)
        elif 15 <= graph[i][j]['weight'] < 25:
            edge_colors.append('blue')
            edge_width.append(1)
        else:
            edge_colors.append('red')
            edge_width.append(6)

    plt.figure(1, figsize=(120, 120))
    nx.draw(graph,
            with_labels=True,
            node_color=list(partition.values()),  # node_color_map,
            node_size=node_size,
            font_size=8,
            edge_color=edge_colors,
            width=edge_width,
            alpha=0.8)
    plt.savefig("institutions_graph.png")
