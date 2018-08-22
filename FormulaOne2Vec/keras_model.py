# -*- coding: utf-8 -*-

import pandas as pd
import itertools
import numpy as np
import operator

from sklearn.preprocessing import MinMaxScaler

from keras.layers import (Input, Dense, Embedding, concatenate,
                          Flatten, Subtract)
from keras.layers.core import Dropout
from keras.models import Model
from keras import regularizers
from keras.callbacks import EarlyStopping
from keras.layers.normalization import BatchNormalization
from keras.preprocessing.text import Tokenizer
from keras.optimizers import SGD

def transform_pairwise_all(X, y):
    X_new = []
    y_new = []
    comp_lst = []
    races = []
    y = np.asarray(y)
    if y.ndim == 1:
        y = np.c_[y, np.ones(y.shape[0])]
    comb = itertools.combinations(range(X.shape[0]), 2)

    for k, (i, j) in enumerate(comb):
        if y[i, 1] != y[j, 1]:
            # skip if same target or different group
            continue
        X_new.append(list((X.iloc[i] - X.iloc[j]).values))
        y_new.append(-np.sign(y[i, 0] - y[j, 0]))
        comp_lst.append((y[i, 2], y[j, 2], y[i, 3], y[j, 3], y[i, 5], y[j, 5], y[i, 4], y[i, 1]))
        races.append(y[i, 1])

        X_new.append(list((X.iloc[j] - X.iloc[i]).values))
        y_new.append(-np.sign(y[j, 0] - y[i, 0]))
        comp_lst.append((y[j, 2], y[i, 2], y[j, 3], y[i, 3], y[j, 5], y[i, 5], y[j, 4], y[j, 1]))
        races.append(y[j, 1])

    return np.asarray(X_new), np.asarray(y_new).ravel(), comp_lst, races

