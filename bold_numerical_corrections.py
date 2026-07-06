import json
import re

def bold_correction(text):
    # 1. Bold standard section headers
    headers = [
        "Data Interpretation",
        "Reasoning",
        "Calculation",
        "Potential Pitfalls and Shortcuts",
        "Potential Shortcuts / Pitfalls"
    ]
    for header in headers:
        # Match header as a separate line or at start of text, case-insensitive, followed by optional newline/whitespace
        pattern = rf"(?mi)^({re.escape(header)})\s*$"
        text = re.sub(pattern, r"**\1**", text)

    # 2. Bold math equations and country-specific ratios/results
    # E.g. "Bulgaria: 0.44 / 7.42 ~ 0.059"
    text = re.sub(rf"(?m)^([A-Za-z\s&]+:\s*[\d\.\s,\+\-\*/=~x()_]+)$", r"**\1**", text)
    
    # E.g. "Czechia (2018): (76.2 + 82.0) / 2 = 79.1"
    text = re.sub(rf"(?m)^([A-Za-z\s&]+(?:\(\d+\))?:\s*[\d\.\s,\+\-\*/=~x()_]+)$", r"**\1**", text)

    # E.g. formula "Motorway-kilometers-per-person ratio = Total\nMotorways length / Total population"
    # or specific formulas on lines with "="
    # Let's bold equations like: "324,000 / 14,794 = 21.9"
    text = re.sub(rf"(\d[\d\s,]*\s*[\*/+-]\s*\d[\d\s,]*\s*=\s*[\d\.,]+)", r"**\1**", text)
    
    # "108329 - 90233 = 18096"
    # "18096/3 = 6032"
    # "21635 *0.408 = 8827"
    # "8827 *0.091 = 803.26"
    # "21252 * 0.396 * 0.092 = 774.25"
    # "803.26 - 774.25 = 29"
    # "401 days/year x 10 years = 4010 days"
    # "4010- 1571 - 1052 = 1387 days"
    # "1387/8 = 173.375"
    # "10- 2 = 8 years"
    
    # Let's also bold the final conclusion or key answers mentioned in the text
    # e.g. "Spain has the highest" -> "**Spain** has the highest"
    # "Switzerland showed the least" -> "**Switzerland** showed the least"
    # "Romania & Switzerland" -> "**Romania & Switzerland**"
    # Let's replace known correct answers with bold versions
    answers = [
        "Spain", "Switzerland", "15.2 thousand square km", "22 children", "6032", "297 million liters", 
        "Between 2004 and 2008", "+29000", "Up 3.7%", "173 days"
    ]
    for ans in answers:
        # Avoid double bolding if already bolded
        # Replace occurrences of ans not already wrapped in **
        pattern = rf"(?<!\*\*)(?<!\w){re.escape(ans)}(?!\w)(?!\*\*)"
        text = re.sub(pattern, f"**{ans}**", text)

    return text

def main():
    with open("data/numerical.json", "r", encoding="utf-8") as f:
        questions = json.load(f)

    for q in questions:
        q["correction"] = bold_correction(q["correction"])

    with open("data/numerical.json", "w", encoding="utf-8") as f:
        json.dump(questions, f, indent=2, ensure_ascii=False)

    print("Success! Bolded key components of numerical corrections.")

if __name__ == "__main__":
    main()
