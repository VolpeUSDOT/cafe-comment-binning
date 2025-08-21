import nltk
from rake_nltk import Rake
import pandas as pd
from collections import defaultdict

nltk.download("punkt_tab")


def load_stop_words(file_path):
    """Load stop words from a file."""
    with open(file_path, "r", encoding="utf-8") as file:
        return {line.strip().lower() for line in file if line.strip()}


def extract_keywords(text, rake):
    """Extract keywords from text using RAKE."""
    rake.extract_keywords_from_text(text)
    ranked_phrases = [phrase.strip().lower() for phrase in rake.get_ranked_phrases()]
    ranked_phrases_with_scores = dict(rake.get_ranked_phrases_with_scores())
    return list(set(ranked_phrases)), ranked_phrases_with_scores


def process_comments(df, comment_col, category_col, stop_words_file_path):
    """Process comments and extract keywords."""
    stop_words = load_stop_words(stop_words_file_path)
    rake = Rake(stopwords=stop_words)

    aggregated_results = defaultdict(
        lambda: {"Ranked Phrases": set(), "Ranked Phrases with Scores": {}}
    )
    total_comments = len(df)
    for index, row in df.iterrows():
        text = row[comment_col]
        category_name = (
            row[category_col].strip().lower() if pd.notna(row[category_col]) else None
        )

        if pd.notna(text) and category_name:
            ranked_phrases, ranked_phrases_with_scores = extract_keywords(text, rake)
            aggregated_results[category_name]["Ranked Phrases"].update(ranked_phrases)
            for phrase, score in ranked_phrases_with_scores.items():
                if (
                    phrase
                    in aggregated_results[category_name]["Ranked Phrases with Scores"]
                ):
                    aggregated_results[category_name]["Ranked Phrases with Scores"][
                        phrase
                    ] += (", " + score)
                else:
                    aggregated_results[category_name]["Ranked Phrases with Scores"][
                        phrase
                    ] = score

        if index % 100 == 0:
            print(
                f"Processed {index+1} out of {total_comments} comments ({(index+1)/total_comments*100:.2f}%)"
            )

    print("Finished processing comments")
    return aggregated_results


def save_results(aggregated_results, output_file_path, category_col):
    """Save results to an Excel file."""
    output_df = pd.DataFrame()
    for category_name, results in aggregated_results.items():
        ranked_phrases = str(list(results["Ranked Phrases"]))
        ranked_phrases_with_scores = str(results["Ranked Phrases with Scores"])
        output_df = output_df._append(
            {
                category_col: category_name,
                "Ranked Phrases": ranked_phrases,
                "Ranked Phrases with Scores": ranked_phrases_with_scores,
            },
            ignore_index=True,
        )

    output_df.to_excel(output_file_path, index=False)


def main():
    # Load the Excel file
    file_path = "two_columns.xlsx"
    df = pd.read_excel(file_path)

    comment_col = "comment"
    category_col = "category"
    stop_words_file_path = "stop_words_english.txt"
    output_file_path = "keywords.xlsx"

    aggregated_results = process_comments(
        df, comment_col, category_col, stop_words_file_path
    )
    save_results(aggregated_results, output_file_path, category_col)

    print(f"Processed and saved to {output_file_path}")


if __name__ == "__main__":
    main()
