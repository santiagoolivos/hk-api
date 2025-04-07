from datetime import datetime
import requests
import json
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
from slack_sdk import WebClient

# Cargar variables del archivo .env
load_dotenv()

SLACK_TOKEN = os.getenv("SLACK_AUTH_TOKEN")
SLACK_CHANNEL = os.getenv("SLACK_CHANNEL_ID")
client = WebClient(token=SLACK_TOKEN)

def send_to_slack(filename):
    try:
        print(f"Sending file to Slack: {filename}")
        response = client.files_upload_v2(
            file=filename,
            title=f"Hacker News Shownew - {datetime.now().strftime('%d-%m-%Y')}",
            channel=SLACK_CHANNEL,
            initial_comment=f"Hacker News Shownew - {datetime.now().strftime('%d-%m-%Y')}",
        )

        if response.status_code == 200:
            print("File sent to Slack successfully.")
        else:
            print("Failed to send file to Slack:", response.json())
    except Exception as e:
        print(f"Error sending file to Slack: {e}")


def get_show_hn_stories_from_web():
    try:
        stories = []
        base_url = "https://news.ycombinator.com/shownew"
        next_id = None
        for offset in range(31, 181, 30):  # Iterar en saltos de 30 hasta 500
            if next_id:
                url = f"{base_url}?next={next_id}&n={offset}"
            else:
                url = f"{base_url}?n={offset}"
            
            print("Fetching URL:", url)
            response = requests.get(url)
            print("Response:", response.status_code)
            if response.status_code != 200:
                print(f"Error fetching Show HN page: {url}")
                break

            soup = BeautifulSoup(response.text, 'html.parser')

            story_ids = []
            for tr in soup.find_all('tr', class_='athing'):
                story_id = tr.get('id')
                if story_id:
                    story_ids.append(int(story_id))
                    
            print("story_ids", story_ids)

            if not story_ids:
                break

            for story_id in story_ids:
                story_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
                
                try: 
                    story_response = requests.get(story_url)
                    if story_response.status_code == 200:
                        story_data = story_response.json()
                        title = story_data.get('title', '')
                        print("show title", title)
                        if title.startswith("Show HN"):
                            stories.append({
                                'id': story_data.get('id'),
                                'origin': 'show_hn_newstories',
                                'title': story_data.get('title'),
                                'username': story_data.get('by'),
                                'url': story_data.get('url'),
                                'description': story_data.get('text'),
                                'discussion_url': f'https://news.ycombinator.com/item?id={story_id}'
                            })
                except Exception as e:
                    print(f"Error fetching story {story_id}: {e}")

            # Obtener el ID del último elemento para la próxima página
            next_id = story_ids[-1] if story_ids else None
            if not next_id:
                break

        return stories
    except Exception as e:
        print(f"An error occurred: {e}")
        return []


def save_stories_to_file(stories):
    try:
        date_str = datetime.now().strftime("%d-%m-%Y")
        filename = f"show-responses/show_hn_stories_{date_str}.txt"

        with open(filename, 'w', encoding='utf-8') as file:
            file.write(json.dumps(stories, indent=4))
        print(f"Stories saved to {filename}")
        
        send_to_slack(filename)
    except Exception as e:
        print(f"Error saving to file: {e}")


if __name__ == "__main__":
    stories = get_show_hn_stories_from_web()
    save_stories_to_file(stories)
    

    
