# Attempting to test out LM Studio with LiteLLM and possibly (Ollama and AutoGen)

from openai import OpenAI
import pandas as pd

client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")
df = pd.read_excel("kshotALL.xlsx")
text_column = "comment"
answer_column = "predicted"
actual_answer = "actual"
labels = ["legal", "compliance", "economics", "technology"]
output_file = "conveyor_belt.xlsx"
MAX_PROMPTS = 3


def get_prompt(text_to_categorize, prompt):

    return f"This text: {text_to_categorize} is {prompt}? True or False. Please only respond with 'True' or 'False'"


def re_prompt(_model):
    # Re-prompt if not true or false
    completion = client.completions.create(
        prompt="Please respond with only 'True' or 'False'.",
        model=_model,
        temperature=0.7,
        max_tokens=100,
    )
    return completion


def get_label(text_to_categorize):
    # Level 1: Is the comment more likely to be legal or not?
    re_prompt_count = 0
    legal_prompt = "related to laws, regulations, statutes, changes to laws, and formal codes of laws or rules and rulemaking"
    completion = client.completions.create(
        prompt=get_prompt(
            text_to_categorize,
            legal_prompt,
        ),
        model="calme-2.3-legalkit-8b",
        temperature=0.7,
        max_tokens=100,
    )
    response = completion.choices[0].text.strip()
    print(f"Response: {response}")

    # Extract the "True" or "False" answer from the response
    answer = None
    if "true" in response.lower():
        answer = "True"
    elif "false" in response.lower():
        answer = "False"

    if answer is None:
        while re_prompt_count < MAX_PROMPTS:
            response = re_prompt("calme-2.3-legalkit-8b").choices[0].text.strip()
            print(f"Response: {response}")
            if "true" in response.lower():
                answer = "True"
                break
            elif "false" in response.lower():
                answer = "False"
                break
            re_prompt_count += 1

    if answer is None:
        return "error"
    elif answer == "True":
        return "legal"

    # Level 2: Is the comment more likely to be economics or not?
    econ_prompt = "related to the economy, changes in budgets, or impacts of changes on the economy."
    completion = client.completions.create(
        prompt=get_prompt(text_to_categorize, econ_prompt),
        model="gemma-2-27b-it",
        temperature=0.7,
        max_tokens=100,
    )
    response = completion.choices[0].text.strip()
    print(f"Response: {response}")

    # Extract the "True" or "False" answer from the response
    answer = None
    if "true" in response.lower():
        answer = "True"
    elif "false" in response.lower():
        answer = "False"

    if answer is None:
        re_prompt_count = 0
        while re_prompt_count < MAX_PROMPTS:
            response = re_prompt("gemma-2-27b-it").choices[0].text.strip()
            print(f"Response: {response}")
            if "true" in response.lower():
                answer = "True"
                break
            elif "false" in response.lower():
                answer = "False"
                break
            re_prompt_count += 1

    if answer is None:
        return "error"
    elif answer == "True":
        return "economics"

    # Level 3: Is the comment more likely technology?
    tech_prompt = "related to improvements or changes in technology such as batteries or other vehicle technology"
    completion = client.completions.create(
        prompt=get_prompt(text_to_categorize, tech_prompt),
        model="gemma-2-27b-it",
        temperature=0.7,
        max_tokens=100,
    )
    response = completion.choices[0].text.strip()
    print(f"Response: {response}")

    answer = None
    if "true" in response.lower():
        answer = "True"
    elif "false" in response.lower():
        answer = "False"

    if answer is None:
        re_prompt_count = 0
        while re_prompt_count < MAX_PROMPTS:
            response = re_prompt("gemma-2-27b-it").choices[0].text.strip()
            print(f"Response: {response}")
            if "true" in response.lower():
                answer = "True"
                break
            elif "false" in response.lower():
                answer = "False"
                break
            re_prompt_count += 1

    if answer is None:
        return "error"
    elif answer == "True":
        return "technology"

    # Level 4: Compliance?
    compliance_prompt = "related to complying with rules, laws, or regulations"
    completion = client.completions.create(
        prompt=get_prompt(text_to_categorize, compliance_prompt),
        model="gemma-2-27b-it",
        temperature=0.7,
        max_tokens=100,
    )
    response = completion.choices[0].text.strip()
    print(f"Response: {response}")

    # Extract the "True" or "False" answer from the response
    answer = None
    if "true" in response.lower():
        answer = "True"
    elif "false" in response.lower():
        answer = "False"

    if answer is None:
        re_prompt_count = 0
        while re_prompt_count < MAX_PROMPTS:
            response = re_prompt("gemma-2-27b-it").choices[0].text.strip()
            print(f"Response: {response}")
            if "true" in response.lower():
                answer = "True"
                break
            elif "false" in response.lower():
                answer = "False"
                break
            re_prompt_count += 1

    if answer is None:
        return "error"
    elif answer == "True":
        return "compliance"
    else:
        return "other"


# Read the existing output file
try:
    output_df = pd.read_excel(output_file)
except FileNotFoundError:
    output_df = df.copy()

# Find the last commented row
last_commented_index = (
    output_df[output_df[answer_column].notnull()].index.max()
    if answer_column in output_df.columns
    else -1
)

# Start processing from the next row
for index, row in df.iterrows():
    if index <= last_commented_index:
        continue

    text_to_categorize = row[text_column]
    label = get_label(text_to_categorize)

    # Write the label to the DataFrame
    df.at[index, answer_column] = label
    df.to_excel(output_file, index=False)
    print(f"Processed comment {index+1} of {len(df)}")

print("Processing Complete")
