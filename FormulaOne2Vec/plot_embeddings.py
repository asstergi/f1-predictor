# -*- coding: utf-8 -*-
from matplotlib import pyplot
import umap
from adjustText import adjust_text
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def plot_embeddings(names, embeddings, n_neighbors=10, min_dist=0.5, metric='euclidean',
                    random_state=1, adjust_labels=False, d_names=None, highlighted_names=None):

    model = umap.UMAP(n_neighbors=min(len(names)-1, n_neighbors), min_dist=min_dist, metric=metric)
    vectors = model.fit_transform(embeddings)
    x, y = vectors[:, 0], vectors[:, 1]

    if d_names:
        s = pd.DataFrame([x, y, names]).T
        s.columns=['x','y','names']
        s = s[s.names.isin(d_names)]
        s = s.sort_values('x')
        x = s['x'].tolist()
        y = s['y'].tolist()
        names = s['names'].tolist()

    plt.figure(figsize=(20, 15))
    scatter = plt.scatter(x, y)
    annotations = []
    for x_i, y_i, n_i in zip(x,y, names):
        if highlighted_names and n_i in highlighted_names:
            annotations.append(plt.text(x_i,y_i, n_i, color='red'))
        elif 'Verstappen' in n_i:
            annotations.append(plt.text(x_i,y_i, n_i, color='green'))
        elif 'Rosberg' in n_i:
            annotations.append(plt.text(x_i,y_i, n_i, color='blue'))

        elif 'Mf1' in n_i or 'Spyker' in n_i:
            annotations.append(plt.text(x_i,y_i, n_i, color='green'))

        elif 'Mclaren' in n_i and any([i in n_i for i in ['2015', '2016', '2017', '2018']]):
            annotations.append(plt.text(x_i,y_i, n_i, color='orange'))
        else:
            annotations.append(plt.text(x_i,y_i, n_i))

    adjust_text(annotations, x=x, y=y)

    pyplot.show()

    return x, y


def plot_stuff(names_txt, embs_file, exclude_names, highlighted_names):

    with open(names_txt, "r") as file:
        names = eval(file.readline())

    embeddings = np.load(embs_file)
    d_names = [i for i in names if i not in exclude_names]

    x, y = plot_embeddings(names, embeddings, n_neighbors=10, min_dist=0.6,
                    metric='euclidean', random_state=1, adjust_labels=True,
                    d_names=d_names, highlighted_names=highlighted_names)

    return names

if __name__ == '__main__':

    names_txt = "drivers_names.txt"
    embs_file = "drivers_embeddings.npy"

    # List of names you want to exclude from plotting
    exclude_names = ['----', 'Grassi', 'Jones']
    # List of names you want to highlight with red color on the plot
    highlighted_names = ['Alonso', 'Hamilton', 'Vettel']

    names = plot_stuff(names_txt, embs_file, exclude_names, highlighted_names)
