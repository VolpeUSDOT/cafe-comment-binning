import pandas as pd
from collections import Counter
import re


# Function to load stop words from a file
def load_stop_words(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        stop_words = {line.strip().lower() for line in file if line.strip()}
    return stop_words


# Function to extract the ten most common words from the text
def extract_most_common_words(text, stop_words, num_words=10):
    # Remove punctuation and split the text into words
    words = re.findall(r"\b\w+\b", text.lower())  # Convert text to lowercase
    filtered_words = [word for word in words if word not in stop_words]
    # Count the frequency of each word
    word_counts = Counter(filtered_words)
    # Return the most common words
    return [word for word, _ in word_counts.most_common(num_words)]


# Load the Excel file
file_path = "two_columns.xlsx"
df = pd.read_excel(file_path)

# Load the stop words
stop_words_file_path = "stop_words_english.txt"
stop_words = load_stop_words(stop_words_file_path)

# Specify the column names (or indices) to work with
comment_col = "comment"
category_col = "category"
output_column = "MostCommonWords"

# Create a dictionary to accumulate results
aggregated_results = {}

# Iterate through each row in the DataFrame
for index, row in df.iterrows():
    # Extract text from the row
    text = row[comment_col]

    # Ensure the category is not NaN, then strip whitespace and convert to lowercase
    if pd.notna(row[category_col]):
        category_name = row[category_col].strip().lower()
    else:
        continue

    if pd.notna(text):
        # Extract the ten most common words from the text, excluding stop words
        most_common_words = extract_most_common_words(text, stop_words)

        # If the category already exists, update the accumulated counts
        if category_name in aggregated_results:
            aggregated_results[category_name].update(most_common_words)
        else:
            aggregated_results[category_name] = Counter(most_common_words)

# Prepare the output DataFrame
output_df = pd.DataFrame()

# Create a new DataFrame with the categories and their most common words
for category_name, word_counts in aggregated_results.items():
    most_common = [word for word, _ in word_counts.most_common(10)]
    output_df = output_df.append(
        {category_col: category_name, output_column: most_common}, ignore_index=True
    )

# Save the output DataFrame to a new Excel file
output_file_path = "common_key_words.xlsx"
output_df.to_excel(output_file_path, index=False)

print(f"Processed and saved to {output_file_path}")
