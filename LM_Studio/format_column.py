# Replace invalid labels with "other" in the "actual" column

import pandas as pd

# Load Excel file
df = pd.read_excel("conveyor_belt.xlsx")

# Define valid labels
valid_labels = ["legal", "compliance", "economics", "technology"]

# Replace invalid labels with "other" in the "actual" column
df["actual"] = df["actual"].apply(
    lambda x: x if x.strip().lower() in valid_labels else "other"
)

# Save the updated Excel file
df.to_excel("conveyor_belt_cleaned.xlsx", index=False)
