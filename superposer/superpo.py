import networkx as nx
import pickle
import os
import matplotlib.pyplot as plt

def load_graph(file_path):
    """Charge un graphe depuis un fichier pickle."""
    with open(file_path, 'rb') as f:
        G = pickle.load(f)
    return G

def filter_graph_by_context(initial_graph, contextual_graphs, target_node="FAM111B"):
    """Supprime les chemins à partir du nœud cible si ses voisins ne sont pas dans les graphes contextuels."""
    nodes_to_remove = set()

    # Construire un ensemble de tous les nœuds présents dans les graphes contextuels
    context_nodes = set()
    for G in contextual_graphs:
        context_nodes.update(G.nodes())

    # Vérifier les voisins du nœud cible
    if target_node in initial_graph:
        neighbors = set(initial_graph.neighbors(target_node))
        for neighbor in neighbors:
            if neighbor not in context_nodes:
                nodes_to_remove.add(neighbor)
                paths = list(nx.all_simple_paths(initial_graph, source=target_node, target=neighbor))
                for path in paths:
                    nodes_to_remove.update(path)

    # Supprimer les nœuds marqués
    filtered_graph = initial_graph.copy()
    filtered_graph.remove_nodes_from(nodes_to_remove)

    return filtered_graph

def highlight_paths(initial_graph, contextual_graphs, target_node="FAM111B"):
    """Identifie et surligne les chemins conservés dans le graphe initial."""
    highlighted_graph = initial_graph.copy()
    conserved_edges = set()

    # Rechercher les chemins conservés dans les graphes contextuels
    for G in contextual_graphs:
        if target_node in G:
            for neighbor in initial_graph.neighbors(target_node):
                if neighbor in G:
                    path = nx.shortest_path(G, source=target_node, target=neighbor)
                    if nx.is_simple_path(initial_graph, path):
                        edges = [(path[i], path[i+1]) for i in range(len(path)-1)]
                        conserved_edges.update(edges)
                        nx.set_edge_attributes(highlighted_graph, {edge: {'color': 'red'} for edge in edges})

    return highlighted_graph, conserved_edges

def find_common_nodes(initial_graph, contextual_graphs):
    """Trouve les nœuds du graphe initial qui sont présents dans au moins un des graphes contextuels."""
    common_nodes = set()
    for G in contextual_graphs:
        common_nodes.update(set(initial_graph.nodes()).intersection(G.nodes()))
    return common_nodes

def extract_red_nodes_graph_with_highlights(G, common_nodes, conserved_edges=None):
    """Extrait un sous-graphe contenant uniquement les nœuds rouges et leurs connexions, en conservant les highlights."""
    red_nodes = {node for node in G.nodes() if node in common_nodes}
    subgraph = G.subgraph(red_nodes).copy()

    # Conserver les arêtes surlignées en rouge, sinon les arêtes normales
    edge_colors = {}
    for edge in subgraph.edges():
        if conserved_edges and edge in conserved_edges:
            edge_colors[edge] = 'red'
        else:
            edge_colors[edge] = 'black'
    nx.set_edge_attributes(subgraph, edge_colors, 'color')

    return subgraph

def draw_graph_with_highlights(G, common_nodes, target_node="FAM111B", conserved_edges=None):
    """Visualise le graphe avec les chemins surlignés et les nœuds en commun, centré sur la cible."""
    plt.figure(figsize=(15, 10))  # Taille de la figure ajustée pour être plus large

    # Ajuster la disposition des nœuds pour éviter la superposition des arêtes
    pos = nx.spring_layout(G, k=0.5, center=nx.spring_layout(G)[target_node], seed=42, iterations=200, scale=2)
    edges = G.edges(data=True)

    # Surligner les arêtes
    edge_colors = [attr['color'] if 'color' in attr else 'black' for _, _, attr in edges]

    # Surligner les nœuds en commun
    node_colors = ['red' if node in common_nodes else 'skyblue' for node in G.nodes()]

    # Dessiner le graphe avec les arêtes et les nœuds surlignés
    nx.draw(G, pos, with_labels=True, edge_color=edge_colors, node_color=node_colors, node_size=500, font_size=10, font_color='black')
    plt.show()

    # Afficher le graphe réduit
    if conserved_edges:
        reduced_graph = G.edge_subgraph(conserved_edges).copy()
        plt.figure(figsize=(15, 10))  # Taille de la figure ajustée pour être plus large
        reduced_pos = nx.spring_layout(reduced_graph, k=0.5, center=nx.spring_layout(G)[target_node], seed=42, iterations=200, scale=2)

        # Surligner les nœuds en commun dans le graphe réduit
        reduced_node_colors = ['red' if node in common_nodes else 'skyblue' for node in reduced_graph.nodes()]

        # Dessiner le graphe réduit
        nx.draw(reduced_graph, reduced_pos, with_labels=True, edge_color='red', node_color=reduced_node_colors, node_size=500, font_size=10, font_color='black')
        plt.show()

