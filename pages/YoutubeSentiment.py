import streamlit as st
import pandas as pd
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Initialize VADER sentiment analyzer
analyzer = SentimentIntensityAnalyzer()

# Function to search YouTube videos by keyword
def search_videos_by_keyword(api_key, keyword, max_results=10):
    youtube = build('youtube', 'v3', developerKey=api_key)
    response = youtube.search().list(
        q=keyword,
        part='id,snippet',
        type='video',
        maxResults=max_results
    ).execute()

    data = []

    for item in response.get('items', []):
        video_id = item['id']['videoId']
        video_title = item['snippet']['title']
        
        comments_disabled = False
        video_comments = ''
        comment_sentiment = {'compound': 0.0}  # Default value if comments are disabled

        try:
            # Fetch comments for the video
            comment_response = youtube.commentThreads().list(
                part='snippet',
                videoId=video_id,
                maxResults=10
            ).execute()
            
            comments = [comment['snippet']['topLevelComment']['snippet']['textDisplay'] 
                        for comment in comment_response.get('items', [])]
            
            video_comments = ' '.join(comments)
            
            # Analyze sentiment of comments using VADER
            comment_sentiment = analyze_sentiment(video_comments)
            
        except HttpError as e:
            comments_disabled = True

        video_response = youtube.videos().list(
            part='snippet,contentDetails,statistics',
            id=video_id
        ).execute()

        if not video_response.get('items'):
            continue

        video_snippet = video_response['items'][0]['snippet']
        video_description = video_snippet.get('description', 'N/A')
        video_sentiment = analyze_sentiment(video_description)
        video_url = f"https://www.youtube.com/watch?v={video_id}"

        data.append({
            'Video Title': video_title,
            'Video ID': video_id,
            'Video URL': video_url,
            'Description': video_description,
            'Sentiment': video_sentiment,
            'Comment Sentiment': comment_sentiment['compound'],
            'Comments Disabled': comments_disabled,
            'Comments': video_comments
        })

    return pd.DataFrame(data)

# Sentiment analysis function using VADER
def analyze_sentiment(text):
    sentiment = analyzer.polarity_scores(text)
    return sentiment

# Streamlit App
def main():
    st.title("YouTube Video Search App with Sentiment Score")

    # API key input
    api_key = st.text_input("Enter your YouTube API Key, My Key: AIzaSyCu8WrnQze2Prns70SpFSpXAY9Dr_FVmyc", type="password")

    # Keyword input
    keyword_list = st.text_area("Enter comma-separated keywords", height=100)
    keyword_list = [keyword.strip() for keyword in keyword_list.split(',')]

    if st.button("Search"):
        if api_key:
            final_df = pd.DataFrame()

            for keyword in keyword_list:
                keyword_df = search_videos_by_keyword(api_key, keyword)
                final_df = pd.concat([final_df, keyword_df], ignore_index=True)

            st.write(final_df)

            # Filter videos with high positive sentiment scores
            positive_scores = final_df[final_df['Comment Sentiment'] > 0]

            # Calculate percentage of positive sentiment scores
            total_videos = len(final_df)
            total_positive_scores = len(positive_scores)
            
            if total_videos > 0:
                percentage_positive_scores = (total_positive_scores / total_videos) * 100
            else:
                percentage_positive_scores = 0

            st.subheader("Videos with High Positive Comment Sentiment Scores")
            st.write(positive_scores)
            st.write(f"Percentage of videos with positive sentiment scores: {percentage_positive_scores:.2f}%")

if __name__ == "__main__":
    main()
