import time
import random
import pandas as pd
from playwright.sync_api import sync_playwright

def run_scraper():
    TARGET_URL = "https://www.airbnb.com/s/Almaty--Kazakhstan/homes"
    CARD_SELECTOR = '[data-testid="card-container"]'
    NEXT_BUTTON_SELECTOR = 'a[aria-label="Next"]'

    all_data = []
    target_count = 108 

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=["--start-maximized"]) 
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080}, 
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        page.goto(TARGET_URL, timeout=90000) 
        time.sleep(5) 

        page_number = 1
        
        while len(all_data) < target_count:
            print(f"page # {page_number} ---")
            
            for i in range(4): 
                page.mouse.wheel(0, 2000)
                time.sleep(1)
            page.mouse.wheel(0, -2000)
            time.sleep(1)

            cards = page.query_selector_all(CARD_SELECTOR)
            print(f"Cards: {len(cards)}")

            if len(cards) == 0:
                print("Cards are not found")
                time.sleep(5)
                cards = page.query_selector_all(CARD_SELECTOR)
                if len(cards) == 0:
                    break

            for item in cards:
                try:
                    full_text = item.inner_text().split('\n')
                    title = full_text[0] if len(full_text) > 0 else "No Title"
                    price = "No Price"
                    for line in full_text:
                        if '$' in line or '₸' in line or '€' in line:
                            price = line
                            break
                    
                    link_el = item.query_selector('a')
                    link = f"https://www.airbnb.com{link_el.get_attribute('href')}" if link_el else ""

                    record = {'title': title, 'price': price, 'link': link}
                    
                    if not any(d['link'] == link for d in all_data):
                        all_data.append(record)
                except Exception:
                    continue
            
            print(f"Collected {len(all_data)} / {target_count}")

            if len(all_data) >= target_count:
                break

            next_btn = page.query_selector(NEXT_BUTTON_SELECTOR)
            if next_btn:
                next_btn.scroll_into_view_if_needed()
                time.sleep(1)
                
                try:
                    page.evaluate("arguments[0].click();", next_btn)
                except:
                    next_btn.click(force=True)
                
                page_number += 1
                time.sleep(random.uniform(6, 10)) 
                page.wait_for_load_state("domcontentloaded")
            else:
                print("Button is not found")
                break
        browser.close()


    df = pd.DataFrame(all_data)
    df = df.head(target_count) 
    df.to_csv('data/raw_data.csv', index=False)
    print(f"Data collected: {len(df)}")

if __name__ == "__main__":
    run_scraper()