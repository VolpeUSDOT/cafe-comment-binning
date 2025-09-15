from semantic_text_splitter import TextSplitter, CodeSplitter
from tokenizers import Tokenizer
import tree_sitter_python
from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from tqdm import tqdm
import numpy as np

def tikToken_split(docstring, max_tokens = 1000):
    splitter = CodeSplitter.from_tiktoken_model(tree_sitter_python.language(), "gpt-3.5-turbo", max_tokens)
    return splitter.chunks(docstring)

def hugging_split(docstring, max_tokens = 1000):
    max_tokens = 1000
    tokenizer = Tokenizer.from_pretrained("bert-base-uncased")
    splitter = CodeSplitter.from_huggingface_tokenizer(tree_sitter_python.language(), tokenizer, max_tokens)
    return splitter.chunks(docstring)

def splitDocument(doctring, min_characters = 100, max_characters = 250):
    '''
    Takes a document that has already been converted to string format and divides it up into chunks to be categorized
    '''
    splitter = TextSplitter((min_characters, max_characters), trim=True)
    chunks = splitter.chunks(doctring)
    return chunks

def tokenizeChunks(chunks):
    '''
    convert new data to tokenized form to be fed to NN
    '''
    vectorizer = TfidfVectorizer(
        sublinear_tf=True, max_df=0.5, min_df=5, stop_words="english"
    )
    X_data = vectorizer.fit_transform(chunks)
    X_data = X_data.toarray()

    # Convert testing data format to csr_matrix for scikit
    rows = []
    cols = []
    data = []
    # test_df = test_df.reset_index()
    for i, row in tqdm(enumerate(X_data)):
        data_in_row = row
        for feature_num, val in enumerate(data_in_row):
            if val != 0:
                rows.append(i)
                cols.append(feature_num)
                data.append(val)

    row = np.array(rows)
    col = np.array(cols)
    data = np.array(data)
    tokenizedChunks = csr_matrix((data, (row, col)), shape=(i+1, len(data_in_row)))

    return tokenizedChunks
