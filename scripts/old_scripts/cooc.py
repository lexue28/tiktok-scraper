import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
from collections import defaultdict, Counter

folder = "hashtags"
all_documents = []
for filename in os.listdir(folder):
    with open(os.path.join(folder, filename), "r", encoding="utf-8") as f:
        for line in f:
            words = [w.strip() for w in line.strip().split() if w.strip()]
            if words:
                all_documents.append(words)


from collections import Counter

banned_words = ["videoia", "fyp", "foryoupage", "foryou", "video", "tiktok", "viral", "trending", "funnyvideos", "fy", "trend", "pov", "fypシ", "tik_tok", "edit", "italia", "funny"]
def is_banned(word):
    return word in banned_words or "viral" in word

print("HEY", is_banned("virale"))

all_words = [w for doc in all_documents for w in doc if not is_banned(w)]
word_counts = Counter(all_words)
top_100_words = set([w for w, _ in word_counts.most_common(100)])

# Step 2: Filter all_documents to keep only top 100 words
filtered_documents = []
for doc in all_documents:
    filtered_doc = [w for w in doc if w in top_100_words]
    if len(filtered_doc) > 1:  # keep only if at least two words left
        filtered_documents.append(filtered_doc)


# Flatten for unique vocab using filtered docs only
vocab = set(w for doc in filtered_documents for w in doc)
unique_words = list(vocab)

# Build co-occurrence counts (window=2 within filtered docs only)
window_size = 2
co_occurrences = defaultdict(Counter)
for doc in filtered_documents:
    for i, word in enumerate(doc):
        for j in range(max(0, i-window_size), min(len(doc), i+window_size+1)):
            if i != j:
                co_occurrences[word][doc[j]] += 1

# Build co-occurrence matrix
co_matrix = np.zeros((len(unique_words), len(unique_words)), dtype=int)
word_index = {word: idx for idx, word in enumerate(unique_words)}
for word, neighbors in co_occurrences.items():
    for neighbor, count in neighbors.items():
        co_matrix[word_index[word]][word_index[neighbor]] = count

co_matrix_df = pd.DataFrame(co_matrix, index=unique_words, columns=unique_words)
print(co_matrix_df)

G = nx.from_pandas_adjacency(co_matrix_df)
G.remove_edges_from(nx.selfloop_edges(G))
edges = G.edges(data=True)

csv_path = os.path.join("gephi", "cooccurrence_network_filter100.csv")
nx.write_edgelist(G, csv_path, delimiter=',', data=['weight'])
print(f"Edge list exported to {csv_path}")

# if len(edges) > 0:
#     edge_widths = [5 * attr['weight']/max(co_matrix_df.max()) for _,_,attr in edges]
# else:
#     edge_widths = []

# min_weight = 5
# filtered_edges = [(u, v, d) for u, v, d in G.edges(data=True) if d['weight'] >= min_weight]

# # Build a new filtered graph
# G_filtered = nx.Graph()
# G_filtered.add_edges_from(filtered_edges)

# # --- If you want, also remove isolated nodes (no edges) ---
# isolated = list(nx.isolates(G_filtered))
# G_filtered.remove_nodes_from(isolated)


# # --- Plot filtered network ---


# plt.figure(figsize=(14, 14))
# if len(G_filtered.nodes) == 0:
#     print("No nodes with edge weight >= 5")
# else:
#     pos = nx.spring_layout(G_filtered, seed=42, k=0.8)
#     edge_weights = [d['weight'] for (_, _, d) in G_filtered.edges(data=True)]
#     nx.draw(
#         G_filtered, pos,
#         with_labels=True,
#         node_color="skyblue",
#         edge_color="gray",
#         width=[w/10 for w in edge_weights],
#         font_size=10,
#         node_size=700
#     )
#     plt.title("Filtered Word Co-occurrence Network (weight >= 5)")
#     plt.tight_layout()
#     plt.show()

# G = nx.from_pandas_adjacency(co_matrix_df)
# G.remove_edges_from(nx.selfloop_edges(G))
# edges = G.edges(data=True)
# if len(edges) > 0:
#     edge_widths = [5 * attr['weight']/max(co_matrix_df.max()) for _,_,attr in edges]
# else:
#     edge_widths = []

# plt.figure(figsize=(8,8))
# pos = nx.spring_layout(G, seed=42)
# nx.draw(G, pos, with_labels=True, node_color="skyblue", edge_color="gray", width=edge_widths, font_size=12)
# plt.title("Word Co-occurrence Network")
# plt.tight_layout()
# plt.show()
