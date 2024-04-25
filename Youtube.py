import streamlit as st
import pandas as pd
from googleapiclient.discovery import build

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
        video_response = youtube.videos().list(
            part='snippet,contentDetails,statistics',
            id=video_id
        ).execute()

        if not video_response.get('items'):
            continue

        video_snippet = video_response['items'][0]['snippet']
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        video_comments = video_response['items'][0]['statistics'].get('commentCount', 0)
        video_likes = video_response['items'][0]['statistics'].get('likeCount', 0)
        video_dislikes = video_response['items'][0]['statistics'].get('dislikeCount', 0)
        video_description = video_snippet.get('description', 'N/A')
        video_published_timestamp = video_snippet.get('publishedAt', 'N/A')

        data.append({
            'Video Title': video_title,
            'Video ID': video_id,
            'Video URL': video_url,
            'Comments': video_comments,
            'Likes': video_likes,
            'Dislikes': video_dislikes,
            'Description': video_description,
            'Keyword': keyword,
            'Published Timestamp': video_published_timestamp
        })

    return pd.DataFrame(data)

# Streamlit App
def main():
    st.title("YouTube Video Search App")

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

if __name__ == "__main__":
    main()
