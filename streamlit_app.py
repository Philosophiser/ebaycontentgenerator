import streamlit as st
import pandas as pd
from ebay_scraper import main as scrape_ebay

st.title('eBay Scraper App')

search_term = st.text_input('Enter your search term:')

if st.button('Scrape eBay'):
    if search_term:
        try:
            with st.spinner(f"Scraping eBay for '{search_term}'..."):
                csv_data, items = scrape_ebay(search_term)
            
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
                st.warning("No items were scraped. The search may have returned no results.")
        except Exception as e:
            st.error(f"An error occurred while scraping: {str(e)}")
    else:
        st.warning("Please enter a search term.")

st.info("If you encounter any issues, please check your internet connection and try again. If the problem persists, the eBay website structure may have changed, requiring an update to the scraper.")
