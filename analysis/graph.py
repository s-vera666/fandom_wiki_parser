import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

entities = pd.read_csv("../fandom_wiki_parser/data/processed/entities.csv")
doc_entities = pd.read_csv("../fandom_wiki_parser/data/processed/doc_entities.csv")

# Приведение типов
entities['entity_id'] = entities['entity_id'].astype(int)
doc_entities['entity_id'] = doc_entities['entity_id'].astype(int)

# Фильтрация только персонажей
if 'PERSON' in entities['type'].values:
    entities = entities[entities['type'] == 'PERSON']

# Сопоставление id персонажа с его именем для подписей на графе
id_to_name = {}
for i in range(len(entities)):
    entity_id = int(entities.loc[i, 'entity_id'])
    name = entities.loc[i, 'entity_name']
    id_to_name[entity_id] = name

# Совместные упоминания
co_occurrence = {}

for doc_id in doc_entities['doc_id'].unique():
    ids_in_doc = set(doc_entities[doc_entities['doc_id'] == doc_id]['entity_id'])
    if len(ids_in_doc) < 2:
        continue
    ids_list = list(ids_in_doc)
    for i in range(len(ids_list)):
        for j in range(i + 1, len(ids_list)):
            a, b = ids_list[i], ids_list[j]
            if a > b:
                a, b = b, a
            pair = (a, b)
            if pair in co_occurrence:
                co_occurrence[pair] += 1
            else:
                co_occurrence[pair] = 1

# Построение графа (вес ребра >= 5)
G = nx.Graph()
for pid in id_to_name.keys():
    G.add_node(int(pid))

for (a, b), w in co_occurrence.items():
    if w >= 5:
        G.add_edge(int(a), int(b), weight=w)

# Фильтрация вершин со степенью >= 5
degree = dict(G.degree())
high_degree_nodes = [int(node) for node, deg in degree.items() if deg >= 5]
G = G.subgraph(high_degree_nodes)

print(f"После фильтрации: вершин = {G.number_of_nodes()}, рёбер = {G.number_of_edges()}")

if G.number_of_nodes() == 0:
    print("Нет вершин со степенью >= 5")
    exit()

degree_filtered = dict(G.degree())

# Визуализация
plt.figure(figsize=(32, 10))
pos = nx.spring_layout(G, seed=42, k=3.0, iterations=50, scale=2)

# Размер узлов
node_sizes = [degree_filtered[node] * 50 for node in G.nodes()]

# Рисовка узлов
nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color='lightpink', edgecolors='palevioletred', linewidths=1.5)

weights = [G[u][v]['weight'] for u, v in G.edges()]

# Рёбра
nx.draw_networkx_edges(G, pos, width=[w * 0.5 for w in weights], alpha=0.4, edge_color='gray')


# Подписи для графа
labels = {}
for node in G.nodes():
    node_int = int(node)
    if node_int in id_to_name:
        name = id_to_name[node_int]
    else:
        name = f"Unknown({node_int})"
    labels[node] = f"{name}\n({degree_filtered[node]})"

nx.draw_networkx_labels(G, pos, labels=labels, font_size=6, font_weight='bold', font_color='black')

plt.title("Граф совместных упоминаний (степень ≥ 5, вес ребра ≥ 5)", fontsize=15)
plt.axis('off')
plt.tight_layout()
plt.savefig("../fandom_wiki_parser/data/results/graph.png", dpi=200) # добавляем в папку data для просмотра результата

plt.savefig("../fandom_wiki_parser/docs/figures/graph.png", dpi=200) # добавляем в папку docs/figures для отчета

plt.show()

print("Граф сохранён в 'graph.png'")