def draw_red_nodes_graph_with_highlights(G, target_node="FAM111B"):
    """Visualise le sous-graphe des nœuds rouges avec les chemins surlignés conservés."""
    plt.figure(figsize=(15, 10))  # Taille de la figure ajustée pour être plus large

    # Ajuster la disposition des nœuds pour éviter la superposition des arêtes
    pos = nx.spring_layout(G, k=0.5, center=nx.spring_layout(G)[target_node], seed=42, iterations=200, scale=2)
    edges = G.edges(data=True)

    # Surligner les arêtes
    edge_colors = [attr['color'] if 'color' in attr else 'black' for _, _, attr in edges]

    # Dessiner le graphe avec les arêtes et les nœuds surlignés
    nx.draw(G, pos, with_labels=True, edge_color=edge_colors, node_color='red', node_size=500, font_size=18, font_color='black')
    plt.show()

def save_nodes_to_txt(graph, file_path):
    """Sauvegarde les nœuds du graphe réduit dans un fichier texte."""
    with open(file_path, 'w') as f:
        for node in graph.nodes():
            f.write(f"{node}\n")

import os

# Fonction pour rechercher les fichiers avec une extension spécifique dans un dossier
def find_files_with_extension(directory, extension):
    """
    Parcourt récursivement le répertoire et récupère les chemins relatifs des fichiers ayant l'extension spécifiée.

    :param directory: Chemin du répertoire à parcourir
    :param extension: Extension de fichier à rechercher (par ex: '.pkl')
    :return: Liste des chemins relatifs des fichiers correspondant
    """
    files_with_extension = []

    # Parcourir tous les fichiers et sous-répertoires
    for root, dirs, files in os.walk(directory):
        for file in files:
            # Vérifier si l'extension correspond
            if file.endswith(extension):
                # Obtenir le chemin relatif
                relative_path = os.path.relpath(os.path.join(root, file), directory)
                files_with_extension.append(relative_path)

    return files_with_extension


# Fonction principale 'superpo' avec intégration de la recherche des sous-graphes
def superpo(initial_graph, search_path, target_node):
    # Charger le graphe initial
    initial = load_graph(initial_graph)

    # Rechercher les graphes contextuels dans le dossier donné
    contextual_graphs = []
    contextual_graphs_dir = search_path  # Dossier renseigné par l'utilisateur

    # Trouver les fichiers .pkl dans le répertoire
    graph_files = find_files_with_extension(contextual_graphs_dir, '.pkl')

    # Charger les graphes contextuels (en évitant le graphe initial)
    for file_name in graph_files:
        graph_path = os.path.join(contextual_graphs_dir, file_name)

        # Vérifier que le fichier n'est pas le même que le graphe initial
        if graph_path != initial_graph:
            contextual_graphs.append(load_graph(graph_path))
            print(contextual_graphs[0])
        else:
            print(f"Le fichier {graph_path} est le graphe initial et ne sera pas traité comme un sous-graphe.")

    # Filtrer les nœuds du graphe initial en fonction des graphes contextuels, en se concentrant sur "FAM111B"
    filtered_graph = filter_graph_by_context(initial_graph, contextual_graphs, target_node)

    # Identifier et surligner les chemins conservés
    highlighted_graph, conserved_edges = highlight_paths(filtered_graph, contextual_graphs, target_node)

    # Trouver les nœuds en commun entre le graphe initial et les graphes contextuels
    common_nodes = find_common_nodes(filtered_graph, contextual_graphs)

    # Visualiser le graphe complet avec surlignage
    draw_graph_with_highlights(highlighted_graph, common_nodes, target_node, conserved_edges=conserved_edges)

    # Extraire et dessiner le sous-graphe des nœuds rouges en gardant les highlights
    red_nodes_graph = extract_red_nodes_graph_with_highlights(highlighted_graph, common_nodes, conserved_edges)
    draw_red_nodes_graph_with_highlights(red_nodes_graph, target_node)

    # Sauvegarder les nœuds du réseau réduit dans un fichier texte
    save_nodes_to_txt(red_nodes_graph, "reduced_graph_nodes.txt")
