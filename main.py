import os
import pandas as pd
import glob
from pathlib import Path
from MinimalComputeApproach.prepCAFEData import *
from sklearn.linear_model import SGDClassifier

from KeywordClassify import keywordClassify
from TextSplitter.TextSplitter import *
from File_Parsing.FileTextRetriever import get_text

class SplitMethods:
    CUSTOM = 'custom'
    TIKTOKEN = 'tiktoken'
    HUGGING = 'hugging'

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

def concatenateComments(chunk_list, predictions, footers = ''):
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
    concat_comment_list.append({'Comment': footers, 'Bin': 'Footers'})
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

def getUniqueFileOutput(outputPath, filePath):
    '''
    Appends a numeric suffix to create a unique filename if one already exists.
    '''
    suffix = 0
    output_file = f'{outputPath}/binned_{Path(filePath).stem}_{suffix}.xlsx'

    while os.path.exists(output_file):
        output_file = f'{outputPath}/binned_{Path(filePath).stem}_{suffix}.xlsx'
        suffix += 1

    return output_file

if __name__ == "__main__":

    # USER: Set output path and directory containing files to bin here.
    dataPath = './Sample_Comments/'
    outputPath = './BinnedComments' 

    fileNames = glob.glob(f"{dataPath}*.*") # Currently only reading text files using "*txt" suffix
    
    if not os.path.exists(outputPath):
        os.makedirs(outputPath)

    failed_files = [ ]
    body = [ ]
    footers = ''
    for (filePath) in fileNames:
        _, file_extension = os.path.splitext(filePath)

        data = get_text(filePath)
        if type(data) is not str:
            body = data[0]
            footers = data[1]
        else:
            body = data
            footers = ''
        
        # PDFs are already split by paragraph.
        temp = type(body)
        if type(body) is not str:
            chunk_list = body
        else:
            # USER: Select comment splitting method here.
            method = SplitMethods.TIKTOKEN
                
            match method:
                case SplitMethods.CUSTOM:
                    chunk_list = splitDocument(body, min_characters=200, max_characters=800)
                case SplitMethods.TIKTOKEN:
                    chunk_list = tikToken_split(body, 250)
                case SplitMethods.HUGGING:
                    chunk_list = hugging_split(data)

        # Path to training data... may need to update with new "graded" comments for next rule
        trainingDataFilePath = 'C:/Users/Vincent.Livant/source/repos/CommentBinning/CommentBinning/CAFECommentsHuman.xlsx'

        # Format for SGD
        clf, tokenizedChunks = trainModelAllData(trainingDataFilePath, chunk_list)

        # Opaque box... spooky
        pred = clf.predict(tokenizedChunks)
        keywordDict = {'legal': ['regulation', 'policy']} # Need input from folks here...
        keywordClassification = keywordClassify(keywordDict, chunk_list)

        # Combine + IF intervention=true -> manually adjust 
        combinedPredictions = combinePredictions(keywordClassification, pred, chunk_list, requireIntervention=False)

        concat_comment_df = concatenateComments(chunk_list=chunk_list, predictions=combinedPredictions, footers = footers)

        # Handle duplicates by appending number suffix to output file name
        file_exists = os.path.exists(f'{outputPath}/binned_{Path(filePath).stem}.xlsx')
        output_file = f'{outputPath}/binned_{Path(filePath).stem}.xlsx' if not file_exists else getUniqueFileOutput(outputPath, filePath)

        # Output file
        concat_comment_df.to_excel(output_file)
