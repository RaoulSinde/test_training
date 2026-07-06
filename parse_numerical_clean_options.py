import re
import json

def clean_option(text):
    text = text.replace("##Bonne réponse##", "").strip()
    # Strip leading bullet/dot/dash if followed by space or text
    cleaned = re.sub(r'^[·•\-*\.]\s+', '', text)
    return cleaned

def parse_raw_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.splitlines()

    questions = []
    current_q = None
    state = None # "QUESTION", "OPTIONS", "EXPLANATION"
    
    i = 0
    n = len(lines)
    
    while i < n:
        line = lines[i].strip()
        
        # Check for new question block
        if re.match(r'^\d+$', line):
            q_id = int(line)
            expected_id = len(questions) + (2 if current_q else 1)
            if q_id == expected_id:
                if current_q:
                    questions.append(current_q)
                current_q = {
                    "id": q_id,
                    "question": "",
                    "options": [],
                    "answer": "",
                    "correction": ""
                }
                state = "QUESTION"
                i += 1
                continue
        
        if current_q:
            if state == "QUESTION":
                if line == "":
                    if current_q["question"] != "":
                        state = "OPTIONS"
                else:
                    if current_q["question"] == "":
                        current_q["question"] = line
                    else:
                        current_q["question"] += "\n" + line
            elif state == "OPTIONS":
                if line == "Explanation":
                    state = "EXPLANATION"
                elif line != "":
                    is_correct = "##Bonne réponse##" in line
                    cleaned = clean_option(line)
                    # Filter out dots or empty choices
                    if cleaned != "." and cleaned != "":
                        current_q["options"].append(cleaned)
                        if is_correct:
                            current_q["answer"] = cleaned
            elif state == "EXPLANATION":
                if current_q["correction"] == "":
                    current_q["correction"] = line
                else:
                    current_q["correction"] += "\n" + line
                    
        i += 1
        
    if current_q:
        questions.append(current_q)
        
    for q in questions:
        q["correction"] = q["correction"].strip()
        
    return questions

questions = parse_raw_file("numerical_raw_questions.txt")

with open("data/numerical.json", "w", encoding="utf-8") as f:
    json.dump(questions, f, indent=2, ensure_ascii=False)

print(f"Successfully cleaned options, parsed {len(questions)} questions and updated data/numerical.json!")
