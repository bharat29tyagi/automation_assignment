# import feedparser
# import logging
# from apscheduler.schedulers.background import BackgroundScheduler
# import requests
# import sqlite3
# from bs4 import BeautifulSoup, SoupStrainer

# # Configure logging
# logging.basicConfig(
#     level=logging.INFO,  # Set to DEBUG for more detailed logs
#     format='%(asctime)s - %(levelname)s - %(message)s',
#     handlers=[
#         logging.FileHandler("script.log"),  # Log to a file
#         logging.StreamHandler()  # Log to the console
#     ]
# )

# variety_rss_url = "https://variety.com/feed/"

# # Initialize the database
# connection = sqlite3.connect("posts.db", check_same_thread=False)
# cursor = connection.cursor()

# cursor.execute('''
# CREATE TABLE IF NOT EXISTS posts (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     entry_id TEXT UNIQUE,
#     title TEXT,
#     link TEXT,
#     image TEXT
# )
# ''')
# connection.commit()

# # Function to check for new posts
# def check_for_new_posts():
#     logging.info("Checking for new posts...")
#     try:
#         feed = feedparser.parse(variety_rss_url)
#         for entry in feed.entries:
#             logging.info(f"THIS IS ENTRYTHIS IS ENTRYTHIS IS ENTRY :: {entry}")
#             # Check if the entry already exists in the database
#             cursor.execute("SELECT id FROM posts WHERE entry_id = ?", (entry.id,))
#             if cursor.fetchone():
#                 logging.debug(f"Post already processed: {entry.title}")
#                 continue

#             # New post found, process it
#             logging.info(f"New post found: {entry.title} - {entry.link}")
#             try:
#                 post = requests.get(entry.link, timeout=10)
#                 post.raise_for_status()

#                 # Extract content using BeautifulSoup
#                 only_tags_with_id_link2 = SoupStrainer(class_="pmc-paywall")
#                 soup = BeautifulSoup(post.content, 'html.parser', parse_only=only_tags_with_id_link2)
#                 content = soup.find_all('p')
#                 text_content = ''
#                 for p in content:
#                     unwanted_content = p.find('div')
#                     if unwanted_content:
#                         unwanted_content.decompose()
#                     text_content += p.get_text(strip=True) + ' '

#                 logging.info(f"Extracted content: {text_content}")

#                 # Insert the new post into the database
#                 cursor.execute(
#                     "INSERT INTO posts (entry_id, title, link, image) VALUES (?, ?, ?, ?)",
#                     (entry.id, entry.title, entry.link, "")  # Placeholder for image
#                 )
#                 connection.commit()
#                 logging.info("Post saved to database.")

#             except requests.exceptions.RequestException as e:
#                 logging.error(f"HTTP error while processing post: {e}")
#             except Exception as e:
#                 logging.error(f"Error processing post: {e}")

#         logging.info("Finished checking for posts.")
#     except Exception as e:
#         logging.error(f"An unexpected error occurred: {e}")

# # Schedule the task
# scheduler = BackgroundScheduler()
# scheduler.add_job(check_for_new_posts, 'interval', seconds=20)
# scheduler.start()

# logging.info("Script started. Press Ctrl+C to exit.")

# # Keep the program running
# try:
#     while True:
#         pass
# except (KeyboardInterrupt, SystemExit):
#     logging.info("Shutting down the script.")
#     scheduler.shutdown()
#     connection.close()

import feedparser
import logging
from apscheduler.schedulers.background import BackgroundScheduler
import requests
import sqlite3
from bs4 import BeautifulSoup, SoupStrainer
import json

# Configure logging(documentation)
logging.basicConfig(
    level=logging.INFO,  # Set to DEBUG for more detailed logs
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("script.log"),  # Log to file
        logging.StreamHandler()  # Log to console
    ]
)

variety_rss_url = "https://variety.com/feed/"
wordpress_endpoint = "https://my-wp-site.ddev.site/wp-json/job-cron/v1/receive-jobs" #change domain, keep this "/wp-json/job-cron/v1/receive-jobs"

# Initialize the database
connection = sqlite3.connect("posts.db", check_same_thread=False)
cursor = connection.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entry_id TEXT UNIQUE,
    title TEXT,
    link TEXT,
    image TEXT
)
''')
connection.commit()

# Function to check for new posts
def check_for_new_posts():
    logging.info("Checking for new posts...")
    try:
        feed = feedparser.parse(variety_rss_url)
        for entry in feed.entries:
            logging.info(f"Processing entry: {entry.title}")
            # Check if the entry already exists in the database
            cursor.execute("SELECT id FROM posts WHERE entry_id = ?", (entry.id,))
            if cursor.fetchone():
                logging.debug(f"Post already processed: {entry.title}")
                continue

            # New post found, process it
            logging.info(f"New post found: {entry.title} - {entry.link}")
            try:
                post = requests.get(entry.link, timeout=10)
                post.raise_for_status()

                # Extract content using BeautifulSoup(documentation page)
                only_tags_with_id_link2 = SoupStrainer(class_="pmc-paywall")
                soup = BeautifulSoup(post.content, 'html.parser', parse_only=only_tags_with_id_link2)
                content = soup.find_all('p')
                text_content = ''
                for p in content:
                    unwanted_content = p.find('div')
                    if unwanted_content:
                        unwanted_content.decompose()
                    text_content += p.get_text(strip=True) + ' '

                logging.info(f"Extracted content: {text_content}")

                # Prepare data for WordPress
                post_data = {
                    'jobsList': [
                        {
                            'jobid': entry.id, # redundant/doesnt exist
                            'jobname': entry.title,
                            'jobdescription': text_content,
                            # 'jobdatecreated': entry.published, to do: date format issue
                            # 'jobdateupdated': entry.published,
                            'featuredImageUrl': entry.media_thumbnail[0]['url'] if entry.media_thumbnail else '',
                        }
                    ]
                }
                
                # Set the headers
                headers = {
                        'Content-Type': 'application/json'
                }

                # Send the data to the WordPress REST API
                response = requests.post(wordpress_endpoint, json=post_data, headers=headers)
                if response.status_code == 200:
                    logging.info(f"Successfully sent post to WordPress: {entry.title}")
                else:
                    logging.error(f"Failed to send post to WordPress: {response.text}")

                # Insert the new post into the database
                cursor.execute(
                    "INSERT INTO posts (entry_id, title, link, image) VALUES (?, ?, ?, ?)",
                    (entry.id, entry.title, entry.link, entry.media_thumbnail[0]['url'] if entry.media_thumbnail else "")
                )
                connection.commit()
                logging.info("Post saved to database.")

            except requests.exceptions.RequestException as e:
                logging.error(f"HTTP error while processing post: {e}")
            except Exception as e:
                logging.error(f"Error processing post: {e}")

        logging.info("Finished checking for posts.")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

# Schedule the task
scheduler = BackgroundScheduler()
scheduler.add_job(check_for_new_posts, 'interval', seconds=20)
scheduler.start()

logging.info("Script started. Press Ctrl+C to exit.")

# Keep the program running
try:
    while True:
        pass
except (KeyboardInterrupt, SystemExit):
    logging.info("Shutting down the script.")
    scheduler.shutdown()
    connection.close()
