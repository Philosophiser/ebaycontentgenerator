import streamlit as st
import pandas as pd
from ebay_scraper import main as scrape_ebay

st.title('eBay Scraper App')

search_term = st.text_input('Enter your search term:')

if st.button('Scrape eBay'):
    if search_term:
        st.write(f"Scraping eBay for '{search_term}'...")
        csv_data, items = scrape_ebay(search_term)
        
        if csv_data:
            st.success(f"Successfully scraped {len(items)} items!")
            
            # Display the data as a table
            df = pd.read_csv(pd.compat.StringIO(csv_data))
            st.write(df)
            
            # Provide a download button for the CSV
            st.download_button(
                label="Download data as CSV",
                data=csv_data,
                file_name=f"ebay_results_{search_term}.csv",
                mime="text/csv"
            )
        else:
            st.error("No items were scraped. Please check your search term and try again.")
    else:
        st.warning("Please enter a search term.") 
