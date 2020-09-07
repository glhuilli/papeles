import itertools
import json
from collections import defaultdict
from typing import Any, Dict, List, Optional, Set

import community
import matplotlib.pyplot as plt
import networkx as nx

from papeles.paper.neurips import institutions


def build_institutions_graph(file_lines,
                             metadata,
                             inst_counter,
                             freq: int = None,
                             year: str = None,
                             keys_filter: Optional[Set[str]] = None,
                             directed: bool = False):
    """
    Build graph using two filters:
    - Frequency that the institution has across all periods of time
    - Year of publishing
    """
    keys_filter = keys_filter or set()
    filtered_institutions = {x[0] for x in inst_counter.items() if x[1] > freq and x[0]}
    year_keys: Dict[str, List[str]] = defaultdict(list)
    for k, d in metadata.items():
        year_keys[d.get('year')].append(k)

    graph_node_files: Dict[str, Set[str]] = defaultdict(set)
    if directed:
        graph = nx.DiGraph()
    else:
        graph = nx.Graph()
    for file, lines in list(file_lines.items()):
        if year and file not in year_keys.get(year, {}):
            continue
        if keys_filter:
            if file not in keys_filter:
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


def graph_to_d3js(graph, file: str) -> None:
    """
    Output graph compatible with D3.js network structure
    """
    output_graph: Dict[str, Any] = {'nodes': [], 'links': []}
    nodes = set()
    for e in graph.edges():
        output_graph['links'].append({
            'source': e[0],
            'target': e[1],
            'value': graph[e[0]][e[1]]['weight']
        })
        nodes.add(e[0])
        nodes.add(e[1])
    output_graph['nodes'] = [{'id': n, 'group': 1} for n in list(nodes)]
    with open(file, 'w') as f:
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
                    if graph.degree[e] <= graph.degree[node]:
                        targets.append(e)
                    else:
                        targets.append(node)
                else:
                    targets.append(node)
        if len(targets):
            output.append({'name': node, 'size': len(edges), 'edges': targets})
    with open(file, 'w') as f:
        json.dump(output, f)


def plot_graph(graph, file: str) -> None:
    node_size = []
    for _, degree in graph.degree():
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
    nx.draw(
        graph,
        with_labels=True,
        node_color=list(partition.values()),  # node_color_map,
        node_size=node_size,
        font_size=8,
        edge_color=edge_colors,
        width=edge_width,
        alpha=0.8)
    plt.savefig(file)


def dump_to_treemap_d3js(graph, file: str, cluster_threshold: int = 3) -> None:
    """
    Dumps into an output json file all clusters and the information for each institution about their
    centrality scores.

    Given that it's an undirected graph, the centrality scores included are:
         - hub
         - authorities
         - betweenness
         - closeness centrality
         - katz centrality
         - eigen centrality
    """
    partition = community.best_partition(graph)
    institution_clusters: Dict[str, List[str]] = defaultdict(list)
    for k, p in partition.items():
        institution_clusters[p].append(k)
    eigen_centrality = nx.eigenvector_centrality(graph)
    katz_centrality = nx.katz_centrality_numpy(graph)
    closeness_centrality = nx.closeness_centrality(graph)
    betweenness_centrality = nx.betweenness_centrality(graph)
    hubs, authorities = nx.hits(graph)

    output: Dict[str, Any] = {'name': 'institutions', 'children': []}
    for k, v in institution_clusters.items():
        if len(v) > cluster_threshold:
            name_k = f'cluster_{k}'
            cluster_childrens: Dict[str, Any] = {'name': name_k, 'children': []}
            for institution in v:
                degree = graph.degree[institution]
                institution_data = {
                    'name': institution,
                    'hub': hubs[institution],
                    'authorities': authorities[institution],
                    'betweenness': betweenness_centrality[institution],
                    'closeness': closeness_centrality[institution],
                    'katz': katz_centrality[institution],
                    'eigen': eigen_centrality[institution],
                    'size': degree
                }
                cluster_childrens['children'].append(institution_data)
            output['children'].append(cluster_childrens)

    with open(file, 'w') as f:
        json.dump(output, f)
