import streamlit as st
import pandas as pd
from ebay_scraper import main as scrape_ebay

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
                except Exception as e:
                    st.error(f"Error creating DataFrame: {e}")
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

st.info("If you encounter any issues, please try the following:")
st.info("1. Check your internet connection")
st.info("2. Try a different search term")
st.info("3. Wait a few minutes and try again")
st.info("If problems persist, the eBay website structure may have changed, requiring an update to the scraper.")
