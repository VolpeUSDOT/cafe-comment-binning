import spacy
import pandas as pd
import random
import numpy as np
import time

start_time = time.time()
# Load pre-trained English model
nlp = spacy.load("en_core_web_md")

categories = ['legal', 'non-legal']

# Add classy_classification to pipeline
nlp.add_pipe("classy_classification", after="ner")

# Add labels
for label in categories:
    nlp.get_pipe("classy_classification").add_label(label)

nlp.get_pipe("classy_classification").dropout = 0.2

# Hyperparameters
epochs = 10
batch_size = 10
learning_rate = 1e-4
best_accuracy = 0

# Begin training
nlp.begin_training()
nlp._optimizer.learn_rate = learning_rate

def convert_data(data_frame, categories):
    train_data = []
    
    for _, row in data_frame.iterrows():
        comment = str(row['Comments']).strip()
        category = str(row['BIN1']).strip().lower()
        labels = {"cats": {}}
        for cat in categories:
            labels["cats"][cat] = 1.0 if category == cat else 0.0
        
        train_data.append((comment, labels))
    
    return train_data

# Load Excel file
file_path = "legalVnon_legal.xlsx"
df = pd.read_excel(file_path)

# Prepare training data
train_data = convert_data(df[['Comments', 'BIN1']].iloc[1:751], categories)

# Convert train_data to Example objects
examples = [spacy.training.Example.from_dict(nlp.make_doc(text), labels) for text, labels in train_data]

# Update the losses dictionary to use "classy_classification"
for epoch in range(epochs):
    print(f"Starting epoch {epoch+1}")
    examples_epoch = examples.copy()
    for i in range(0, len(examples_epoch), batch_size):
        batch = examples_epoch[i:i+batch_size]
        random.shuffle(batch)
        nlp.update(batch, losses={"classy_classification": 0.0})

# Save the model
nlp.to_disk("C:\\Users\\jeremiah.hicks\\Desktop\\LLM Project")
print("Training complete")

end_time = time.time()
training_time = end_time - start_time
print(f"Training time: {training_time:.2f} seconds")