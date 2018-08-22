# -*- coding: utf-8 -*-
"""
Created on Thu Aug 16 11:08:54 2018

@author: asterioss
"""

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

    names_txt = "driver_names_1980.txt"
    embs_file = "driver_embeddings_1980.npy"

    names_txt = "constructor_year_names_1980.txt"
    embs_file = "team_year_embeddings_1980.npy"

    #names_txt = "constructor_names_1980.txt"
    #embs_file = "team_embeddings_1980.npy"

    names_txt = "gp_names_1980.txt"
    embs_file = "gp_embeddings_1980.npy"

    names_txt = "gp_names-del.txt"
    embs_file = "gp_embeddings-del.npy"

    #exclude_names = ['----', 'Piquet Jr', 'Salo', 'Vergne', 'Grassi', 'Jones',
    #                 'Glock', 'Mcnish', 'Kobayashi', 'Tuero', 'Pic',
    #                 'Tambay', 'Cecotto', 'Foitek', 'Henton', 'Zunino',
    #                 'Arnoux', 'Zanardi', 'Grouillard', 'Sullivan',
    #                 'Satoru Nakajima', 'Manfred Winkelhock', 'Guerrero',
    #                 'Adams', 'Corrado Fabi', 'Wendlinger', 'Dalmas', 'Giacomelli',
    #                 'Ratzenberger', 'Rothengatter', 'Martini', 'Tarquini',
    #                 'Jules Bianchi', 'Sala', 'Bernard', 'Merhi', 'Wurz',
    #                 'Wehrlein', 'Vandoorne', 'Larini', 'Naspetti', 'Cheever',
    #                 'Pizzonia', 'Diniz', 'Rebaque']
    #
    #highlighted_names = ['Alonso', 'Hamilton', 'Vettel', 'Senna', 'Hakkinen',
    #                 'Prost', 'Lauda', 'Michael Schumacher']

    ###Use for both Constructor and GPs
    exclude_names = ['----']
    highlighted_names = []
    #
    ##Use for constructor-year
    ###https://www.motorsport.com/f1/news/most-successful-best-f1-cars-991911/1399077/?nrt=54
    #highlighted_names = ['Mercedes 2014', 'Mercedes 2016', 'Mercedes 2015', 'Mercedes 2017',
    #             'Mclaren 1984', 'Mclaren 1988', 'Mclaren 1989',
    #             'Ferrari 2000', 'Ferrari 2001', 'Ferrari 2002', 'Ferrari 2003', 'Ferrari 2004', 'Ferrari 2007',
    #             'Red Bull 2010', 'Red Bull 2011', 'Red Bull 2012', 'Red Bull 2013',
    #             'Williams 1992', 'Williams 1992', 'Williams 1996',
    #             'Benetton 1994',  'Benetton 1995',
    #             'Renault 2005', 'Renault 2006',
    #             'Brawn 2009']
    #
    #exclude_names = [i for i in random.sample(names, 430) if i not in highlighted_names and
    #                 i not in ['Alfa 1980', 'Benetton 1992', 'Ligier 1981', 'Bar 2004',
    #                   'Mercedes 2018', 'Williams 1995', 'Mclaren 2017',
    #                   'Jordan 2004', 'Minardi 2004', 'Caterham 2014',
    #                   'Lotus Racing 2010', 'Virgin 2010', 'Virgin 2011',
    #                   'Hrt 2011', 'Minardi 2001', 'Forti 1995', 'Mclaren 2014',
    #                   'Mclaren 2015', 'Mclaren 2016', 'Mclaren 2018',
    #                   'Mclaren 2005', 'Williams 1986', 'Mclaren 1998', 'Williams 1987',
    #                    'Ferrari 2006', 'Mclaren 1991', 'Williams 1997', 'Mclaren 2007',
    #                    'Mclaren 2012', 'Ferrari 2008', 'Williams 1991', 'Mclaren 1999',
    #                    'Mclaren 2000', 'Mclaren 1985', 'Ferrari 1990', 'Mclaren 1990',
    #                    'Ferrari 1998', 'Mclaren 2008', 'Ferrari 1999', 'Red Bull 2009',
    #                    'Mclaren 2011']]

    names = plot_stuff(names_txt, embs_file, exclude_names, highlighted_names)