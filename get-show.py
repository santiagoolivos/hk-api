import json
import requests


def get_show_hn_stories(endpoint):
    try:
        response = requests.get(f"https://hacker-news.firebaseio.com/v0/{endpoint}.json")
        if response.status_code != 200:
            print("Error fetching Show HN story IDs.")
            return []

        story_ids = response.json()

        stories = []
        for story_id in story_ids:
            story_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
            story_response = requests.get(story_url)
            if story_response.status_code == 200:
                story_data = story_response.json()
                title = story_data.get('title', '')
                # Verificar que el título comience con "Show HN"
                if title.startswith("Show HN:"):
                    print(story_data)
                    stories.append({
                      'origin': f'show_hn_{endpoint}',
                      'title': story_data.get('title'),
                      'username': story_data.get('by'),
                      'url': story_data.get('url'),
                      'description': story_data.get('text'),
                    })

        return stories
    except Exception as e:
        print(f"An error occurred: {e}")
        return []
      
def save_stories_to_file(stories, filename):
    try:
        with open(filename, 'w', encoding='utf-8') as file:
          file.write(json.dumps(stories, indent=4))
        print(f"Stories saved to {filename}")
    except Exception as e:
        print(f"Error saving to file: {e}")


if __name__ == "__main__":
    endpoints = [ 'newstories']
    for endpoint in endpoints:
        stories = get_show_hn_stories(endpoint)
        save_stories_to_file(stories, f'{endpoint}_stories.txt')
