import streamlit as st
import json
import random
import os

def call_gemini_api(q_data, user_choice, chat_history):
    try:
        import google.generativeai as genai
        
        # Configure Gemini API key
        if "GEMINI_API_KEY" in st.secrets:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        else:
            return "Erreur : La clé GEMINI_API_KEY n'est pas définie dans vos secrets Streamlit."
            
        # Create a helpful system instruction using the question context
        system_instruction = f"""Tu es un tuteur pédagogique expert préparant un candidat aux examens d'aptitude et de logique (notamment le raisonnement verbal).
Voici le contexte complet de la question en cours :
- Énoncé / Question : {q_data['question']}
- Options proposées : {', '.join(q_data['options'])}
- Réponse donnée par l'utilisateur : {user_choice}
- Bonne réponse attendue : {q_data['answer']}
- Correction / Explications officielles : {q_data['correction']}

Consignes de comportement :
1. Sois très bienveillant, clair, concis et extrêmement pédagogue dans tes réponses.
2. Ne donne jamais de réponses fausses ou d'informations contradictoires avec la correction officielle.
3. Guide l'utilisateur pas à pas pour qu'il comprenne sa méprise ou pour éclaircir ses doutes.
4. Réponds toujours en français.
5. N'introduis pas tes réponses. 
6. Fournis des réponses courtes, va droit au but.
"""

        model = genai.GenerativeModel("gemini-3.5-flash", system_instruction=system_instruction)
        
        # Build chat history for Gemini API (user / model)
        formatted_history = []
        for msg in chat_history[:-1]:
            role = "user" if msg["role"] == "user" else "model"
            formatted_history.append({"role": role, "parts": [msg["content"]]})
            
        chat_session = model.start_chat(history=formatted_history)
        response = chat_session.send_message(chat_history[-1]["content"])
        return response.text
    except Exception as e:
        return f"Désolé, une erreur est survenue lors de l'appel à l'assistant IA : {str(e)}"

def inject_custom_css():
    st.markdown("""
        <style>
        /* 1. Contrainte de largeur maximale et centrage */
        .block-container {
            max-width: 800px;
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        
        /* 2. Style des 'Cartes' pour les conteneurs */
        div[data-testid="stVerticalBlock"] > div > div[data-testid="stVerticalBlock"] {
            background-color: #ffffff;
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
            border: 1px solid #f0f0f0;
            margin-bottom: 1rem;
        }

        /* 3. Style de l'Expander (Correction) */
        div[data-testid="stExpander"] {
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            box-shadow: none;
        }
        div[data-testid="stExpander"] > details > summary {
            color: #495057;
            font-weight: 500;
        }

        /* 4. Bouton Call-To-Action (Primaire) */
        button[kind="primary"] {
            background-color: #111827 !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 0.5rem 1rem !important;
            font-weight: 600 !important;
            transition: all 0.2s ease !important;
            width: 100% !important;
        }
        button[kind="primary"]:hover {
            background-color: #374151 !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
        }

        /* Personnalisation douce de l'alerte d'erreur */
        div[data-testid="stAlert"] {
            border-radius: 8px;
        }

        /* 6. Sidebar Navigation Styling (simulation d'onglets) */
        [data-testid="stSidebarNav"] span {
            font-size: 15px;
            font-weight: 500;
        }
        </style>
    """, unsafe_allow_html=True)

def load_data(category):
    filepath = os.path.join("data", f"{category}.json")
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    import re
    def clean_text_and_get_explanation(text):
        if not isinstance(text, str):
            return text, None
        # Matches \nExplanation\n, \nExplanation\r\n, \nExplanation:, \nExplanation :, case-insensitive
        pattern = r'\r?\n[Ee]xplanation\s*(?:\r?\n|:|\s:)\s*'
        parts = re.split(pattern, text)
        if len(parts) > 1:
            return parts[0].strip(), parts[1].strip()
        return text.strip(), None

    cleaned_data = []
    for q in data:
        cleaned_q = q.copy()
        options = q.get("options", [])
        cleaned_options = []
        explanations = []
        for opt in options:
            opt_text, opt_expl = clean_text_and_get_explanation(opt)
            cleaned_options.append(opt_text)
            if opt_expl:
                explanations.append((opt_text, opt_expl))
        
        cleaned_q["options"] = cleaned_options
        
        ans_text, ans_expl = clean_text_and_get_explanation(q.get("answer", ""))
        cleaned_q["answer"] = ans_text
        
        # Build correction
        orig_correction = q.get("correction", "").strip()
        if explanations:
            new_correction_parts = []
            if orig_correction:
                new_correction_parts.append(orig_correction)
                new_correction_parts.append("")
            
            new_correction_parts.append("**Explications détaillées :**")
            for opt_text, opt_expl in explanations:
                new_correction_parts.append(f"• **{opt_text}** :\n  {opt_expl}")
            
            cleaned_q["correction"] = "\n\n".join(new_correction_parts)
        elif orig_correction:
            cleaned_q["correction"] = orig_correction
            
        cleaned_data.append(cleaned_q)
        
    return cleaned_data

