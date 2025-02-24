from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import requests
import os
import json
from dotenv import load_dotenv

# ✅ Load API keys from .env file
load_dotenv()
GOOGLE_CIVIC_API_KEY = os.getenv("GOOGLE_CIVIC_API_KEY")

app = FastAPI()

# Request model
class ZipRequest(BaseModel):
    zip_codes: List[str]

# ✅ Get representative from Google Civic API
def get_district_and_representative(zip_code: str):
    google_api_key = os.getenv("GOOGLE_CIVIC_API_KEY")
    url = f"https://www.googleapis.com/civicinfo/v2/representatives?address={zip_code}&roles=legislatorLowerBody&key={google_api_key}"

    response = requests.get(url)
    print(f"Google API Response for ZIP {zip_code}: {response.status_code} - {response.text}")

    if response.status_code == 200:
        try:
            data = response.json()
            divisions = data.get("divisions", {})
            district_number, state_abbreviation = None, None

            for key in divisions.keys():
                if "cd:" in key:
                    district_number = key.split("cd:")[-1]
                    state_abbreviation = key.split("/state:")[-1].split("/")[0].upper()

            officials = data.get("officials", [])
            if officials:
                representative = officials[0]
                representative_name = representative.get("name", "Unknown")
                party = representative.get("party", "Unknown")
                return district_number, state_abbreviation, representative_name, party

        except Exception as e:
            print(f"Error processing Google Civic API response: {e}")

    return None, None, None, None

# ✅ Get committees from scraped JSON data
def get_committees(representative_name: str):
    try:
        with open("house_committees.json", "r") as house_file, open("senate_committees.json", "r") as senate_file:
            house_committees = json.load(house_file)
            senate_committees = json.load(senate_file)

        committees = []

        for committee, members in house_committees.items():
            if representative_name in members:
                committees.append(committee)

        for committee, members in senate_committees.items():
            if representative_name in members:
                committees.append(committee)

        print(f"Committees for {representative_name}: {committees}")
        return committees

    except Exception as e:
        print(f"Error loading committee files: {e}")
        return []

@app.post("/lookup")
def lookup_zipcodes(request: ZipRequest):
    results = []
    for zip_code in request.zip_codes:
        district, state, representative_name, party = get_district_and_representative(zip_code)
        if not district or not state or not representative_name:
            results.append({"zip_code": zip_code, "error": "Representative data not found"})
            continue

        committees = get_committees(representative_name)

        results.append({
            "zip_code": zip_code,
            "name": representative_name,
            "party": party,
            "district": f"{state}-{district}",
            "committees": committees
        })

    return {"results": results}
