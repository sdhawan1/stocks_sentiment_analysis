# Stocks Sentiment Analysis

This repo contains the code which tries to predict daily stock price changes using sentiment analysis.
So far, the web crawling and data aggregation using pandas has been fleshed out. Some more work is required on the machine learning and sentiment analysis portions.

### 1. Crawling Web Data
Takes advantage of a tool called "Wayback", which stores an archive of many pages on the internet. I used this to crawl old rss feeds from CNBC. I haven't yet crawled the contents of old articles, but the titles / metadata of the old feeds was crawled for use in the sentiment analysis.

To crawl the data, run: "crawl_data/crawl_archived_rss_feeds/retrieve_wayback_articles.py". 
This goes to all the saved RSS links and downloads the full webpage.

### 2. Organizing RSS files and stock data into Training Data Dataframe
Takes the crawled RSS html pages and extracts all the titles associated with a given stock. Then, it creates a dataset that concatenates all titles for a given day and a given stock into one data point (i.e. one row in the "trdata" dataframe).
Additionally, data on real stock movements from "nasdaq.com" is joined with the aggregated rss titles dataframe. 
All aggregations and joins are done in Pandas.

To create the training data, run: "training/create_trdata_pandas.py"

### 3. Sentiment Analysis
This hasn't been completely fleshed out yet. The current method uses preset dictionaries of negative and positive words, and counts how many of each show up in the titles.

To run the current sentiment analysis on the pandas training data, run: "training/test_sentiment.py"

This doesn't seem to be very accurate since often the titles contain very few of the preset negative and positive words.
A simple extension might be to extend the preset dictionaries with the words from the titles themselves (maybe only include those words that are more likely to be associated with positivity or negativity).

A more complex but potentially better performing extension would be to use deep learning for inference. This could learn more flexible correlations between title words and stock movement.