def reset_quiz():
    st.session_state.quiz_active = False
    st.session_state.current_category = None
    st.session_state.questions = []
    st.session_state.current_q_index = 0
    st.session_state.user_answers = {}
    st.session_state.show_correction = False
    st.session_state.quiz_finished = False
    st.session_state.chat_histories = {}

def init_quiz(category, num_questions):
    if 'quiz_active' not in st.session_state:
        reset_quiz()
        
    data = load_data(category)
    # Randomly select questions
    selected_questions = random.sample(data, min(num_questions, len(data)))
    
    st.session_state.quiz_active = True
    st.session_state.current_category = category
    st.session_state.questions = selected_questions
    st.session_state.current_q_index = 0
    st.session_state.user_answers = {}
    st.session_state.show_correction = False
    st.session_state.quiz_finished = False
    st.session_state.chat_histories = {}

def next_question():
    st.session_state.current_q_index += 1
    st.session_state.show_correction = False
    if st.session_state.current_q_index >= len(st.session_state.questions):
        st.session_state.quiz_finished = True

def render_quiz(category):
    inject_custom_css()

    # Check if we need to reset because we changed category mid-quiz
    if 'current_category' in st.session_state and st.session_state.current_category != category and st.session_state.current_category is not None:
        reset_quiz()

    if 'quiz_active' not in st.session_state or not st.session_state.quiz_active:
        st.title(f"Entraînement - {category.capitalize()}")
        num_q = st.number_input("Combien de questions souhaitez-vous réaliser ?", min_value=1, max_value=10, value=5)
        if st.button("Lancer le test", type="primary"):
            init_quiz(category, num_q)
            st.rerun()
        return

    if st.session_state.quiz_finished:
        render_results()
        return

    # Render current question
    q_index = st.session_state.current_q_index
    total_q = len(st.session_state.questions)
    q_data = st.session_state.questions[q_index]
    
    st.write(f"Progression : {q_index + 1} / {total_q}")
    st.progress((q_index + 1) / total_q)
    
    with st.container():
        st.markdown(f'<div style="font-weight: bold; font-size: 14px;">{q_data["question"]}</div>', unsafe_allow_html=True)
        st.write("Votre réponse :")
        
        # User choice
        if not st.session_state.show_correction:
            user_choice = st.radio("Sélectionnez :", q_data["options"], key=f"q_{q_index}", label_visibility="collapsed")
        else:
            # Format options with emojis based on correctness
            correct_answer = q_data["answer"]
            user_choice = st.session_state.user_answers.get(q_index, "")
            
            formatted_options = []
            for opt in q_data["options"]:
                if opt == correct_answer:
                    formatted_options.append(f"{opt} ✅ (Bonne réponse)")
                elif opt == user_choice and opt != correct_answer:
                    formatted_options.append(f"{opt} ❌ (Votre réponse)")
                else:
                    formatted_options.append(opt)
            
            # Display formatted options as disabled radio (we just use standard radio but ignore input)
            st.radio("Sélectionnez :", formatted_options, index=q_data["options"].index(user_choice) if user_choice in q_data["options"] else 0, key=f"q_ans_{q_index}", label_visibility="collapsed", disabled=True)
    
    if not st.session_state.show_correction:
        with st.container():
            if st.button("Valider et afficher la réponse", type="primary", use_container_width=True):
                st.session_state.user_answers[q_index] = user_choice
                st.session_state.show_correction = True
                st.rerun()
    else:
        # Show answer and correction
        with st.container():
            correct_answer = q_data["answer"]
            if user_choice == correct_answer:
                st.success("Bonne réponse !")
            else:
                st.error(f"Mauvaise réponse. La bonne réponse était : {correct_answer}")
                
            with st.expander("Afficher la correction"):
                st.write(q_data["correction"])
                
            st.write("") # Espacement
            
            # --- AI Chatbot Section ---
            st.write("---")
            st.write("### 🤖 Assistant IA - Posez vos questions !")
            
            # Use JSON ID as the chat identifier to keep memory per question
            q_id = str(q_data.get("id", q_index))
            
            if "chat_histories" not in st.session_state:
                st.session_state.chat_histories = {}
            if q_id not in st.session_state.chat_histories:
                st.session_state.chat_histories[q_id] = []
                
            # Display chat messages from history
            for msg in st.session_state.chat_histories[q_id]:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])
                    
            # Chat input
            if user_query := st.chat_input("Ex: Expliquez-moi pourquoi l'autre option est incorrecte...", key=f"chat_input_{q_id}"):
                # Add user query to history and display it
                st.session_state.chat_histories[q_id].append({"role": "user", "content": user_query})
                with st.chat_message("user"):
                    st.write(user_query)
                    
                # Call Gemini API
                with st.chat_message("assistant"):
                    with st.spinner("L'assistant IA réfléchit..."):
                        response_text = call_gemini_api(q_data, user_choice, st.session_state.chat_histories[q_id])
                        st.write(response_text)
                        
                # Add assistant response to history
                st.session_state.chat_histories[q_id].append({"role": "assistant", "content": response_text})
                st.rerun()
            # --------------------------
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("Passer à la question suivante", type="primary", use_container_width=True):
                    next_question()
                    st.rerun()

