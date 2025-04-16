import requests
from bs4 import BeautifulSoup
import time
import json
import wikipediaapi
import csv

# List of exact topic titles to exclude
excluded_topics = {
    "American News Pathways 2020 Project",
    "American Trends Panel",
    "Future of the Internet (Project)",
    "Pew-Templeton Global Religious Futures Project",
    "State of the News Media (Project)",
    'Other Topics',
    'Test'
}

# Fetch topics from Pew Research website
url = 'https://www.pewresearch.org/topics/'
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

# Extract topics, skipping excluded ones
topics = []
for section in soup.find_all('div', class_='wp-block-prc-block-taxonomy-index-az-list'):
    for li in section.find_all('li'):
        topic = li.find('a').text.strip()
        if topic not in excluded_topics:
            topics.append(topic)


def clean_topic_for_wikipedia(topic):
    topic = topic.replace('&', 'and')
    return topic


# Clean topics
cleaned_topics = [clean_topic_for_wikipedia(topic) for topic in topics]

# Wikipedia API setup
wiki_wiki = wikipediaapi.Wikipedia(
    language='en',
    user_agent="AI_Auditing_Bot/1.0 (contact: daviddai@example.com)"
)

def search_term(term):
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        'action': 'query',
        'list': 'search',
        'srsearch': f'"{term}"',  # Enclose the term in double quotes for exact phrase search
        'format': 'json',
        'srlimit': 10  # Number of results to return
    }

    response = requests.get(url, params=params)
    data = response.json()

    suggestions = []
    if 'query' in data and 'search' in data['query']:
        for result in data['query']['search']:
            title = result['title']
            page = wiki_wiki.page(title)
            if page.exists():
                suggestions.append(title)
    return suggestions

def search_wikipedia_page(topic):
    # First, try searching the full topic
    suggestions = search_term(topic)

    # If nothing is found, then try splitting the topic
    if not suggestions:
        if ' and ' in topic:
            parts = topic.split(' and ')
        else:
            parts = [topic]

        split_suggestions = []

        for i, part in enumerate(parts):
            sub_parts = [part.strip()]

            # Further split the first part by commas if it contains any
            if i == 0 and ',' in part:
                sub_parts = [sub.strip() for sub in part.split(',') if sub.strip()]

            for sub in sub_parts:
                split_suggestions += search_term(sub)

        # Remove duplicates
        suggestions = list(set(split_suggestions))

    # Print results
    if suggestions:
        print(f"✅ Found valid pages for '{topic}': {suggestions}")
    else:
        print(f"❌ No valid pages found for topic: '{topic}'")

    return suggestions


def fallback_search(term):
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        'action': 'query',
        'list': 'search',
        'srsearch': term,  # use precise the term
        'format': 'json',
        'srlimit': 10  # Number of results to return
    }

    response = requests.get(url, params=params)
    data = response.json()

    suggestions = []
    if 'query' in data and 'search' in data['query']:
        for result in data['query']['search']:
            title = result['title']
            page = wiki_wiki.page(title)
            if page.exists():
                suggestions.append(title)

    if suggestions:
        print(f"✅ Found fallback pages for '{topic}': {suggestions}")
    else:
        print(f"❌ No fallback pages found for topic: '{topic}'")
    return suggestions


# Mapping topics
mapped_topics = {}
topic_records = []  # For CSV output

for topic in cleaned_topics:
    used_fallback = False

    results = search_wikipedia_page(topic)
    if not results:
        results = fallback_search(topic)
        used_fallback = True

    if not results:
        results = ["NA"]

    mapped_topics[topic] = results
    topic_records.append((topic, len(results) if results != ["NA"] else 0, used_fallback))

    time.sleep(0.1)

# Save mapping
with open('topic_map.json', 'w') as f:
    json.dump(mapped_topics, f, indent=4)

# Save CSV
with open('topic_counts.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Topic', 'Valid Wikipedia Pages Found', 'Used Fallback Search'])
    writer.writerows(topic_records)

print(f"\n✅ Successfully mapped {len(mapped_topics)} topics and wrote to topic_map.json and topic_counts.csv.")