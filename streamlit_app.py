import streamlit as st
import pandas as pd
import plotly.express as px
from ebay_scraper import main as scrape_ebay
import re

def clean_price(price_str):
    price_str = price_str.replace('$', '').replace(',', '')
    if ' to ' in price_str:
        low, high = map(float, price_str.split(' to '))
        return (low + high) / 2
    else:
        return float(price_str)

def create_histogram(df, column):
    fig = px.histogram(df, x=column, title=f'Histogram of {column}')
    return fig

def create_box_plot(df, column):
    fig = px.box(df, y=column, title=f'Box Plot of {column}')
    return fig

def is_valid_image_url(url):
    return url.startswith('http') and (url.endswith('.jpg') or url.endswith('.png') or url.endswith('.gif'))

st.title('eBay Scraper App')

search_term = st.text_input('Enter your search term:')
num_pages = st.number_input('Enter the number of pages to scrape:', min_value=1, max_value=10, value=1)

if st.button('Scrape eBay'):
    if search_term:
        try:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            def update_progress(current_page, total_pages):
                progress = int((current_page / total_pages) * 100)
                status_text.text(f"Scraping page {current_page} of {total_pages}...")
                progress_bar.progress(progress)
            
            csv_data, items = scrape_ebay(search_term, int(num_pages), update_progress)
            
            if items:
                st.success(f"Successfully scraped {len(items)} items from {num_pages} page(s)!")
                
                try:
                    df = pd.DataFrame(items)
                    columns_order = ['title', 'price', 'condition', 'shipping', 'location', 'seller_rating', 'bids', 'item_number', 'link', 'image_url']
                    df = df[columns_order]
                    
                    # Display items with clickable links and images
                    for index, row in df.iterrows():
                        col1, col2 = st.columns([1, 3])
                        with col1:
                            if is_valid_image_url(row['image_url']):
                                st.image(row['image_url'], use_column_width=True)
                            else:
                                st.write("No image available")
                        with col2:
                            st.write(f"**{row['title']}**")
                            st.write(f"Price: {row['price']}")
                            st.write(f"Condition: {row['condition']}")
                            st.write(f"Shipping: {row['shipping']}")
                            st.write(f"[View on eBay]({row['link']})")
                        st.write("---")

                    # Clean and convert price data
                    df['price_numeric'] = df['price'].apply(clean_price)

                    # Create visualizations
                    try:
                        st.subheader("Price Distribution Histogram")
                        hist_fig = create_histogram(df, 'price_numeric')
                        st.plotly_chart(hist_fig)

                        st.subheader("Price Distribution Box Plot")
                        box_fig = create_box_plot(df, 'price_numeric')
                        st.plotly_chart(box_fig)
                    except Exception as viz_error:
                        st.warning(f"Error creating visualizations: {viz_error}")
                        st.write("Visualization skipped. You can still download the CSV data.")

                except Exception as e:
                    st.error(f"Error processing data: {e}")
                    st.write("Raw data:", items[:5])  # Show only first 5 items to avoid clutter
                
                if csv_data:
                    st.download_button(
                        label="Download data as CSV",
                        data=csv_data,
                        file_name=f"ebay_results_{search_term.replace(' ', '_')}.csv",
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

st.info("If you encounter any issues, please try the following:")
st.info("1. Check your internet connection")
st.info("2. Try a different search term")
st.info("3. Reduce the number of pages to scrape")
st.info("4. Wait a few minutes and try again")
st.info("If problems persist, the eBay website structure may have changed, requiring an update to the scraper.")