def render_results():
    st.title("Résultats du test")
    
    score = 0
    questions = st.session_state.questions
    answers = st.session_state.user_answers
    
    for i, q in enumerate(questions):
        if i in answers and answers[i] == q["answer"]:
            score += 1
            
    st.header(f"Votre score : {score} / {len(questions)}")
    
    st.write("### Récapitulatif")
    for i, q in enumerate(questions):
        user_ans = answers.get(i, "")
        correct_ans = q["answer"]
        is_correct = (user_ans == correct_ans)
        
        status_label = "Bonne réponse ✅" if is_correct else "Mauvaise réponse ❌"
        expander_title = f"Question {i + 1} : {status_label}"
        
        with st.expander(expander_title):
            st.markdown(f'<div style="font-weight: bold; font-size: 14px; margin-bottom: 10px;">{q["question"]}</div>', unsafe_allow_html=True)
            
            # Format options with emojis based on correctness
            formatted_options = []
            for opt in q["options"]:
                if opt == correct_ans:
                    formatted_options.append(f"{opt} ✅ (Bonne réponse)")
                elif opt == user_ans and opt != correct_ans:
                    formatted_options.append(f"{opt} ❌ (Votre réponse)")
                else:
                    formatted_options.append(opt)
            
            # Display formatted options as disabled radio
            st.radio("Options :", formatted_options, index=q["options"].index(user_ans) if user_ans in q["options"] else 0, key=f"recap_q_ans_{i}", label_visibility="collapsed", disabled=True)
            
            st.write("**Correction :**")
            st.info(q["correction"])
            
            # --- AI Chatbot Section ---
            st.write("---")
            st.write("### 🤖 Assistant IA - Posez vos questions !")
            
            q_id = str(q.get("id", i))
            
            if "chat_histories" not in st.session_state:
                st.session_state.chat_histories = {}
            if q_id not in st.session_state.chat_histories:
                st.session_state.chat_histories[q_id] = []
                
            # Display chat messages from history
            for msg in st.session_state.chat_histories[q_id]:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])
                    
            # Chat input
            if user_query := st.chat_input("Ex: Expliquez-moi pourquoi l'autre option est incorrecte...", key=f"recap_chat_input_{q_id}"):
                st.session_state.chat_histories[q_id].append({"role": "user", "content": user_query})
                with st.chat_message("user"):
                    st.write(user_query)
                    
                with st.chat_message("assistant"):
                    with st.spinner("L'assistant IA réfléchit..."):
                        response_text = call_gemini_api(q, user_ans, st.session_state.chat_histories[q_id])
                        st.write(response_text)
                        
                st.session_state.chat_histories[q_id].append({"role": "assistant", "content": response_text})
                st.rerun()
            
    if st.button("Recommencer un test"):
        reset_quiz()
        st.rerun()
