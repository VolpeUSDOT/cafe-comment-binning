import pandas as pd

# Load the Excel file
df = pd.read_excel("two_columns.xlsx")

# Create a dictionary to store the concatenated comments for each category
category_comments = {}

# Iterate over each category
for category in df["category"].unique():
    # Filter the data for the current category
    category_data = df[df["category"] == category]

    # Replace missing values with an empty string
    category_data["comment"] = category_data["comment"].fillna("")

    # Concatenate all comments into a single string
    concatenated_comment = " ".join(category_data["comment"].astype(str))

    # Store the concatenated comment in the dictionary
    category_comments[category] = concatenated_comment

# Create a dictionary to store the word frequencies for each category
category_word_freq = {}

# Iterate over each category and its concatenated comment
for category, comment in category_comments.items():
    # Split the comment into words
    words = comment.split()

    # Create a set to store the unique words
    unique_words = set(words)

    # Store the unique words in the dictionary
    category_word_freq[category] = unique_words

# Create a set to store the words that appear in multiple categories
multi_category_words = set()

# Iterate over each category and its unique words
for category, words in category_word_freq.items():
    # Iterate over each word
    for word in words:
        # Check if the word appears in multiple categories
        if sum(1 for cat, ws in category_word_freq.items() if word in ws) > 1:
            multi_category_words.add(word)

# Remove words that appear in multiple categories
for category, words in category_word_freq.items():
    category_word_freq[category] = words - multi_category_words

# Create a list to store the output data
output_data = []

# Iterate over each category and its unique words
for category, words in category_word_freq.items():
    # Add the category and its unique words to the output data
    for word in words:
        output_data.append([category, word])

# Create a DataFrame from the output data
output_df = pd.DataFrame(output_data, columns=["Category", "Word"])

# Save the DataFrame to an Excel file
output_df.to_excel("output.xlsx", index=False)
