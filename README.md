# Website Post Automation

This project automates the process of checking for new posts on specific websites (e.g., Variety) via RSS feeds and sending the relevant data to a WordPress website through a custom REST API endpoint. The script checks the RSS feed for updates, processes new posts, extracts content, and uploads posts with images to the WordPress site.

## Features
- **RSS Feed Integration**: The script parses an RSS feed from a website (e.g., Variety) to check for new posts.
- **Content Extraction**: Extracts content from the linked articles using BeautifulSoup to filter out unwanted elements.
- **Database Logging**: Saves processed posts into an SQLite database to prevent duplicate processing.
- **WordPress Integration**: Sends the post data (including title, link, content, and image) to a WordPress site via a custom REST API endpoint.
- **Automated Scheduling**: Uses `APScheduler` to run the check for new posts at regular intervals.

## Prerequisites
Before running this project, ensure you have the following installed:
- Python 3.x
- `pip` for installing Python packages
- WordPress site. 
- SQLite database (the script will create one automatically)

## Installation

### 1. Clone the repository
Clone this repository to your local machine using Git:

### 2. Create a folder in your WordPress site named job_cron
Go into wp-content/themes/your_theme -> create **job_cron** folder.
Paste both the php files in that folder

### 3. functions.php
paste this line of code at the end of your functions.php file
```bash
require get_theme_file_path('/job_cron/jobScheduler.php');
```

```bash
git clone https://github.com/bharat29tyagi/automation_assignment
cd automation_assignment
pip install -r requirements.txt
python3 index.py
```
