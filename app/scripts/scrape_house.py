# scripts/scrape_base.py
import logging
import time
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
import json
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraping.log'),
        logging.StreamHandler()
    ]
)

class RateLimiter:
    """Rate limiter to prevent overwhelming the server"""
    def __init__(self, requests_per_minute: int = 30):
        self.delay = 60.0 / requests_per_minute
        self.last_request = 0

    def wait(self):
        """Wait appropriate amount of time between requests"""
        now = time.time()
        elapsed = now - self.last_request
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)
        self.last_request = time.time()

class CommitteeScraper(ABC):
    """Base class for committee scrapers"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.rate_limiter = RateLimiter()
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/119.0.0.0 Safari/537.36"
            )
        }

    def make_request(self, url: str) -> Optional[BeautifulSoup]:
        """Make an HTTP request with rate limiting and error handling"""
        self.rate_limiter.wait()
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            return BeautifulSoup(response.text, "html.parser")
        except requests.RequestException as e:
            self.logger.error(f"Error fetching {url}: {str(e)}")
            return None

    @abstractmethod
    def scrape_committees(self) -> Dict[str, List[str]]:
        """Scrape committee data - to be implemented by subclasses"""
        pass

    def save_data(self, data: Dict[str, List[str]], filename: str):
        """Save scraped data to JSON file"""
        try:
            output_path = Path("data") / filename
            output_path.parent.mkdir(exist_ok=True)
            
            with output_path.open("w") as f:
                json.dump(data, f, indent=4)
            self.logger.info(f"Successfully saved data to {output_path}")
        except Exception as e:
            self.logger.error(f"Error saving data: {str(e)}")
            raise

# scripts/scrape_house.py
class HouseCommitteeScraper(CommitteeScraper):
    BASE_URL = "https://www.house.gov"
    COMMITTEES_URL = f"{BASE_URL}/committees"

    def scrape_committee_members(self, url: str) -> List[str]:
        """Scrape members from a committee page"""
        soup = self.make_request(url)
        if not soup:
            return []

        members = []
        # Try multiple selector patterns
        selectors = [
            "div.member-name", 
            ".roster-member h4",
            ".member-info h3",
            ".member-card h3"
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                members = [element.get_text(strip=True) for element in elements]
                self.logger.info(f"Found {len(members)} members using selector '{selector}'")
                break
                
        return members

    def scrape_committees(self) -> Dict[str, List[str]]:
        """Scrape all House committees and their members"""
        soup = self.make_request(self.COMMITTEES_URL)
        if not soup:
            return {}

        committees = {}
        committee_links = soup.select("a[href^='/committees/']")
        
        for link in committee_links:
            committee_name = link.text.strip()
            if not committee_name or "historical" in committee_name.lower():
                continue
                
            committee_url = link.get("href")
            if not committee_url.startswith("http"):
                committee_url = f"{self.BASE_URL}{committee_url}"
                
            self.logger.info(f"Scraping committee: {committee_name}")
            members = self.scrape_committee_members(committee_url)
            committees[committee_name] = members

        return committees

# scripts/scrape_senate.py
class SenateCommitteeScraper(CommitteeScraper):
    BASE_URL = "https://www.senate.gov"
    COMMITTEES_URL = f"{BASE_URL}/committees/membership.htm"

    def scrape_committee_members(self, url: str) -> List[str]:
        """Scrape members from a Senate committee page"""
        soup = self.make_request(url)
        if not soup:
            return []

        members = []
        selectors = [
            ".member-name",
            ".committee-member h4",
            ".senator-name",
            ".member-info strong"
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                members = [element.get_text(strip=True) for element in elements]
                self.logger.info(f"Found {len(members)} members using selector '{selector}'")
                break
                
        return members

    def scrape_committees(self) -> Dict[str, List[str]]:
        """Scrape all Senate committees and their members"""
        soup = self.make_request(self.COMMITTEES_URL)
        if not soup:
            return {}

        committees = {}
        committee_links = soup.select("a[href*='committee']")
        
        for link in committee_links:
            committee_name = link.text.strip()
            if not committee_name or "historical" in committee_name.lower():
                continue
                
            committee_url = link.get("href")
            if not committee_url.startswith("http"):
                committee_url = f"{self.BASE_URL}{committee_url}"
                
            self.logger.info(f"Scraping committee: {committee_name}")
            members = self.scrape_committee_members(committee_url)
            committees[committee_name] = members

        return committees

# scripts/__main__.py
def main():
    """Main entry point for scraping scripts"""
    logging.info("Starting committee scraping process")
    
    try:
        # Scrape House committees
        house_scraper = HouseCommitteeScraper()
        house_committees = house_scraper.scrape_committees()
        house_scraper.save_data(house_committees, "house_committees.json")
        
        # Scrape Senate committees
        senate_scraper = SenateCommitteeScraper()
        senate_committees = senate_scraper.scrape_committees()
        senate_scraper.save_data(senate_committees, "senate_committees.json")
        
        logging.info("Committee scraping completed successfully")
    except Exception as e:
        logging.error(f"Scraping process failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()