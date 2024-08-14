import requests
from bs4 import BeautifulSoup
import csv
import time
import random
import io
import re

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
]

def get_random_user_agent():
    return random.choice(USER_AGENTS)

def scrape_ebay_page(url, max_retries=5, delay=10):
    for attempt in range(max_retries):
        try:
            headers = {
                "User-Agent": get_random_user_agent(),
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": "https://www.ebay.com/",
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            items = parse_ebay_page(soup)
            
            if items:
                return items
            else:
                print(f"Attempt {attempt + 1}: No items found. Retrying...")
        
        except requests.RequestException as e:
            print(f"Attempt {attempt + 1} failed: {e}")
        
        if attempt < max_retries - 1:
            wait_time = delay * (attempt + 1) + random.uniform(1, 5)
            print(f"Waiting for {wait_time:.2f} seconds before retrying...")
            time.sleep(wait_time)
    
    print("Max retries reached. Unable to scrape data.")
    return []

def parse_ebay_page(soup):
    items = []
    listings = soup.select('.s-item__wrapper')
    
    if not listings:
        print("No listings found. The page structure might have changed.")
        return items

    for listing in listings:
        item = {}
        
        title_elem = listing.select_one('.s-item__title')
        item['title'] = title_elem.text.strip() if title_elem else 'N/A'
        
        price_elem = listing.select_one('.s-item__price')
        item['price'] = price_elem.text.strip() if price_elem else 'N/A'
        
        condition_elem = listing.select_one('.SECONDARY_INFO')
        item['condition'] = condition_elem.text.strip() if condition_elem else 'N/A'
        
        shipping_elem = listing.select_one('.s-item__shipping, .s-item__freeXDays')
        item['shipping'] = shipping_elem.text.strip() if shipping_elem else 'N/A'
        
        location_elem = listing.select_one('.s-item__location')
        item['location'] = location_elem.text.strip() if location_elem else 'N/A'
        
        seller_rating_elem = listing.select_one('.x-star-rating')
        item['seller_rating'] = seller_rating_elem.text.strip() if seller_rating_elem else 'N/A'
        
        bids_elem = listing.select_one('.s-item__bids')
        item['bids'] = bids_elem.text.strip() if bids_elem else 'N/A'
        
        link_elem = listing.select_one('.s-item__link')
        item['link'] = link_elem['href'] if link_elem and 'href' in link_elem.attrs else 'N/A'

        # Extract image URL
        img_elem = listing.select_one('.s-item__image-img')
        item['image_url'] = img_elem['src'] if img_elem and 'src' in img_elem.attrs else 'N/A'

        item['item_number'] = 'N/A'
        if item['link'] != 'N/A':
            item_number_match = re.search(r'/itm/(\d+)', item['link'])
            if item_number_match:
                item['item_number'] = item_number_match.group(1)

        if item['title'] != "Shop on eBay" and item['title'] != 'N/A':
            items.append(item)
    
    return items

def scrape_ebay(search_term, num_pages=1, progress_callback=None):
    all_items = []
    for page in range(1, num_pages + 1):
        if progress_callback:
            progress_callback(page, num_pages)
        url = f"https://www.ebay.com/sch/i.html?_nkw={search_term.replace(' ', '+')}&_sacat=0&_pgn={page}"
        items = scrape_ebay_page(url)
        all_items.extend(items)
        if not items:
            break  # Stop if no items found on a page
        time.sleep(random.uniform(2, 5))  # Add a delay between page requests
    return all_items

def save_to_csv(items):
    if not items:
        return None
    
    output = io.StringIO()
    fieldnames = ['title', 'price', 'condition', 'shipping', 'location', 'seller_rating', 'bids', 'item_number', 'link', 'image_url']
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(items)
    return output.getvalue()

def main(search_term, num_pages=1, progress_callback=None):
    items = scrape_ebay(search_term, num_pages, progress_callback)
    csv_data = save_to_csv(items) if items else None
    return csv_data, items

if __name__ == "__main__":
    search_term = input("Enter your search term: ")
    num_pages = int(input("Enter the number of pages to scrape: "))
    csv_data, items = main(search_term, num_pages)
    if csv_data:
        filename = f"ebay_results_{search_term.replace(' ', '_')}.csv"
        with open(filename, 'w', newline='', encoding='utf-8') as file:
            file.write(csv_data)
        print(f"Data successfully saved to {filename}")
    else:
        print("No items were scraped. Please check the search term and try again.")
