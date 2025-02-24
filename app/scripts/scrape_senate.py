import requests
from bs4 import BeautifulSoup
import json
import time

# URL of the Senate Committees Membership Page
SENATE_COMMITTEES_URL = "https://www.senate.gov/committees/membership.htm"

# Optional headers to mimic a browser request (helps avoid blocks)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
}

def scrape_committee_members(url):
    """
    Given a URL for a committee page, scrape and return a list of member names.
    """
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            print(f"Failed to load {url}: {response.status_code}")
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        # Debug: print a preview of the HTML to help adjust selectors if needed
        print(f"Scraping {url}... preview:\n", soup.prettify()[:500])

        # Try a list of possible selectors for member names
        selectors = [
            "div.member-name", 
            "ul.members-list li", 
            "div.members li", 
            ".member", 
            ".person-name"
        ]
        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                members = [element.get_text(strip=True) for element in elements]
                print(f"Found {len(members)} members using selector '{selector}'")
                return members
        
        print(f"No members found on {url} using available selectors.")
        return []
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return []

def scrape_senate_committees():
    """
    Scrape the Senate committees page to extract all committees and then scrape
    each committee page for its members.
    Returns a dictionary where keys are committee names and values are lists of member names.
    """
    try:
        response = requests.get(SENATE_COMMITTEES_URL, headers=HEADERS)
        if response.status_code != 200:
            print(f"Failed to retrieve Senate committees page: {response.status_code}")
            return {}

        soup = BeautifulSoup(response.text, "html.parser")
        committees = {}

        # Selector for committee links – may need to be adjusted based on page structure.
        committee_links = soup.select("a[href*='committee']")
        if not committee_links:
            print("No committee links found. Check the CSS selector on the main page.")
            return {}

        for link in committee_links:
            committee_name = link.text.strip()
            committee_url = link.get("href")
            if not committee_url.startswith("http"):
                committee_url = "https://www.senate.gov" + committee_url

            print(f"Scraping committee: {committee_name} ({committee_url})")
            members = scrape_committee_members(committee_url)
            committees[committee_name] = members

            # Sleep for 2 seconds to avoid overwhelming the server
            time.sleep(2)

        return committees
    except Exception as e:
        print(f"Error scraping Senate committees: {e}")
        return {}

if __name__ == "__main__":
    senate_committees = scrape_senate_committees()
    # Save the scraped data to a JSON file
    with open("senate_committees.json", "w") as outfile:
        json.dump(senate_committees, outfile, indent=4)
    print("Senate Committees Scraped Successfully!")
