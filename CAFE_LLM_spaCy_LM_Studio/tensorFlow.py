import tensorflow as tf
from tensorflow import Sequential
from tensorflow import TextVectorization, Embedding, Dense
from sklearn.metrics import accuracy_score, classification_report
import pandas as pd
import numpy as np

## Load Excel file
FILE_PATH = "legalVnon_legal.xlsx"
DATA_FRAME = pd.read_excel(FILE_PATH)

## Define text classification model
model = Sequential([
    TextVectorization(max_tokens=1000),
    Embedding(input_dim=1000, output_dim=128),
    Dense(64, activation='relu'),
    Dense(2, activation='softmax')
])

## Compile model
model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

## Prepare data
train_texts = DATA_FRAME['Comments']
train_labels = np.where(DATA_FRAME['Actual Label'] == 'legal', 0, 1)

## Train model
model.fit(train_texts, train_labels, epochs=5)

## Predict
predictions = model.predict(DATA_FRAME['Comments'])
predicted_labels = np.argmax(predictions, axis=1)
predicted_labels = np.where(predicted_labels == 0, 'legal', 'non-legal')

## Evaluate
accuracy = accuracy_score(DATA_FRAME['Actual Label'], predicted_labels)
print("Accuracy:", accuracy)
print("Classification Report:")
print(classification_report(DATA_FRAME['Actual Label'], predicted_labels))

## Save updated DataFrame to Excel
DATA_FRAME['Predicted Label'] = predicted_labels
DATA_FRAME.to_excel('updated_legalVnon_legal.xlsx', index=False)