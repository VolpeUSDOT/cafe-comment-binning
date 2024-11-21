import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from imblearn.over_sampling import SMOTE
from collections import Counter
from typing import Literal
from tqdm import tqdm
from scipy.sparse import csr_matrix
import os


def createTrainTestData():
    '''
    Reads excel file provided by CAFE team and crates separate testing and training data for later use.
    Training data is subsidized with duplicate sampling.
    '''
    if os.path.isfile('train_df.csv') and os.path.isfile('test_df.csv'):
        train_df = pd.read_csv('train_df.csv')[['Comments', 'BIN 1']]
        test_df = pd.read_csv('test_df.csv')
        return train_df, test_df

    # Pull data from excel file
    df = pd.read_excel('CAFECommentsHuman.xlsx')

    # Remove nan rows
    df = df.dropna().reset_index()

    # Fix formatting in bin1 column
    df['BIN 1'] = df['BIN 1'].str.strip().str.lower()

    # Find how many comments are in each bin and cut out the smallest categories since we don't have enough data to train for them
    bin_totals = df['BIN 1'].value_counts()

    bin_totals = bin_totals.loc[bin_totals > 50]
    df = df.loc[df['BIN 1'].isin(bin_totals.index)].reset_index()[['Comments', 'BIN 1']]

    # Create train and test datasets. Address imbalance with oversampling by duplication
    rng = np.random.default_rng()
    df['TestTrain'] = rng.random(df.shape[0])
    df['TestTrain'] = df['TestTrain'].apply(lambda x: 'Test' if x > 0.8 else 'Train')

    # Separate testing and Training Data
    test_df = df.loc[df['TestTrain'] == 'Test'].reset_index()[['Comments', 'BIN 1']]
    train_df = df.loc[df['TestTrain'] == 'Train'].reset_index()[['Comments', 'BIN 1']]

    # Oversample training data with duplication
    train_bin_max = train_df['BIN 1'].value_counts().max()
    train_df = train_df.groupby(['BIN 1']).sample(n=train_bin_max, replace=True).reset_index()

    test_df = test_df[['Comments', 'BIN 1']].reset_index()
    train_df = train_df[['Comments', 'BIN 1']].reset_index()

    train_df.to_csv('train_df.csv')
    test_df.to_csv('test_df.csv')

    return train_df, test_df

def vectorizeDataset(train_df, test_df):
    '''
    Test and train are done together to ensure target mapping is the same between the two data sets

    NOTE: This is a very simple vectorizer (apparently uses regex under the hood) and works by assigning weights based on the uniqueness of words in the dataset.
    It is possible that due to this, the oversampling by duplication in the training data may become an issue.
    '''
    # Target_names are the categories or bins we are trying to sort into
    target_names = np.unique(train_df['BIN 1']).tolist()

    # Target is an integer that is associated with a target name. Basically the index of the target_names array. Maybe unnecessary?
    y_train = train_df['BIN 1']
    y_test = test_df['BIN 1']
    # for element in train_df['BIN 1']:
    #     y_train = target_names.index(element)
    # for element in test_df['BIN 1']:
    #     y_test = target_names.index(element)

    # Extracting features from the data using a sparse vectorizer
    vectorizer = TfidfVectorizer(
        sublinear_tf=True, max_df=0.5, min_df=5, stop_words="english"
    )
    X_train = vectorizer.fit_transform(train_df['Comments'].values)
    X_test = vectorizer.fit_transform(test_df['Comments'].values)

    # Feature names are all the unique words or word-segments that have been tokenized
    feature_names = vectorizer.get_feature_names_out()

    return X_train, X_test, y_train, y_test, feature_names, target_names

# train_df, test_df = createTrainTestData()
# X_train, X_test, y_train, y_test, feature_names, target_names = vectorizeDataset(train_df, test_df)


# Weighted Average Sampling
def recursive_sampler(total_size, current_list, train_to_test_ratio = 0.8,):
    current_length = len(current_list)
    if current_length == total_size:
        return current_list

    # Calculate weights
    remaining_list_weight = (total_size - current_length) / total_size
    current_list_weight = current_length / total_size

    # Calculate averages
    counts = dict(Counter(current_list))
    if 'Train' in counts:
        current_train = counts['Train']
    else:
        current_train = 0

    # Avoid div by zero
    if current_length > 0:
        current_ratio = current_train / (current_length)
    else:
        current_ratio = train_to_test_ratio

    remaining_odds = (train_to_test_ratio - (current_ratio*current_list_weight)) / remaining_list_weight

    # Add a new value to the list
    if np.random.rand() < remaining_odds:
        current_list.append('Train')
    else:
        current_list.append('Test')
    # Call recursively
    return recursive_sampler(total_size=total_size, current_list=current_list, train_to_test_ratio=train_to_test_ratio)


oversampling_ID = Literal['Duplicate Equal',
                       'Duplicate Equal Large',
                       'Duplicate Ratio',
                       'SMOTE',
                       'SMOTE Ratio',
                       'None']

