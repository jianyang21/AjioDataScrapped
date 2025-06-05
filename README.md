
# AJIO Men's Shirts Scraper

This project uses **Selenium** and **BeautifulSoup** to scrape men's shirt listings from [AJIO.com](https://www.ajio.com), collecting product details like brand, price, rating, discount, and more. The scraped data is saved into a CSV file for further analysis.

---

##  Files

- `AjioScrapped.py`: Main script that performs web scraping.
- `the_new_ajio_mens_shirts.csv`: Output CSV file containing scraped product information.

---

##  Pagination Strategy

The script navigates through paginated results by updating the `page` parameter in the URL dynamically:

```python
driver.get(f"{base_url}?page={page}")


## ❗ Challenges Faced

### 1. Antiscraping Measures
AJIO's product listings are dynamically loaded using JavaScript, which means traditional HTML parsers like `requests + BeautifulSoup` are insufficient.

**Solution**:  
Used `Selenium` to render the page completely before parsing with BeautifulSoup.

---

### 2. Dynamic Image and Link Sources
Product images are sometimes stored in different attributes like `src`, `data-src`, or `data-lazy-src`, depending on how they are loaded.

**Solution**:  
Tried all possible attributes in priority order to extract a valid image URL.

```python
img_tag.get("src") or img_tag.get("data-src") or img_tag.get("data-lazy-src")
