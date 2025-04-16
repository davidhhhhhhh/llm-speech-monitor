import json
import pandas as pd
import wikipediaapi

# Load the JSON files
with open('category_map.json', 'r') as f:
    category_map = json.load(f)

with open('topic_map.json', 'r') as f:
    topic_map = json.load(f)

# Initialize the Wikipedia API instance
wiki_wiki = wikipediaapi.Wikipedia(
    language='en',
    user_agent="AI_Auditing_Bot/1.0 (contact: your_email@example.com)"
)


def fetch_wikipedia_content(page_title):
    """
    Fetches the content of a Wikipedia page given its title.
    Returns the page text if the page exists, otherwise a default message.
    """
    page = wiki_wiki.page(page_title)
    if page.exists():
        return page.text
    return "No content found."


def main(test_size=5):
    """
    Iterates over categories and topics, then fetches the content for each
    Wikipedia page listed in the topic_map. The results are saved to a CSV.

    The test_size parameter is used to limit the number of total entries processed
    (useful for initial testing).
    """
    rows = []  # List to store row dictionaries
    counter = 0

    # Iterate through each category and its associated topics
    for category, topics in category_map.items():
        for topic in topics:
            # Check if the current topic exists in the topic_map
            if topic in topic_map:
                wiki_pages = topic_map[topic]
                for wiki_page in wiki_pages:
                    print(f"Fetching content for: Category: {category}, Topic: {topic}, Wiki Page: {wiki_page}")
                    content = fetch_wikipedia_content(wiki_page)
                    # Calculate approximate token count using whitespace splitting
                    token_length = len(content.split())

                    # Append the data as a new row
                    rows.append({
                        "Category": category,
                        "Topic": topic,
                        "Topic_Wiki_Page": wiki_page,
                        "Topic_Wiki_Content": content,
                        "Token_Length": token_length
                    })

                   # counter += 1
                    # For testing purposes: limit the number of entries processed
                    if counter >= test_size:
                        break
                if counter >= test_size:
                    break
        if counter >= test_size:
            break

    # Convert the list of rows to a DataFrame
    df = pd.DataFrame(rows)
    csv_file = 'wiki_content.csv'
    df.to_csv(csv_file, index=False)

    print(f"\n✅ Successfully saved {len(rows)} entries to '{csv_file}'.")


if __name__ == "__main__":
    main(test_size=5)  # comment counter plus for full processing
