import json
import pandas as pd
import google.generativeai as genai


# Initialize Gemini
genai.configure(api_key="AIzaSyDfxOZ9BLScnRDwkEwqsj-CRUfLlrEvx4A")
model = genai.GenerativeModel("gemini-2.0-flash")


def ask_gemini_for_match_score(tender, reference) -> dict:
    prompt = f"""
                You are comparing a public tender and an internal reference project.
                Evaluate how closely the reference project matches the tender in terms of:

                - Project type
                - Phases
                - Budget
                - Location
                - General similarity

                Give:
                1. A matching score from 0.0 to 1.0
                2. A short explanation (2–4 lines) of the reasoning.

                Format your response as valid JSON:
                {{
                "score": float (0.0 to 1.0),
                "reason": string
                }}

                Tender:
                {json.dumps(tender, indent=2)}

                Reference:
                {json.dumps(reference, indent=2)}
            """

    try:
        response = model.generate_content(prompt)
        content = response.text

        # Extract the JSON from markdown if needed
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()

        return json.loads(content)

    except Exception as e:
        print("Gemini error:", e)
        return {"score": 0.0, "reason": "Error during comparison."}


def match_references_to_tender(tender: dict, references_df: pd.DataFrame, top_n=3) -> list:
    matches = []

    for _, row in references_df.iterrows():
        reference = row.to_dict()
        result = ask_gemini_for_match_score(tender, reference)

        matches.append({
            "reference": reference,
            "score": round(result.get("score", 0.0), 3),
            "reason": result.get("reason", "No reasoning provided.")
        })

    return sorted(matches, key=lambda x: x["score"], reverse=True)[:top_n]