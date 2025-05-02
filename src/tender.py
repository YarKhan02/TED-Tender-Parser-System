import os
import json
import re
import pandas as pd
import google.generativeai as genai
from dotenv import load_dotenv

from match_refernces import match_references_to_tender
from utils import load_tender_files

# Load environment variables from .env file
load_dotenv()

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY is not set in the environment or .env file.")

# Initialize Gemini API
genai.configure(api_key=api_key)

def extract_fields_from_tender(text: str) -> dict:
    prompt = f"""
                Extract the following fields from the tender text:
                - Project name
                - Location
                - Budget (Kostengruppen 300 + 400 combined)
                - Project type
                - Phases
                - Submission deadline

                Return the result as a JSON object.

                Tender Text:
                {text}
            """

    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)

    # Get the text from the first candidate
    response_text = response.candidates[0].content.parts[0].text.strip()

    # Remove Markdown formatting (```json ... ```)
    cleaned_json = re.sub(r"^```json\n?|```$", "", response_text, flags=re.MULTILINE).strip()

    # Parse JSON string to dict
    try:
        extracted_fields = json.loads(cleaned_json)

        # Rename "Budget (Kostengruppen 300 + 400 combined)" to "Budget" if present
        if "Budget (Kostengruppen 300 + 400 combined)" in extracted_fields:
            extracted_fields["Budget"] = extracted_fields.pop("Budget (Kostengruppen 300 + 400 combined)")

        return extracted_fields
    except json.JSONDecodeError:
        print("Error decoding JSON. Raw response:")
        print(cleaned_json)
        return {}


def main():
    print("Starting the tender extraction process...")
    path = "./data/tenders"
    tender_texts = load_tender_files(path)

    tenders = []

    for filename, text in tender_texts:
        extracted_fields = extract_fields_from_tender(text)
        tenders.append({"filename": filename, "fields": extracted_fields, "matches": []})
        
    # Load references from Excel
    references_df = pd.read_excel("./data/references.xlsx")

    for tender in tenders:
        top_matches = match_references_to_tender(tender["fields"], references_df)
        # Handle missing or NaN certifications
        for match in top_matches:
            if "Certifications" in match["reference"]:
                if match["reference"]["Certifications"] is None or pd.isna(match["reference"]["Certifications"]):
                    match["reference"]["Certifications"] = "None"
        tender["matches"] = top_matches

    # Save tenders with matches for further use
    with open("./data/tenders_with_matches.json", "w", encoding="utf-8") as f:
        json.dump(tenders, f, indent=4, ensure_ascii=False)
        print("\nTenders with matches saved to './data/tenders_with_matches.json'")

if __name__ == "__main__":
    main()