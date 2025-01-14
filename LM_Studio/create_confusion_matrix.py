# Create a confusion matrix

import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import ConfusionMatrixDisplay
from sklearn.metrics import confusion_matrix

# Load Excel file
df = pd.read_excel("conveyor_belt_cleaned.xlsx")

# Extract actual and predicted labels
actual_labels = df["actual"].str.lower()
predicted_labels = df["predicted"].str.lower()

# Define unique labels
unique_labels = ["legal", "economics", "compliance", "technology", "other"]

# Create confusion matrix
cm = confusion_matrix(actual_labels, predicted_labels, labels=unique_labels)
cmd = ConfusionMatrixDisplay(cm, display_labels=unique_labels)
cmd.plot()
plt.title("Confusion Matrix for LLM Prediction on Comments Spreadsheet")
plt.show()
