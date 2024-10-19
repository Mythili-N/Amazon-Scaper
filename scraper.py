import csv
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from bs4 import BeautifulSoup

# Function to format the Amazon search URL
def get_url(search_term):
    template = "https://www.amazon.com/s?k={}&crid=29WGROR3X4E4G&sprefix=smart+watch%2Caps%2C979&ref=nb_sb_noss_1"
    search_term = search_term.replace(" ", "+")  # Replace spaces with '+' for the search URL
    return template.format(search_term)

# Function to extract data from each product item
def extract_record(item):
    try:
        # Extract product description and URL
        atag = item.h2.a
        description = atag.text.strip()
        url = "https://www.amazon.com" + atag.get("href")
    except AttributeError:
        return None  # Return None if description or URL not found

    try:
        # Extract price
        price_parent = item.find("span", "a-price")
        price = price_parent.find("span", "a-offscreen").text
    except AttributeError:
        price = "Price not found"  # If price is not found

    try:
        # Extract rating and review count
        rating = item.i.text
        review_count = item.find("span", {"class": "a-size-base", "dir": "auto"}).text
    except AttributeError:
        rating = "No rating"
        review_count = "No reviews"

    # Return the extracted information as a list
    return [description, price, rating, review_count, url]

# Main function to scrape Amazon product search results
def main(search_term):
    # Set up Edge driver options
    options = Options()
    options.use_chromium = True  # Ensures the use of the Chromium-based Edge browser

    # Path to Edge WebDriver
    service = Service(r"path to web driver")
    driver = webdriver.Edge(service=service, options=options)

    records = []  # List to hold all extracted records
    url = get_url(search_term)

    for page in range(1, 2):  # Adjust range to scrape more pages
        driver.get(url + f"&page={page}")

        # Wait for the page to load completely
        driver.implicitly_wait(10)

        # Parse the page content
        soup = BeautifulSoup(driver.page_source, "html.parser")
        results = soup.find_all("div", {"data-component-type": "s-search-result"})

        # Extract data from each search result
        for item in results:
            record = extract_record(item)
            if record:  # Only append if record is valid
                records.append(record)

    driver.quit()  # Close the browser

    # Write extracted data to a CSV file
    with open("results.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Description", "Price", "Rating", "Review Count", "URL"])  # Write header row
        writer.writerows(records)  # Write product data

# Run the main function with a search term
if __name__ == "__main__":
    main("smart watch")
