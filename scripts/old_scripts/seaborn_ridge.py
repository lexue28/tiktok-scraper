import os
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

def bar():
    sns.set_theme(style="white", rc={"axes.facecolor": (0, 0, 0, 0)})

    days = ["thur", "fri", "sat", "sun"]
    summary_rows = []

    for day in days:
        print("day", day)
        folder_path = f"classify/{day}"
        if not os.path.exists(folder_path):
            continue

        adult_path = None
        child_path = None

        for file in os.listdir(folder_path):
            if file.endswith(".csv") and "classified_results" in file:
                if "_a" in file:
                    adult_path = os.path.join(folder_path, file)
                elif "_c" in file:
                    child_path = os.path.join(folder_path, file)

        def count_harm(path):
            if path and os.path.exists(path):
                df = pd.read_csv(path)
                df.columns = df.columns.str.strip().str.lower()
                total = len(df)
                harmful = (df["harmful"] == "harmful").sum() if "harmful" in df.columns else 0
                return harmful, total
            return 0, 0

        adult_harmful, adult_total = count_harm(adult_path)
        child_harmful, child_total = count_harm(child_path)

        # Avoid division by zero
        prop_adult = adult_harmful / adult_total if adult_total > 0 else 0
        prop_child = child_harmful / child_total if child_total > 0 else 0
        avg_prop = (prop_adult + prop_child) / 2

        summary_rows.append({
            "day": day,
            "prop_adult": prop_adult,
            "prop_child": prop_child,
            "avg_prop": avg_prop
        })
    summary_df = pd.DataFrame(summary_rows)

    plt.figure(figsize=(8, 4))
    sns.barplot(data=summary_df, x="day", y="avg_prop", palette="rocket")
    plt.ylabel("Proportion of Harmful Descriptions")
    plt.xlabel("Day")
    plt.title("Proportion of Harmful Descriptions per Day")
    plt.ylim(0, summary_df["avg_prop"].max() * 1.2)
    plt.tight_layout()
    plt.savefig("classify/prop_barplot_day.png", dpi=200)

bar()

    # ridge_df = pd.DataFrame(summary_rows)
    # ridge_df["day"] = pd.Categorical(ridge_df["day"], categories=days, ordered=True)
    # pal = sns.cubehelix_palette(len(days), rot=-.25, light=.7)

    # g = sns.FacetGrid(ridge_df, row="day", hue="day", aspect=15, height=0.5, palette=pal)

    # g.map(sns.kdeplot, "harmful_noisy",
    #       bw_adjust=0.3, clip=[-0.5, 1.5],
    #       fill=True, alpha=1, linewidth=1.5)

    # g.map(sns.kdeplot, "harmful_noisy", clip=[-0.5, 1.5], color="w", lw=2, bw_adjust=0.3)
    # g.refline(y=0, linewidth=2, linestyle="-", color=None, clip_on=False)

    # def label(x, color, label):
    #     ax = plt.gca()
    #     ax.text(0, .2, label.upper(), fontweight="bold", color=color,
    #             ha="left", va="center", transform=ax.transAxes)

    # g.map(label, "harmful_noisy")

    # g.figure.subplots_adjust(hspace=-0.25)
    # g.set_titles("")
    # g.set(yticks=[], ylabel="")
    # g.despine(bottom=True, left=True)

    # plt.savefig("classify/ridgeplot_harmful_per_day.png", dpi=200, bbox_inches="tight")

def ridge():
    sns.set_theme(style="white", rc={"axes.facecolor": (0, 0, 0, 0)})

    days = ["thur", "fri", "sat", "sun"]
    data_rows = []

    for day in days:
        print("day", day)
        folder_path = f"classify/{day}"
        if not os.path.exists(folder_path):
            continue

        adult_path = None
        child_path = None

        for file in os.listdir(folder_path):
            if file.endswith(".csv") and "classified_results" in file:
                if "_a" in file:
                    adult_path = os.path.join(folder_path, file)
                elif "_c" in file:
                    child_path = os.path.join(folder_path, file)

        def get_harm_values(path):
            if path and os.path.exists(path):
                df = pd.read_csv(path)
                df.columns = df.columns.str.strip().str.lower()
                if "harmful" in df.columns:
                    return (df["harmful"] == "harmful").astype(int).tolist()
            return []

        adult_values = get_harm_values(adult_path)
        child_values = get_harm_values(child_path)
        
        all_values = adult_values + child_values
        
        for value in all_values:
            data_rows.append({
                "day": day,
                "harmful": value
            })

    df = pd.DataFrame(data_rows)

    df["day"] = pd.Categorical(df["day"], categories=days, ordered=True)

    pal = sns.cubehelix_palette(len(days), rot=-.25, light=.7)
    g = sns.FacetGrid(df, row="day", hue="day", aspect=15, height=.5, palette=pal)

    g.map(sns.kdeplot, "harmful",
        bw_adjust=.5, clip_on=False,
        fill=True, alpha=1, linewidth=1.5)
    g.map(sns.kdeplot, "harmful", clip_on=False, color="w", lw=2, bw_adjust=.5)

    g.refline(y=0, linewidth=2, linestyle="-", color=None, clip_on=False)

    def label(x, color, label):
        ax = plt.gca()
        ax.text(0, .2, label.upper(), fontweight="bold", color=color,
                ha="left", va="center", transform=ax.transAxes)

    g.map(sns.kdeplot, "harmful",
        bw_adjust=0.1,  
        cut=0,         
        clip_on=False,
        fill=True, alpha=1, linewidth=1.5)

    g.set(xlim=(0, 1)) 
    g.figure.subplots_adjust(hspace=-.25)

    g.set_titles("")
    g.set(yticks=[], ylabel="")
    g.despine(bottom=True, left=True)

    g.set(xlim=(-0.5, 1.5))

    ridge_out = "classify/ridgeplot_harmful_per_day.png"
    plt.savefig(ridge_out, dpi=200, bbox_inches="tight")

# ridge()