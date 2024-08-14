import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime
import time
import random
import io

def scrape_ebay(search_term, max_retries=3, delay=5):
    url = f"https://www.ebay.com/sch/i.html?_nkw={search_term.replace(' ', '+')}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.ebay.com/",
        "DNT": "1",
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                items = parse_ebay_page(soup)
                return items
            
        except requests.RequestException as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                wait_time = delay * (attempt + 1) + random.uniform(1, 5)
                print(f"Waiting for {wait_time:.2f} seconds before retrying...")
                time.sleep(wait_time)
            else:
                print("Max retries reached. Unable to scrape data.")
                return []

def parse_ebay_page(soup):
    items = []
    listings = soup.select('li.s-item')
    
    if not listings:
        print("No listings found. The page structure might have changed.")
        print("Page content:", soup.prettify()[:1000])
        return items

    for listing in listings:
        item = {}
        
        # Title
        title_elem = listing.select_one('.s-item__title')
        item['title'] = title_elem.text.strip() if title_elem else 'N/A'
        
        # Price
        price_elem = listing.select_one('.s-item__price')
        item['price'] = price_elem.text.strip() if price_elem else 'N/A'
        
        # Condition
        condition_elem = listing.select_one('.SECONDARY_INFO')
        item['condition'] = condition_elem.text.strip() if condition_elem else 'N/A'
        
        # Shipping
        shipping_elem = listing.select_one('.s-item__shipping, .s-item__freeXDays')
        item['shipping'] = shipping_elem.text.strip() if shipping_elem else 'N/A'
        
        # Location
        location_elem = listing.select_one('.s-item__location')
        item['location'] = location_elem.text.strip() if location_elem else 'N/A'
        
        # Seller Rating
        seller_rating_elem = listing.select_one('.x-star-rating')
        item['seller_rating'] = seller_rating_elem.text.strip() if seller_rating_elem else 'N/A'
        
        # Number of Bids (for auction items)
        bids_elem = listing.select_one('.s-item__bids')
        item['bids'] = bids_elem.text.strip() if bids_elem else 'N/A'
        
        # Time Left (for auction items)
        time_left_elem = listing.select_one('.s-item__time-left')
        item['time_left'] = time_left_elem.text.strip() if time_left_elem else 'N/A'
        
        # Link to the item
        link_elem = listing.select_one('.s-item__link')
        item['link'] = link_elem['href'] if link_elem else 'N/A'

        # Listing post date
        date_elem = listing.select_one('.s-item__listingDate')
        item['post_date'] = date_elem.text.strip() if date_elem else 'N/A'

        # eBay item number
        if item['link'] != 'N/A':
            item_number_match = re.search(r'/itm/(\d+)', item['link'])
            item['item_number'] = item_number_match.group(1) if item_number_match else 'N/A'
        else:
            item['item_number'] = 'N/A'

        if item['title'] != "Shop on eBay":
            items.append(item)
    
    print(f"Scraped {len(items)} items")
    return items

def save_to_csv(items):
    if not items:
        return None
    
    output = io.StringIO()
    fieldnames = ['title', 'price', 'condition', 'shipping', 'location', 'seller_rating', 'bids', 'time_left', 'post_date', 'item_number', 'link']
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(items)
    return output.getvalue()

def main(search_term):
    items = scrape_ebay(search_term)
    csv_data = save_to_csv(items) if items else None
    return csv_data, items

if __name__ == "__main__":
    # This block will only run if the script is executed directly (not imported)
    search_term = input("Enter your search term: ")
    csv_data, items = main(search_term)
    if csv_data:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ebay_results_{timestamp}.csv"
        with open(filename, 'w', newline='', encoding='utf-8') as file:
            file.write(csv_data)
        print(f"Data successfully saved to {filename}")
    else:
        print("No items were scraped. Please check the search term and try again.")

    # Add a delay to keep the console open in Replit
    time.sleep(10)
