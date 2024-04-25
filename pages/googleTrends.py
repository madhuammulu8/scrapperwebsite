import pandas as pd
import streamlit as st
from pytrends.request import TrendReq
import matplotlib.pyplot as plt

# Initialize pytrend object
pytrend = TrendReq()

def get_interest_over_time(keywords):
    total_df = pd.DataFrame()

    for a in range(0, len(keywords), 5):
        keyword = keywords[a:a+5]
        pytrend.build_payload(kw_list=keyword, timeframe='2023-04-23 2024-04-23', geo='US')
        
        try:
            interest_over_time_df = pytrend.interest_over_time().reset_index()

            if total_df.empty:
                total_df = interest_over_time_df
            else:
                total_df = pd.merge(total_df, interest_over_time_df, on='date', how='left')

        except KeyError as e:
            st.warning(f"KeyError: {e}")
            st.warning(f"Error occurred while processing keywords: {keyword}")

    return total_df

def get_related_queries(keyword):
    pytrend.build_payload(kw_list=[keyword], timeframe='today 5-y', geo='US')
    related_queries = pytrend.related_queries()[keyword]['rising']
    return related_queries

def get_related_topics(keyword):
    pytrend.build_payload(kw_list=[keyword], timeframe='today 5-y', geo='US')
    related_topics = pytrend.related_topics()[keyword]['rising']
    return related_topics

# Streamlit app
def main():
    st.title("Google Trends Analysis")

    # Get user input for keywords
    keywords_input = st.text_area("Enter keywords separated by commas (,)", value='', height=100)
    
    if st.button("Run Analysis"):
        keywords = [kw.strip() for kw in keywords_input.split(',')]
        
        if keywords:
            df = get_interest_over_time(keywords)
            
            # Display the DataFrame
            st.write(df)

            # Plotting
            for keyword in keywords:
                plt.figure(figsize=(12, 6))
                plt.plot(df['date'], df[keyword], label=keyword)
                plt.title(f"Interest Over Time for {keyword}")
                plt.xlabel("Date")
                plt.ylabel("Interest")
                plt.legend()
                st.pyplot(plt)

            # Display related rising queries and topics below the table
            st.subheader("Related Rising Queries")
            for keyword in keywords:
                related_queries = get_related_queries(keyword)
                related_queries_list = ', '.join(related_queries['query'].tolist())
                st.write(f"{keyword}: {related_queries_list}")


            st.subheader("Related Rising Topics")
            for keyword in keywords:
                related_topics = get_related_topics(keyword)
                related_topics_list = ', '.join(related_topics['topic_title'].tolist())
                st.write(f"{keyword}: {related_topics_list}")

if __name__ == "__main__":
    main()
