import praw
import time
import hashlib
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import simpledialog
from tkinter import ttk
import threading
import nltk
from nltk.corpus import stopwords
import math
import random
from pympler import asizeof  # Import asizeof for memory measurement

# Download the stopwords corpus if you haven't already
nltk.download('stopwords')

# Functions to calculate width and depth based on error and confidence parameters
def calculate_width(epsilon):
    return int(math.ceil(math.e / epsilon))

def calculate_depth(delta):
    return int(math.ceil(math.log(1 / delta)))

# Optimized Count-Min Sketch Implementation
class CountMinSketch:
    def __init__(self, epsilon, delta):
        self.width = calculate_width(epsilon)
        self.depth = calculate_depth(delta)
        self.table = [[0] * self.width for _ in range(self.depth)]
        self.p = 2 ** 31 - 1  # A large prime number for hashing
        self.hash_functions = [self._generate_hash_function() for _ in range(self.depth)]

    def _generate_hash_function(self):
        # Generate pairwise independent hash functions
        a = random.randint(1, self.p - 1)
        b = random.randint(0, self.p - 1)

        def hash_function(x):
            # Use built-in hash function and ensure non-negative integers
            x_hash = abs(hash(x))
            return ((a * x_hash + b) % self.p) % self.width

        return hash_function

    def add(self, item_hash):
        for i, hash_function in enumerate(self.hash_functions):
            index = hash_function(item_hash)
            self.table[i][index] += 1

    def estimate(self, item_hash):
        return min(
            self.table[i][hash_function(item_hash)]
            for i, hash_function in enumerate(self.hash_functions)
        )

# Initialize Reddit instance (replace with your own credentials)
reddit = praw.Reddit(
    client_id="FwIMH9P1UPIH7CiLtS2KVg",
    client_secret="LBS7Sgc3SzR6dtnLMHMFI6rOCkEfeg",
    user_agent="CountMinAdvalgo by /u/shonshankar19"
)

# Data structures
trending_subreddits = {}
unique_words = set()
exact_counts = {}  # For validation purposes (optional)

# Use NLTK's stop words list
stop_words = set(stopwords.words('english'))

def get_user_input():
    root = tk.Tk()
    root.withdraw()

    num_submissions = simpledialog.askinteger(
        "Input", "Enter the number of submissions to process:",
        minvalue=1
    )

    time_frame_hours = simpledialog.askinteger(
        "Input", "Enter the time frame (in hours) for 'Most Active Subreddits':",
        minvalue=1
    )

    epsilon = simpledialog.askfloat(
        "Input", "Enter the desired error bound ε (e.g., 0.01 for 1% error):",
        minvalue=0.0001, maxvalue=1.0
    )

    delta = simpledialog.askfloat(
        "Input", "Enter the desired confidence level δ (e.g., 0.01 for 99% confidence):",
        minvalue=0.0001, maxvalue=1.0
    )

    root.destroy()
    return num_submissions, time_frame_hours, epsilon, delta

def process_submission(submission, current_time, cms_subreddit_activity, cms_content_keywords):
    try:
        subreddit_name = submission.subreddit.display_name
        subreddit_hash = hash(subreddit_name)

        title_words = [
            word.lower() for word in submission.title.split()
            if word.lower() not in stop_words and len(word) > 2
        ]

        cms_subreddit_activity.add(subreddit_hash)
        for word in title_words:
            word_hash = hash(word)
            cms_content_keywords.add(word_hash)
            unique_words.add(word)

        if subreddit_name not in trending_subreddits:
            trending_subreddits[subreddit_name] = []
        trending_subreddits[subreddit_name].append(current_time)

        # Update exact counts for validation (optional)
        exact_counts[subreddit_name] = exact_counts.get(subreddit_name, 0) + 1

    except Exception as e:
        print(f"Error processing submission: {e}")