if __name__ == '__main__':

    ####################################
    ########## Data reading ############
    ####################################
    print ("Reading data...")
    df = pd.read_csv('data_sample.csv')

    ####################################
    ###### Data tranformations #########
    ####################################
    print ("Transforming data...")
    unique_races = df.race.unique()
    df['gp'] = df['race'].apply(lambda x: x.split('_')[0])

    df_d = df.iloc[np.random.permutation(len(df))]

    y = df_d[['result', 'race', 'driver', 'constructor', 'gp', 'constructor_year']]
    df_d = df_d.drop(['previous_race', 'result', 'race', 'driver', 'constructor', 'gp', 'constructor_year'], axis=1)
    X_trans, y_trans, comp_lst, races = transform_pairwise_all(df_d, y)
    y_trans[y_trans==-1] = 0
    print ("Data has been transformed...")

    comp_lst_df = pd.DataFrame(comp_lst, columns = ['driver_1', 'driver_2', 'team_1', 'team_2', 'team_year_1', 'team_year_2', 'gp', 'race'])

    # Separate categorical data from the rest of the dataset
    driver_1 = np.array(comp_lst_df['driver_1'])
    driver_2 = np.array(comp_lst_df['driver_2'])

    team_1 = np.array(comp_lst_df['team_1'])
    team_2 = np.array(comp_lst_df['team_2'])

    team_year_1 = np.array(comp_lst_df['team_year_1'])
    team_year_2 = np.array(comp_lst_df['team_year_2'])

    gp = np.array(comp_lst_df['gp'])
    gp = np.array([i.replace(' ', '_') for i in gp])

    # Scale numeric input
    mm = MinMaxScaler((-1,1))
    X_train = mm.fit_transform(X_trans)
    y_train = y_trans.copy()

    ###########################################
    ####  Tokenize the categorical inputs #####
    ###########################################
    print ("Tokenizing data...")

    driver_tokenizer = Tokenizer(filters='!"#$%&()*+,-/:;<=>?@[\]^`{|}~ ')
    driver_tokenizer.fit_on_texts(driver_1)
    driver_1_encoded = driver_tokenizer.texts_to_sequences(driver_1)
    driver_2_encoded = driver_tokenizer.texts_to_sequences(driver_2)
    driver_1_encoded= np.array(driver_1_encoded)
    driver_2_encoded= np.array(driver_2_encoded)
    driver_vocab_size = len(driver_tokenizer.word_index) + 1
    print('Driver vocabulary Size: %d' % driver_vocab_size)


    constructor_tokenizer = Tokenizer(filters='!"#$%&()*+,-/:;<=>?@[\]^`{|}~ ')
    constructor_tokenizer.fit_on_texts(team_1)
    constructor_1_encoded = constructor_tokenizer.texts_to_sequences(team_1)
    constructor_2_encoded = constructor_tokenizer.texts_to_sequences(team_2)
    constructor_1_encoded= np.array(constructor_1_encoded)
    constructor_2_encoded= np.array(constructor_2_encoded)
    constructor_vocab_size = len(constructor_tokenizer.word_index) + 1
    print('Constructor vocabulary Size: %d' % constructor_vocab_size)

    constructor_year_tokenizer = Tokenizer(filters='!"#$%&()*+,-/:;<=>?@[\]^`{|}~ ')
    constructor_year_tokenizer.fit_on_texts(team_year_1)
    constructor_year_1_encoded = constructor_year_tokenizer.texts_to_sequences(team_year_1)
    constructor_year_2_encoded = constructor_year_tokenizer.texts_to_sequences(team_year_2)
    constructor_year_1_encoded= np.array(constructor_year_1_encoded)
    constructor_year_2_encoded= np.array(constructor_year_2_encoded)
    constructor_year_vocab_size = len(constructor_year_tokenizer.word_index) + 1
    print('Constructor-year vocabulary Size: %d' % constructor_year_vocab_size)

    gp_tokenizer = Tokenizer(filters='!"#$%&()*+,-/ :;<=>?@[\]^`{|}~ ')
    gp_tokenizer.fit_on_texts(gp)
    gp_encoded = gp_tokenizer.texts_to_sequences(gp)
    gp_encoded = np.array(gp_encoded)
    gp_vocab_size = len(gp_tokenizer.word_index) + 1
    print('GP vocabulary Size: %d' % gp_vocab_size)


    ###########################################
    ##### Model definition and training ######
    ##########################################
    print ("Model training started...")
    inputs = Input(shape=(X_train.shape[1],))

    x1 = Dropout(rate=0.1, seed=1)(inputs)
    x2 = Dense(50, activation='selu', kernel_initializer = 'lecun_normal')(x1)

    x2 = BatchNormalization()(x2)

    # Driver embedding
    driver_1_input = Input(shape=(1,), name='driver_1_input')
    driver_2_input = Input(shape=(1,), name='driver_2_input')
    driver_emb = Embedding(driver_vocab_size, 20, input_length=1, name='drivers_emb', embeddings_initializer = 'lecun_normal')

    driver_emb_1 = driver_emb(driver_1_input)
    driver_emb_1 = Flatten()(driver_emb_1)

    driver_emb_2 = driver_emb(driver_2_input)
    driver_emb_2 = Flatten()(driver_emb_2)

    driver_emb_diff = Subtract()([driver_emb_1, driver_emb_2])

    # Constructor embedding
    team_1_input = Input(shape=(1,), name='team_1_input')
    team_2_input = Input(shape=(1,), name='team_2_input')
    team_emb = Embedding(constructor_vocab_size, 20, input_length=1, name='team_emb', embeddings_initializer = 'lecun_normal')

    team_emb_1 = team_emb(team_1_input)
    team_emb_1 = Flatten()(team_emb_1)

    team_emb_2 = team_emb(team_2_input)
    team_emb_2 = Flatten()(team_emb_2)

    team_emb_diff = Subtract()([team_emb_1, team_emb_2])

    # GP embedding
    gp_input = Input(shape=(1,), name='gp_input')
    gp_emb = Embedding(gp_vocab_size, 10, input_length=1, name='gp_emb', embeddings_initializer = 'lecun_normal')(gp_input)
    gp_emb = Flatten()(gp_emb)

    # Constructor-year embedding
    team_year_1_input = Input(shape=(1,), name='team_year_1_input')
    team_year_2_input = Input(shape=(1,), name='team_year_2_input')
    team_year_emb = Embedding(constructor_year_vocab_size, 20, input_length=1, name='team_year_emb', embeddings_initializer = 'lecun_normal')

    team_year_emb_1 = team_year_emb(team_year_1_input)
    team_year_emb_1 = Flatten()(team_year_emb_1)

    team_year_emb_2 = team_year_emb(team_year_2_input)
    team_year_emb_2 = Flatten()(team_year_emb_2)

    team_year_emb_diff = Subtract()([team_year_emb_1, team_year_emb_2])


    all_input = concatenate([x2, driver_emb_diff, team_emb_diff, gp_emb, team_year_emb_diff])
    all_input = Dropout(rate=0.1, seed=1)(all_input)
    all_input = Dense(50, activation='selu', activity_regularizer=regularizers.l1(0.0001), kernel_initializer = 'lecun_normal')(all_input)


    predictions = Dense(1, activation='sigmoid', kernel_initializer = 'lecun_normal')(all_input)

    model = Model(inputs = [inputs, driver_1_input, driver_2_input, team_1_input, team_2_input,
                            gp_input, team_year_1_input, team_year_2_input], outputs = predictions)

    model.compile(optimizer=SGD(lr=0.02, momentum=0.95, decay=0.0001, nesterov=True),
                  loss='binary_crossentropy',
                  metrics=['accuracy'])

    callbacks = [EarlyStopping(monitor='val_loss', patience=5,
                              min_delta=0.0001, verbose=0)]

    model.fit([X_train, driver_1_encoded, driver_2_encoded, constructor_1_encoded, constructor_2_encoded,
               gp_encoded, constructor_year_1_encoded, constructor_year_2_encoded], y_train,
              batch_size=64,
              epochs=300,
              shuffle = True,
              verbose = 1,
              validation_split = 0.2,
              callbacks=callbacks)

    ###########################################
    ######## Save embedding weights ##########
    ##########################################
    print ("Saving embeddings and tokenizer values...")

    layer_names = ["drivers_emb", "team_emb", "team_year_emb", "gp_emb"]
    friendly_names = ["drivers_embeddings", "team_embeddings", "team_year_embeddings", "gp_embeddings"]

    for l, f in zip(layer_names, friendly_names):
        embeddings = model.get_layer(l).get_weights()[0]
        np.save(f + ".npy", embeddings)

    ###########################################
    ######## Save tokenizer values ###########
    ##########################################
    tokenizers = [driver_tokenizer, constructor_tokenizer, constructor_year_tokenizer, gp_tokenizer]
    friendly_names = ["drivers_names", "team_names", "team_year_names", "gp_names"]

    for t, f in zip(tokenizers, friendly_names):
        sorted_x = sorted(t.word_index.items(), key=operator.itemgetter(1))
        names = ["----"]
        for i in sorted_x:
            names.append(i[0].title().replace('_', ' ').replace('Grand Prix', 'GP'))

        with open(f + ".txt", "w") as file:
            file.write(str(names))
