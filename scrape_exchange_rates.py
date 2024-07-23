import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import date, datetime
import re

def scrape_maybank_forex_rates():
    """Scrapes Maybank's forex rates, saves to CSV/PNG if updated."""

    url = "https://www.maybank2u.com.my/maybank2u/malaysia/en/personal/rates/forex_rates.page"

    try:
        response = requests.get(url, verify=False)
        response.raise_for_status() 
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return

    soup = BeautifulSoup(response.content, "html.parser")

    # Extract and validate the date (more robust handling)
    date_element = soup.find("p", class_="text-small")
    if not date_element:
        print("Date element not found on the page.")
        return

    date_text = date_element.get_text()
    date_pattern = r"\d{1,2}\s+[a-z]{3}\s+\d{4}\s+\d{2}:\d{2}:\d{2}"
    date_match = re.search(date_pattern, date_text)

    if not date_match:
        print("Date not found or invalid format.")
        return

    forex_date = datetime.strptime(date_match.group(), '%d %b %Y %H:%M:%S')

    # Check if rates are up-to-date
    if forex_date.date() != date.today():
        print("Rates not yet updated.")
        return

    # Extract table data (more efficient and flexible)
    table = soup.find("table", class_="table")
    rows = table.find_all("tr")[1:]  
    data = [[col.get_text(strip=True) for col in row.find_all("td") if col.get_text()] for row in rows]

    # Create DataFrame and clean up
    df = pd.DataFrame(data, columns=["Currency", "Selling TT/OD", "Buying TT", "Buying OD", "Selling Notes", "Buying Notes"])
    df["Date"] = date.today()

    # Save to CSV
    filename = f'{forex_date.date()}_exchange_rates.csv'
    df.to_csv(filename, index=False)
    print(f"Saved to CSV: {filename}")

    # Save screenshot
    hti = Html2Image(size=(1980, 5000))  # Set desired screenshot size
    hti.screenshot(url='https://www.maybank2u.com.my/maybank2u/malaysia/en/personal/rates/forex_rates.page', save_as=f'{forex_date.date()}_exchange_rates.png')
    


if __name__ == "__main__":
    scrape_maybank_forex_rates()
