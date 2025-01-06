from MinimalComputeApproach.prepCAFEData import *
from sklearn.linear_model import SGDClassifier
from KeywordClassify import keywordClassify
from TextSplitter.TextSplitter import *
import pandas as pd

def trainModelAllData(filepath, chunks):
    df = pullDataFromExcel(filepath, train_to_test_ratio=1.00, printouts=False)

    num_chunks = len(chunks)
    chunk_data = {
        'Comments': chunks,
        'BIN 1': [None]*num_chunks,
        'TestTrain': ['Test']*num_chunks
    }
    chunk_df = pd.DataFrame(chunk_data)
    df = pd.concat([df, chunk_df], ignore_index=True)

    X_data, feature_names = vectorizeData(df)

    X_train, train_targets = oversampleTrainingData(oversampling='SMOTE', train_to_test_ratio=1, df=df, X_data=X_data)

    chunk_df = df.loc[df['TestTrain'] == 'Test'][['Comments', 'BIN 1']]

    # Convert testing data format to csr_matrix for scikit
    rows = []
    cols = []
    data = []
    chunk_df = chunk_df.reset_index()
    for i, row in tqdm(chunk_df.iterrows()):
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

    clf = SGDClassifier(loss="log_loss", alpha=1e-4, n_iter_no_change=3, early_stopping=True)
    clf.fit(X_train, train_targets)

    return clf, X_test

def concatenateComments(chunk_list, predictions):
    concat_comment_list = []
    current_bin = predictions[0]
    current_comment = ""
    start_index = 0
    stop_index = 0
    for i, pred in enumerate(predictions):
        if pred != current_bin:
            stop_index = i
            concat_comment_list.append({'Comment': " ".join(chunk_list[start_index:stop_index]), 'Bin': current_bin})
            start_index = i
            current_bin = pred

    # Add the last row
    concat_comment_list.append({'Comment': " ".join(chunk_list[start_index:]), 'Bin': current_bin})
    concat_comment_df = pd.DataFrame(concat_comment_list)
    return (concat_comment_df)

def combinePredictions(keywordClassification, nnPrediction, chunk_list, requireIntervention=False):
    '''
    Compare the classification of keywords and NN prediction.

    If require_intervention is False: keyword classification overrrides nnPrediction

    If require_intervention is True: terminal input will be required whenever keywordClassification does not match nnPrediction
    '''
    combinedPredictions = []
    # Loop through this b/c we know the format will always be the same
    for index, pred in enumerate(nnPrediction):
        keywordDict = keywordClassification[index]
        if requireIntervention:
            if keywordDict:
                classification = list(keywordDict)[0]
                if classification == pred:
                    combinedPredictions.append(classification)
                else:
                    print("=" * 80)
                    print("Categorization disagreement on chunk:")
                    print(chunk_list[index])
                    print("Keyword Results: " + keywordDict)
                    print("Neural Network Prediction: " + pred)
                    try:
                        print("Previous Chunk Classification: " + combinedPredictions[index-1])
                    except:
                        pass # prevent error where mismatch on first chunk prediction
                    print("-" * 80)
                    chosen_category = input("Type in the category you would like to proceed with")
                    print(chosen_category + " selected. Proceeding...")
                    print("=" * 80)
                    combinedPredictions.append(chosen_category)
            else:
                combinedPredictions.append(pred)

        else:
            if keywordDict:
                classification = list(keywordDict)[0]
                combinedPredictions.append(classification)
            else:
                combinedPredictions.append(pred)

    return combinedPredictions


if __name__ == "__main__":

    filepath = './TextSplitter/TestComments/NissanResponseHandModified.txt'
    with open(filepath, 'r') as file:
        data = file.read()

    chunk_list = splitDocument(data, min_characters=200, max_characters=350)
    filepath = '../CAFECommentsHuman.xlsx'
    clf, tokenizedChunks = trainModelAllData(filepath, chunk_list)

    pred = clf.predict(tokenizedChunks)

    keywordDict = {'legal': ['regulation', 'policy']}

    keywordClassification = keywordClassify(keywordDict, chunk_list)

    combinedPredictions = combinePredictions(keywordClassification, pred, chunk_list, requireIntervention=False)

    concat_comment_df = concatenateComments(chunk_list=chunk_list, predictions=combinedPredictions)

    # print(concat_comment_df)
    concat_comment_df.to_excel('Binned Comments Out.xlsx')
