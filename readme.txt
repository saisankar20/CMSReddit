
# README: Reddit Analyzer Scripts

## Overview
In this project, I have developed two Python scripts designed for analyzing subreddit activity and identifying trending keywords. These scripts utilize data fetched directly from Reddit:

1. CountMinsketchReddit.py: Implements the Count-Min Sketch algorithm to efficiently approximate counts of subreddit activity and keywords while being memory-conscious.
2. CountMinsketchRedditCompare.py: Offers precise counting functionality using Python's collections.Counter module.

Both scripts come with visualization tools to highlight active subreddits and trending keywords.

---

## Setup and Installation

### Prerequisites
Before you get started, ensure the following are in place:
1. Python Version: Python 3.7 or newer is required.
2. Reddit API Access: 
   - Register an app/script on [Reddit Apps](https://www.reddit.com/prefs/apps).
   - Retrieve the following credentials:
     - client_id
     - client_secret
     - user_agent

### Installing Dependencies
The required Python libraries can be installed via pip:

bash
pip install praw wordcloud matplotlib tkinter nltk pympler


Here’s what each library does:
- praw: Provides an interface to Reddit's API.
- wordcloud: Used for creating word clouds.
- matplotlib: Powers data visualizations.
- tkinter: Handles GUI interactions like progress dialogs.
- nltk: Assists with text preprocessing and stopword removal.
- pympler: Tracks memory usage.

Linux Users: Ensure tkinter is installed via your system package manager:

bash
sudo apt-get install python3-tk


### Download NLTK Stopwords Corpus
The scripts require the NLTK stopwords corpus. Run the following command once to download it:

python
import nltk
nltk.download('stopwords')


---

## Configuration

Update the placeholder Reddit API credentials in both scripts with your own details:

python
reddit = praw.Reddit(
    client_id="your_client_id",
    client_secret="your_client_secret",
    user_agent="your_user_agent"
)


---

## Running the Scripts

### Count-Min Sketch Script
To execute CountMinsketchReddit.py:
1. Run the script:
   bash
   python CountMinsketchReddit.py
   
2. Provide the following inputs via the GUI:
   - Number of submissions to process.
   - Time frame (in hours) for subreddit activity.
   - Error bound (ε) and confidence level (δ) for the Count-Min Sketch algorithm.

### Exact Counter Script
To execute CountMinsketchRedditCompare.py:
1. Run the script:
   bash
   python CountMinsketchRedditCompare.py
   
2. Provide the following inputs via the GUI:
   - Number of submissions to process.
   - Time frame (in hours) for subreddit activity.

---

## Features

### Shared Features
- Trending Subreddits: Visualizes the most active subreddits within a specified period.
- Trending Keywords: Creates a word cloud of popular keywords.

### Unique Features
- CountMinsketchReddit.py:
  - Provides approximate counts with adjustable error and confidence parameters.
  - Optimized for handling large datasets efficiently.
- CountMinsketchRedditCompare.py:
  - Offers exact counts for subreddit and keyword activity.

---

## Troubleshooting

1. API Issues:
   - Verify your client_id, client_secret, and user_agent are correctly set.
   - Ensure your Reddit app has appropriate permissions and your network connection is stable.
2. Dependency Problems:
   - Double-check that all required libraries are installed (pip install ...).
3. GUI Issues:
   - For Linux systems, ensure tkinter is installed:
     bash
     sudo apt-get install python3-tk
     

---

## Repository Contents

- CountMinsketchReddit.py: Implements approximate counting with Count-Min Sketch.
- CountMinsketchRedditCompare.py: Offers exact counting using collections.Counter.
- This README: A comprehensive guide to setting up and using the scripts.

---

## License
These scripts are released under the MIT License. Feel free to use, modify, and share them while providing appropriate credit.
