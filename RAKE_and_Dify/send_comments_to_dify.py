import pandas as pd
import requests

# Getting the data from a one column version of the CAFE binned comments.
df = pd.read_excel("one column.xlsx")

print(df.head())
print(df.columns)

API_ENDPOINT = ""  # Will need the DOT Dify endpoint and API Key
API_KEY = ""


def categorize_comment(comment):
    if (
        pd.isnull(comment)
        or isinstance(comment, float)
        and (comment == float("inf") or comment == float("-inf"))
    ):
        return "Invalid comment"

    comment = str(comment)
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

    user_id = "jeremiah.hicks@dot.gov"

    data = {"query": comment, "user": user_id}

    response = requests.post(API_ENDPOINT, json=data, headers=headers)

    print(f"Response Status: {response.status_code}")
    print(f"Response Content: {response.text}")

    if response.status_code == 200:
        response_json = response.json()
        if "answer" in response_json:
            return response_json["answer"]
        else:
            return "No answer found"
    else:
        return f"Error: {response.status_code} - {response.text}"


df["Category"] = df["comment"].apply(categorize_comment)

df.to_excel("categorized_comments.xlsx", index=False)
