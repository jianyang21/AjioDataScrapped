from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import csv
from datetime import datetime

# Setup Selenium
driver = webdriver.Chrome()
base_url = "https://www.ajio.com/men-shirts/c/830216001"

products = []
page = 1

def clean_price(price_str):
    if not price_str:
        return 0.0
    return float(price_str.replace("₹", "").replace("Rs", "").replace(",", "").strip())

def normalize_description(desc):
    return ' '.join(desc.split()).strip()

def compute_original_from_discount(current, discount_str):
    try:
        discount = int(discount_str.replace("%", "").strip())
        if discount > 0:
            return round(current / (1 - discount / 100.0), 2)
    except:
        pass
    return current

while len(products) < 50:
    print(f"Scraping page {page}...")
    driver.get(f"{base_url}?page={page}")
    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    items = soup.find_all("div", class_="item rilrtl-products-list__item item")

    if not items:
        print("No more products found.")
        break

    for item in items:
        try:
            # Product Name
            name_tag = item.find("div", class_="nameCls")
            name = name_tag.text.strip() if name_tag else ""

            # Brand
            brand_tag = item.find("div", class_="brand")
            brand = brand_tag.text.strip().lower() if brand_tag else ""

            # Current Price
            current_price_tag = item.find("span", class_="price")
            current_price_text = current_price_tag.text.strip() if current_price_tag else ""
            current_price_val = clean_price(current_price_text)

            # Original Price
            orig_price_tag = item.find("span", class_="orginal-price")
            original_price_text = orig_price_tag.text.strip() if orig_price_tag else current_price_text
            original_price_val = clean_price(original_price_text)

            # Calculate discount percentage
            if original_price_val > current_price_val:
                discount_val = round(((original_price_val - current_price_val) / original_price_val) * 100)
            else:
                discount_val = 0
                original_price_val = compute_original_from_discount(current_price_val, str(discount_val) + "%")
            discount_percentage = f"{discount_val}%"

            # Description
            description_tag = item.find("div", class_="product-desc-rating")
            description = description_tag.text.strip().split("Rating")[0].strip() if description_tag else ""
            description = normalize_description(description)

            # Rating and Reviews
            rating_tag = item.find("div", class_="product-ratings")
            average_rating = "0"
            review_count = "0"
            if rating_tag:
                rating_info = rating_tag.text.strip().split("·")
                if len(rating_info) >= 1:
                    average_rating = rating_info[0].strip()
                if len(rating_info) == 2:
                    review_count = rating_info[1].strip().split()[0]

            # Numeric conversions for urgency_label
            try:
                avg_rating_val = float(average_rating)
            except:
                avg_rating_val = 0.0

            try:
                review_count_val = int(review_count.replace(",", ""))
            except:
                review_count_val = 0

            # Determine urgency_label
            if discount_val > 25:
                urgency_label = 2  # High
            elif discount_val > 10 and discount_val < 25:
                urgency_label = 1  # Medium
            else:
                urgency_label = 0  # Low

            # Product URL
            link_tag = item.find("a")
            product_url = "https://www.ajio.com" + link_tag["href"] if link_tag and "href" in link_tag.attrs else ""

            # Image URL
            img_tag = item.find("img")
            image_url = (
                img_tag.get("src") or
                img_tag.get("data-src") or
                img_tag.get("data-lazy-src") or
                ""
            ) if img_tag else ""

            # Append product
            products.append({
                "product_name": name,
                "brand": brand,
                "current_price": current_price_val,
                "original_price": original_price_val,
                "discount_percentage": discount_percentage,
                "description": description,
                "average_rating": avg_rating_val,
                "review_count": review_count_val,
                "product_url": product_url,
                "image_url": image_url,
                "scraped_timestamp": datetime.utcnow().isoformat(),
                "urgency_label": urgency_label
            })

            if len(products) >= 50:
                break
        except Exception as e:
            print(f"Error scraping product: {e}")
            continue

    page += 1

driver.quit()

# Save to CSV
csv_file = "the_new_ajio_mens_shirts.csv"
with open(csv_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=products[0].keys())
    writer.writeheader()
    writer.writerows(products)

print(f"\n✅ Scraping completed. Saved {len(products)} products to '{csv_file}'.")


