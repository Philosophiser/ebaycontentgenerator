import streamlit as st
import pandas as pd
import plotly.express as px
from ebay_scraper import main as scrape_ebay

# Function to create a histogram
def create_histogram(df, column):
    fig = px.histogram(df, x=column, title=f'Histogram of {column}')
    return fig

# Function to create a box plot
def create_box_plot(df, column):
    fig = px.box(df, y=column, title=f'Box Plot of {column}')
    return fig

st.title('eBay Scraper App')

search_term = st.text_input('Enter your search term:')

if st.button('Scrape eBay'):
    if search_term:
        try:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i in range(100):
                status_text.text(f"Scraping in progress... {i+1}%")
                progress_bar.progress(i + 1)
                if i == 0:
                    csv_data, items = scrape_ebay(search_term)
                    break
            
            if items:
                st.success(f"Successfully scraped {len(items)} items!")
                
                # Display the data as a table
                try:
                    df = pd.DataFrame(items)
                    # Reorder columns for better presentation
                    columns_order = ['title', 'price', 'condition', 'shipping', 'location', 'seller_rating', 'bids', 'time_left', 'post_date', 'item_number', 'link']
                    df = df[columns_order]
                    st.write(df)

                    # Clean and convert price data
                    df['price_numeric'] = df['price'].str.replace('$', '').str.replace(',', '').astype(float)

                    # Create and display histogram
                    st.subheader("Price Distribution Histogram")
                    hist_fig = create_histogram(df, 'price_numeric')
                    st.plotly_chart(hist_fig)

                    # Create and display box plot
                    st.subheader("Price Distribution Box Plot")
                    box_fig = create_box_plot(df, 'price_numeric')
                    st.plotly_chart(box_fig)

                except Exception as e:
                    st.error(f"Error processing data: {e}")
                    st.write("Raw data:", items)
                
                # Provide a download button for the CSV
                if csv_data:
                    st.download_button(
                        label="Download data as CSV",
                        data=csv_data,
                        file_name=f"ebay_results_{search_term}.csv",
                        mime="text/csv"
                    )
                else:
                    st.warning("CSV data is not available.")
            else:
                st.warning("No items were scraped. The search may have returned no results or eBay might be blocking our requests.")
        except Exception as e:
            st.error(f"An error occurred while scraping: {str(e)}")
    else:
        st.warning("Please enter a search term.")