def show_visualizations(time_frame_hours, cms_subreddit_activity, cms_content_keywords):
    try:
        current_time = time.time()
        filtered_activity = {}

        # Filter and count subreddit activity within the specified time frame
        for subreddit, timestamps in trending_subreddits.items():
            recent_posts = sum(
                1 for t in timestamps if current_time - t <= time_frame_hours * 3600
            )
            if recent_posts > 0:
                filtered_activity[subreddit] = recent_posts

        if not filtered_activity:
            print("No activity data to visualize")
            return

        # Sort subreddits by estimated activity
        sorted_subreddits = sorted(
            filtered_activity.keys(),
            key=lambda x: cms_subreddit_activity.estimate(hash(x)),
            reverse=True
        )[:10]

        # Prepare data for plotting
        counts = [cms_subreddit_activity.estimate(hash(s)) for s in sorted_subreddits]

        # Create the visualization
        plt.figure(figsize=(15, 6))

        # Subreddit activity subplot
        plt.subplot(1, 2, 1)
        plt.bar(range(len(sorted_subreddits)), counts)
        plt.xticks(
            range(len(sorted_subreddits)), sorted_subreddits,
            rotation=45, ha='right'
        )
        plt.title(f"Most Active Subreddits (Last {time_frame_hours} Hours)")
        plt.xlabel("Subreddits")
        plt.ylabel("Estimated Posts")

        # Word cloud subplot
        plt.subplot(1, 2, 2)
        if unique_words:
            word_frequencies = {
                word: cms_content_keywords.estimate(hash(word)) for word in unique_words
            }
            wordcloud = WordCloud(
                width=800, height=400, background_color='white'
            ).generate_from_frequencies(word_frequencies)
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis('off')
            plt.title("Trending Keywords")

        plt.tight_layout()
        plt.show()

    except Exception as e:
        print(f"Error in visualization: {e}")

def validate_cms(cms_subreddit_activity):
    print("\nValidation of CMS estimates against exact counts:")
    for subreddit in exact_counts.keys():
        exact = exact_counts[subreddit]
        estimated = cms_subreddit_activity.estimate(hash(subreddit))
        error = abs(estimated - exact)
        print(f"Subreddit: {subreddit}, Exact: {exact}, Estimated: {estimated}, Error: {error}")

def format_size(bytes_size):
    # Helper function to format bytes into KB, MB, etc.
    for unit in ['Bytes', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} PB"

def main():
    try:
        # Get user inputs
        num_submissions, time_frame_hours, epsilon, delta = get_user_input()
        if not num_submissions or not time_frame_hours or not epsilon or not delta:
            print("Input cancelled")
            return

        # Initialize CMS instances with calculated width and depth
        cms_subreddit_activity = CountMinSketch(epsilon, delta)
        cms_content_keywords = CountMinSketch(epsilon, delta)

        # Create progress window
        progress_window = tk.Tk()
        progress_window.title("Processing Reddit Submissions")
        progress_window.geometry("400x100")

        # Progress bar
        progress_bar = ttk.Progressbar(
            progress_window,
            orient="horizontal",
            length=300,
            mode="determinate",
            maximum=num_submissions
        )
        progress_bar.pack(pady=10)

        # Progress label
        progress_label = tk.Label(progress_window, text="Starting...")
        progress_label.pack()

        # Variables to track progress and exceptions
        count = {'value': 0}  # Use a mutable type like dict
        processing_exception = []

        def process_data():
            try:
                for submission in reddit.subreddit("all").stream.submissions(skip_existing=True):
                    current_time = time.time()
                    process_submission(submission, current_time, cms_subreddit_activity, cms_content_keywords)
                    count['value'] += 1

                    if count['value'] >= num_submissions:
                        break

            except Exception as e:
                print(f"Error during processing: {e}")
                processing_exception.append(e)

        # Function to update GUI
        def update_gui():
            progress_bar["value"] = count['value']
            progress_label.config(
                text=f"Processed {count['value']}/{num_submissions} submissions"
            )
            progress_window.update_idletasks()
            if count['value'] >= num_submissions or processing_exception:
                progress_window.destroy()
            else:
                progress_window.after(100, update_gui)  # Schedule next update

        # Start processing thread
        processing_thread = threading.Thread(target=process_data)
        processing_thread.start()

        # Start GUI updates
        update_gui()

        # Start progress window mainloop
        progress_window.mainloop()

        # Wait for the processing thread to finish
        processing_thread.join()

        # Check if any exceptions occurred
        if processing_exception:
            print("An error occurred during processing. Exiting.")
            return

        print("Data collection complete.")
        print("Generating visualizations...")
        show_visualizations(time_frame_hours, cms_subreddit_activity, cms_content_keywords)

        # Optional: Validate CMS accuracy
        validate_cms(cms_subreddit_activity)

        # Calculate and display memory usage
        cms_activity_size = asizeof.asizeof(cms_subreddit_activity)
        cms_keywords_size = asizeof.asizeof(cms_content_keywords)
        total_cms_size = cms_activity_size + cms_keywords_size

        print("\nMemory Usage:")
        print(f"CMS Subreddit Activity Size: {format_size(cms_activity_size)}")
        print(f"CMS Content Keywords Size: {format_size(cms_keywords_size)}")
        print(f"Total CMS Size: {format_size(total_cms_size)}")

    except Exception as e:
        print(f"Main error: {e}")

if __name__ == "__main__":
    main()
