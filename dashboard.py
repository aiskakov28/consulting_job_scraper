# dashboard.py
import streamlit as st
import pandas as pd
from datetime import datetime
import glob
import os

def load_data():
    try:
        list_of_files = glob.glob('business_internships_full_*.csv')
        if list_of_files:
            latest_file = max(list_of_files, key=os.path.getctime)
            df = pd.read_csv(latest_file).astype(str)
            df = df.replace('nan', '')
            df = df.replace('None', '')
            return df
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()


def create_dashboard():
    st.set_page_config(page_title="2025 Consulting Internships", layout="wide")
    st.title('2025 Consulting Internships (made by Abylay Iskakov)')

    # Add refresh button
    if st.button('🔄 Refresh Data'):
        st.rerun()

    df = load_data()

    if df.empty:
        st.warning("No data available. Please run the scraper first to collect job listings.")
        st.info("Run 'python main.py' to collect job listings.")
        return

    st.sidebar.header('Filters')

    try:
        # Add search box
        search_term = st.sidebar.text_input('🔍 Search Jobs', '').lower()

        # Filters
        companies = ['All'] + sorted(df['company'].unique().tolist())
        company_filter = st.sidebar.selectbox('Select Company', companies)

        locations = ['All'] + sorted(df['location'].unique().tolist())
        location_filter = st.sidebar.selectbox('Select Location', locations)

        categories = ['All'] + sorted(df['category'].unique().tolist())
        category_filter = st.sidebar.selectbox('Select Role Category', categories)

        filtered_df = df.copy()

        # Apply search filter
        if search_term:
            filtered_df = filtered_df[
                filtered_df['title'].str.lower().str.contains(search_term) |
                filtered_df['company'].str.lower().str.contains(search_term) |
                filtered_df['location'].str.lower().str.contains(search_term)
                ]

        # Apply dropdown filters
        if company_filter != 'All':
            filtered_df = filtered_df[filtered_df['company'] == company_filter]

        if location_filter != 'All':
            filtered_df = filtered_df[filtered_df['location'] == location_filter]

        if category_filter != 'All':
            filtered_df = filtered_df[filtered_df['category'] == category_filter]

        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric('Total Positions', len(filtered_df))
        with col2:
            st.metric('Companies', filtered_df['company'].nunique())
        with col3:
            st.metric('Locations', filtered_df['location'].nunique())
        with col4:
            st.metric('Categories', filtered_df['category'].nunique())

        # Display jobs
        st.subheader('💼 Available Positions')
        if filtered_df.empty:
            st.info("No positions found matching the selected filters.")
        else:
            filtered_df = filtered_df.sort_values('date_posted', ascending=False)
            for idx, row in filtered_df.iterrows():
                with st.expander(f"🏢 {row['title']} at {row['company']} ({row['category']})"):
                    with st.container():
                        if row['application_url'] and len(row['application_url'].strip()) > 0:
                            st.write(f"**Company:** [{row['company']}]({row['application_url']})")
                        else:
                            st.write(f"**Company:** {row['company']}")
                        st.write(f"**Location:** {row['location']}")
                        st.write(f"**Category:** {row['category']}")
                        st.write(f"**Posted:** {row['date_posted']}")

                        if row['application_url'] and len(row['application_url'].strip()) > 0:
                            # Using link_button instead of button for proper URL navigation
                            st.link_button('Apply Now', row['application_url'], type="primary")

    except Exception as e:
        st.error(f"Error processing data: {str(e)}")

if __name__ == "__main__":
    create_dashboard()