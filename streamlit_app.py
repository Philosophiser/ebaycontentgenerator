import streamlit as st
import pandas as pd
import plotly.express as px
from ebay_scraper import main as scrape_ebay

def create_histogram(df, column):
    fig = px.histogram(df, x=column, title=f'Histogram of {column}')
    return fig

def create_box_plot(df, column):
    fig = px.box(df, y=column, title=f'Box Plot of {column}')
    return fig

st.title('eBay Scraper App')

search_term = st.text_input('Enter your search term:')
num_pages = st.number_input('Enter the number of pages to scrape:', min_value=1, max_value=10, value=1)

if st.button('Scrape eBay'):
    if search_term:
        try:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i in range(100):
                status_text.text(f"Scraping in progress... {i+1}%")
                progress_bar.progress(i + 1)
                if i == 0:
                    csv_data, items = scrape_ebay(search_term, int(num_pages))
                    break
            
            if items:
                st.success(f"Successfully scraped {len(items)} items from {num_pages} page(s)!")
                
                try:
                    df = pd.DataFrame(items)
                    columns_order = ['title', 'price', 'condition', 'shipping', 'location', 'seller_rating', 'bids', 'item_number', 'link']
                    df = df[columns_order]
                    st.write(df)

                    df['price_numeric'] = df['price'].str.replace('$', '').str.replace(',', '').astype(float)

                    st.subheader("Price Distribution Histogram")
                    hist_fig = create_histogram(df, 'price_numeric')
                    st.plotly_chart(hist_fig)

                    st.subheader("Price Distribution Box Plot")
                    box_fig = create_box_plot(df, 'price_numeric')
                    st.plotly_chart(box_fig)

                except Exception as e:
                    st.error(f"Error processing data: {e}")
                    st.write("Raw data:", items)
                
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