def createData(oversampling: oversampling_ID):
    '''
    Reads excel file provided by CAFE team and crates separate testing and training data for later use.
    Training data is subsidized with duplicate sampling.
    '''
    # Pull data from excel file
    df = pd.read_excel('CAFECommentsHuman.xlsx')

    # Remove nan rows
    df = df.dropna().reset_index()

    # Fix formatting in bin1 column
    df['BIN 1'] = df['BIN 1'].str.strip().str.lower()

    # Group all small bins into an "Other" bin
    bin_totals = df['BIN 1'].value_counts().reset_index()
    # print(bin_totals)
    small_bins = bin_totals.loc[(bin_totals['count'] < 50)]['BIN 1']
    df['BIN 1'] = np.where(df['BIN 1'].isin(small_bins), 'other', df['BIN 1'])

    bin_totals = df['BIN 1'].value_counts()
    # print(bin_totals)
    # df = df.loc[df['BIN 1'].isin(bin_totals.index)].reset_index()[['Comments', 'BIN 1']]

    df = df.reset_index()[['Comments', 'BIN 1']]

    # Get list of unique target names
    target_names = np.unique(df['BIN 1']).tolist()

    # Create train and test datasets. Goal is to use about 80% of available data in each bin for training.

    # In theory this approach should give about 80% of each group
    # In reality, this allows for imbalance in the test/train data split across bins
    # rng = np.random.default_rng()
    # df['TestTrain'] = rng.random(df.shape[0])
    # df['TestTrain'] = df['TestTrain'].apply(lambda x: 'Test' if x > 0.8 else 'Train')

    # This method guarantees that close to 80% of each bin will be used for training
    grouped_df = df.groupby('BIN 1')
    sampled_groups = []
    for _, group in grouped_df:
        # Shuffle data
        group = group.sample(frac=1)
        group['TestTrain'] = recursive_sampler(total_size=group.shape[0], current_list=[])
        sampled_groups.append(group)

    # NOTE: Data MUST be sorted or reset because comments are later vecotrized and
    # stored in an array who's index will be reset but must still match the bin column
    df = pd.concat(sampled_groups).reset_index()

    # Vectorize before splitting to ensure feature list is consistent across data
    # NOTE: Vectorizing before oversampling via duplicating. I think this is good, but should maybe experiment with this
    vectorizer = TfidfVectorizer(
        sublinear_tf=True, max_df=0.5, min_df=5, stop_words="english"
    )
    X_data = vectorizer.fit_transform(df['Comments'].values)
    X_data = X_data.toarray()

    feature_names = vectorizer.get_feature_names_out()

    # Separate Training Data
    train_df = df.loc[df['TestTrain'] == 'Train'][['Comments', 'BIN 1']]
    # print(train_df['BIN 1'].value_counts())

    # Oversample training data
    if oversampling == 'Duplicate Equal':
        train_bin_max = train_df['BIN 1'].value_counts().max()
        train_df = train_df.groupby(['BIN 1']).sample(n=train_bin_max, replace=True).reset_index()
    elif oversampling == 'Duplicate Equal Large':
        train_bin_max = 1000
        train_df = train_df.groupby(['BIN 1']).sample(n=train_bin_max, replace=True).reset_index()
    elif oversampling == 'Duplicate Ratio':
        grouped_df = df.groupby('BIN 1')
        sampled_groups = []
        for _, group in grouped_df:
            group = group.sample(frac=5)
            group['TestTrain'] = recursive_sampler(total_size=group.shape[0], current_list=[])
            sampled_groups.append(group)
        train_df = train_df.groupby(['BIN 1']).sample(n=train_bin_max, replace=True).reset_index()
    elif oversampling == 'None':
        train_df = train_df.reset_index()
    else:
        train_df = train_df.reset_index()
    # NOTE: SMOTE oversampling must occur later

    # Save array of training targets
    train_targets = train_df['BIN 1']

    # Convert training data format to csr_matrix for scikit
    rows = []
    cols = []
    data = []
    for i, row in tqdm(train_df.iterrows()):
        data_in_row = X_data[row['index']]
        for feature_num, val in enumerate(data_in_row):
            if val != 0:
                rows.append(i)
                cols.append(feature_num)
                data.append(val)

    row = np.array(rows)
    col = np.array(cols)
    data = np.array(data)
    X_train = csr_matrix((data, (row, col)), shape=(i+1, len(data_in_row)))
    # print(X_train)

    # SMOTE oversample if selected
    if oversampling == 'SMOTE':
        smote_data = SMOTE()
        X_train, train_targets = smote_data.fit_resample(X_train, train_targets)
        # counter = Counter(y)
        # print(counter)
    elif oversampling == 'SMOTE Ratio':
        smote_data = SMOTE(sampling_strategy=0.5) #TODO: This value can be played with
        X_train, train_targets = smote_data.fit_resample(X_train, train_targets)
        # counter = Counter(y)
        # print(counter)

    # Separate Testing Data
    test_df = df.loc[df['TestTrain'] == 'Test'][['Comments', 'BIN 1']]

    # Save array of testing targets
    test_targets = test_df['BIN 1']

    # Convert testing data format to csr_matrix for scikit
    rows = []
    cols = []
    data = []
    test_df = test_df.reset_index()
    for i, row in tqdm(test_df.iterrows()):
        data_in_row = X_data[row['index']]
        for feature_num, val in enumerate(data_in_row):
            if val != 0:
                rows.append(i)
                cols.append(feature_num)
                data.append(val)

    row = np.array(rows)
    col = np.array(cols)
    data = np.array(data)
    X_test = csr_matrix((data, (row, col)), shape=(i+1, len(data_in_row)))
    # print(X_test)



    return X_train, X_test, train_targets, test_targets, feature_names, target_names

createData(oversampling='SMOTE')
