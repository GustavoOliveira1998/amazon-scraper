import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
from retrying import retry  # Importing retry function from retrying library
import time

# retry decorator is used to retry the function in case of failure
@retry(stop_max_attempt_number=3, wait_fixed=2000)  # Try at most 3 times, waiting 2 seconds between each attempt
def fetch_url(url, headers):
    # Make a GET request to the URL with the provided headers
    response = requests.get(url, headers=headers)
    # Check if the response contains an error status code
    response.raise_for_status()
    return response

# Function to scrape data from Amazon
def scrape_amazon(keyword):
    # URL of Amazon search page with the keyword
    url = f"https://www.amazon.com.br/s?k={quote(keyword)}"
    # HTTP headers to mimic a browser and avoid blocks
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    print("Trying to access Amazon URL:", url)

    try:
        # Try to access the Amazon URL using the fetch_url function decorated with retry
        response = fetch_url(url, headers)
        print("Response status code:", response.status_code)

        # Parse the HTML content of the web page using BeautifulSoup
        soup = BeautifulSoup(response.content, "html.parser")
        # Find all product elements on the page
        products = soup.find_all("div", class_="s-result-item")

        scraped_data = []

        # Iterate over product elements and extract relevant data
        for product in products:
            title_element = product.find("h2")
            rating_element = product.find(class_="a-icon-star-small")
            review_count_element = product.find(class_="a-size-small.a-link-normal")
            image_element = product.find(class_="s-image")

            title = title_element.text.strip() if title_element else "N/A"
            rating_text = rating_element.text.strip() if rating_element else "0"
            rating = float(rating_text.split()[0].replace(",", ".")) if rating_text else 0
            review_count = int(review_count_element.text.replace(",", "")) if review_count_element else 0
            image = image_element["src"] if image_element else "N/A"

            # Add product data to the list of scraped data
            scraped_data.append({
                "title": title,
                "rating": rating,
                "review_count": review_count,
                "image": image
            })

        return scraped_data

    except Exception as e:
        # If an exception occurs during the scraping process, print the error message
        print("Failed to scrape Amazon data:", e)
        return None

# Example of usage
keyword = input("Enter a keyword: ")
data = scrape_amazon(keyword)
if data:
    # Print the scraped data for each product
    for product in data:
        print(f"Title: {product['title']}")
        print(f"Rating: {product['rating']}")
        print(f"Review Count: {product['review_count']}")
        print(f"Image URL: {product['image']}")
        print("------------------------")
