import os
import string
import numpy as np
import pandas as pd
import shifterator as sh
from collections import defaultdict

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
    fq= defaultdict(int)
    for w in hashtags:
        fq[w] += 1                  
    return fq

def shift(l1, l2):
    '''
    Compares word distributions between two sets of text (l1 and l2).
    Returns list of (term, z-score) tuples.
    '''
    l1 = {k: v for k, v in l1.items() if k not in banned_words}
    l2 = {k: v for k, v in l2.items() if k not in banned_words}
    proportion_shift = sh.ProportionShift(type2freq_1=l1,
                                      type2freq_2=l2)
    proportion_shift.get_shift_graph(system_names = ['Adults', 'Children'],
                                 title='Proportion Shift of Hashtags')
    return proportion_shift

# === Load and filter data ===
adults_hashtags = read_hashtags("hashtags/adults")
children_hashtags = read_hashtags("hashtags/children")

# === Run analysis ===
results = shift(adults_hashtags, children_hashtags)

output_path = os.path.join("hashtags", "shifterator.csv")
df = pd.DataFrame(results, columns=["Term", "ZScore"])
df.to_csv(output_path, index=False)
print(f"Saved fighting words to {output_path}")
