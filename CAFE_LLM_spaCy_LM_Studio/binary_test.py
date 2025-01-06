import spacy
import pandas as pd
import numpy as np
from spacy.language import Language
from spacy.matcher import Matcher
import warnings
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, roc_auc_score
from sklearn.utils.class_weight import compute_class_weight

# Suppress warnings
warnings.filterwarnings("ignore")

# Load SpaCy model
nlp = spacy.load("C:\\Users\\jeremiah.hicks\\Desktop\\LLM Project\\classy")

df_text = pd.read_excel("legalVnon_legal.xlsx")
df_text['Comments'] = df_text['Comments'].astype(str)  

comments = df_text['Comments'].iloc[751:1101].tolist()
comments = [text.strip().lower() for text in comments if isinstance(text, str)]
labels = df_text['BIN1'].iloc[751:1101].tolist()

df_labeled = pd.DataFrame(columns=['Comment', 'Label', 'Predicted Label'])

def process_comment(text, nlp):
    doc = nlp(text)
    return "legal" if doc.cats["legal"] > doc.cats["non-legal"] else "non-legal"

y_true = [label.lower() for label in labels]
y_pred = []
y_pred_probs_legal = []  # Separate list for legal probabilities
y_pred_probs_non_legal = []  # Separate list for non-legal probabilities

# Use nlp.pipe for batch processing
docs = list(nlp.pipe(comments, batch_size=50))

for doc, label in zip(docs, labels):
    predicted_label = "legal" if doc.cats["legal"] > doc.cats["non-legal"] else "non-legal"
    y_pred.append(predicted_label)
    
    # Append probabilities for both classes
    y_pred_probs_legal.append(doc.cats["legal"])
    y_pred_probs_non_legal.append(doc.cats["non-legal"])
    
    df_labeled.loc[len(df_labeled)] = [doc.text, label, predicted_label]

# Compute class weights
class_weights = compute_class_weight(class_weight='balanced', classes=np.unique(y_true), y=y_true)

print("Accuracy:", accuracy_score(y_true, y_pred))
print("Classification Report:")
print(classification_report(y_true, y_pred))
print("Confusion Matrix:")
print(confusion_matrix(y_true, y_pred))

if len(np.unique(y_true)) > 1:
    # Calculate ROC-AUC for legal class
    print("ROC-AUC (Legal):", roc_auc_score([1 if x == 'legal' else 0 for x in y_true], y_pred_probs_legal))
    
    # Calculate ROC-AUC for non-legal class
    print("ROC-AUC (Non-Legal):", roc_auc_score([1 if x == 'non-legal' else 0 for x in y_true], y_pred_probs_non_legal))

df_labeled.to_excel('binary_test.xlsx', index=False)