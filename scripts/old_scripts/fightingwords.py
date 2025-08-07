import os
import string
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer as CV
import seaborn as sns

# Exclude punctuation and banned words
exclude = set(string.punctuation)
banned_words = [
    "videoia", "fyp", "foryoupage", "foryou", "video", "tiktok", "viral", "trending",
    "funnyvideos", "fy", "trend", "pov", "fypシ", "tik_tok", "edit", "italia", "funny", "foru"
]

def basic_sanitize(in_string):
    '''Returns a very roughly sanitized version of the input string.'''
    in_string = ''.join([ch for ch in in_string if ch not in exclude])
    in_string = in_string.lower()
    in_string = ' '.join(in_string.split())
    return in_string

def read_hashtags(folder):
    hashtags = []
    for file in os.listdir(folder):
        if file.endswith(".txt"):
            with open(os.path.join(folder, file), encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        hashtags.extend(line.split())
    return hashtags

def bayes_compare_language(l1, l2, ngram=1, prior=.01, cv=None):
    '''
    Compares word distributions between two sets of text (l1 and l2).
    Returns list of (term, z-score) tuples.
    '''
    if cv is None and type(prior) is not float:
        print("If using a non-uniform prior:")
        print("Please also pass a count vectorizer with the vocabulary parameter set.")
        quit()
    l1 = [basic_sanitize(l) for l in l1 if l not in banned_words]
    l2 = [basic_sanitize(l) for l in l2 if l not in banned_words]
    if cv is None:
        cv = CV(decode_error='ignore', min_df=10, max_df=.5, ngram_range=(1, ngram),
                binary=False, max_features=15000)
    counts_mat = cv.fit_transform(l1 + l2).toarray()
    vocab_size = len(cv.vocabulary_)
    if type(prior) is float:
        priors = np.array([prior for _ in range(vocab_size)])
    else:
        priors = prior
    z_scores = np.empty(priors.shape[0])
    count_matrix = np.empty([2, vocab_size], dtype=np.float32)
    count_matrix[0, :] = np.sum(counts_mat[:len(l1), :], axis=0)
    count_matrix[1, :] = np.sum(counts_mat[len(l1):, :], axis=0)
    a0 = np.sum(priors)
    n1 = 1. * np.sum(count_matrix[0, :])
    n2 = 1. * np.sum(count_matrix[1, :])
    for i in range(vocab_size):
        term1 = np.log((count_matrix[0, i] + priors[i]) / (n1 + a0 - count_matrix[0, i] - priors[i]))
        term2 = np.log((count_matrix[1, i] + priors[i]) / (n2 + a0 - count_matrix[1, i] - priors[i]))
        delta = term1 - term2
        var = 1. / (count_matrix[0, i] + priors[i]) + 1. / (count_matrix[1, i] + priors[i])
        z_scores[i] = delta / np.sqrt(var)
    index_to_term = {v: k for k, v in cv.vocabulary_.items()}
    sorted_indices = np.argsort(z_scores)
    return [(index_to_term[i], z_scores[i]) for i in sorted_indices]

# === Load and filter data ===
adults_hashtags = read_hashtags("hashtags/adults")
children_hashtags = read_hashtags("hashtags/children")

# === Run analysis ===
results = bayes_compare_language(adults_hashtags, children_hashtags, ngram=1, prior=0.01)

# === Save to CSV ===
# output_path = os.path.join("hashtags", "fightingwords.csv")
df = pd.DataFrame(results, columns=["Term", "ZScore"])
# df.to_csv(output_path, index=False)
# print(f"Saved fighting words to {output_path}")

def plot(df):
    plt.figure(figsize=(10, 6))
    
    # Create horizontal bar plot
    bar_plot = sns.barplot(y='Term', x='ZScore', data=df, palette="vlag", orient='h')
    
    # Annotate each bar
    for p in bar_plot.patches:
        bar_plot.annotate(format(p.get_width(), '.1f'), 
                          (p.get_x() + p.get_width(), p.get_y() + p.get_height() / 2),
                          ha='left', va='center', 
                          xytext=(5, 0), 
                          textcoords='offset points')
        
        # Color bars
        if p.get_width() < 0:
            p.set_color('red')
        else:
            p.set_color('green')

    plt.title('Fighting Words Z-Scores')
    plt.xlabel('Z-Score')
    plt.ylabel('Term')
    
    # Save plot
    output_path = os.path.join("hashtags", "fightingwordstop.png")
    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"Saved bar plot to {output_path}")

top_pos = df.nlargest(10, "ZScore")
top_neg = df.nsmallest(10, "ZScore")
df_trimmed = pd.concat([top_neg, top_pos])
plot(df_trimmed)