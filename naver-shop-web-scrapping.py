from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time

# Configure Selenium WebDriver
service = Service()
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(service=service, options=options)

url = "https://search.shopping.naver.com/ns/search?query=baby%20clothes"
driver.get(url)

# Simulate incremental scrolling and gather chunks of HTML
full_html = ""
scroll_pause_time = 2  # Adjust based on the page's loading speed
max_scrolls = 10  # Limit the number of scrolls
current_scroll = 0

while current_scroll < max_scrolls:
    # Append the current HTML chunk to full_html
    full_html += driver.page_source
    
    # Scroll down to the bottom of the page
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(scroll_pause_time)  # Pause to allow content to load
    
    # Wait for new content to load
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'compositeCardContainer_composite_card_container__jr8cb'))
        )
    except:
        print("Timed out waiting for elements to load. Continuing...")
    
    current_scroll += 1  # Increment the scroll counter

# Close the driver
driver.quit()

# Parse the combined HTML using BeautifulSoup
soup = BeautifulSoup(full_html, 'html.parser')

# Extract product data from the combined HTML
products = soup.find_all('li', class_='compositeCardContainer_composite_card_container__jr8cb')

# List to store product data
product_data = []

for product in products:
    # Product Title
    title_tag = product.find('strong', class_='basicProductCardInformation_title__Bc_Ng')
    title = title_tag.text.strip() if title_tag else "No Title"

    # Product Price
    price_tag = product.find('span', class_='priceTag_inner_price__TctbK')
    price = price_tag.text.strip() if price_tag else "No Price"

    # Discount Information
    discount_tag = product.find('span', class_='priceTag_discount__F_ZXz')
    discount = discount_tag.text.strip() if discount_tag else "No Discount"

    # Delivery Information
    delivery_tag = product.find('div', class_='productCardPrice_delivery_price__AiyD2')
    delivery = delivery_tag.text.strip() if delivery_tag else "Delivery Info Not Available"

    # Product Rating
    rating_tag = product.find('span', class_='productCardReview_star__7iHNO')
    rating = rating_tag.text.strip() if rating_tag else "No Rating"

    # Reviews Count
    reviews_tag = product.find('span', class_='productCardReview_text__A9N9N')
    reviews = reviews_tag.text.strip() if reviews_tag else "No Reviews"

    # Product Image URL
    image_tag = product.find('img', class_='productCardThumbnail_image__Li6iz')
    image_url = image_tag['src'] if image_tag else "No Image URL"

    # Store URL and Name
    store_tag = product.find('a', class_='basicProductCardInformation_mall_link__9TeDD')
    store_name = store_tag.text.strip() if store_tag else "No Store Name"
    store_url = store_tag['href'] if store_tag else "No Store URL"

    # Append product data to the list
    product_data.append({
        "Title": title,
        "Price": price,
        "Discount": discount,
        "Delivery": delivery,
        "Rating": rating,
        "Reviews": reviews,
        "Image URL": image_url,
        "Store Name": store_name,
        "Store URL": store_url
    })

# Save the data to a CSV file
df = pd.DataFrame(product_data)
csv_file = "products.csv"
df.to_csv(csv_file, index=False, encoding="utf-8-sig")

print(f"Data saved to {csv_file}")
