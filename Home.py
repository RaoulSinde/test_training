import streamlit as st
import sys
import os

# Add parent directory to path to import modules if needed (Home is in root so it can just import)
from modules.quiz_logic import inject_custom_css

st.set_page_config(
    page_title="CAST Training App",
    page_icon="🇪🇺",
    layout="centered"
)

inject_custom_css()

st.title("Bienvenue sur l'application d'entraînement au concours CAST 🇪🇺")

st.markdown("""
Cette application a été conçue pour vous aider à vous préparer aux tests de raisonnement du concours CAST (Contract Agent Selection Tool) du Parlement européen.

### Les épreuves disponibles :
* **Abstract (Raisonnement abstrait)** : Évalue votre capacité à identifier des règles logiques dans des suites de figures ou de nombres.
* **Verbal (Raisonnement verbal)** : Teste votre compréhension de texte, votre vocabulaire et votre logique verbale.
* **Numerical (Raisonnement numérique)** : Mesure votre aisance avec les chiffres, les pourcentages, les ratios et la résolution de problèmes mathématiques simples.

### Comment utiliser l'application :
1. Sélectionnez une catégorie dans le menu latéral à gauche.
2. Choisissez le nombre de questions que vous souhaitez réaliser (jusqu'à 10 par catégorie).
3. Lancez le test et répondez aux questions.
4. Après chaque question, validez pour voir immédiatement la réponse correcte, l'explication détaillée, et poser vos questions à l'Assistant IA.
5. À la fin du test, vous obtiendrez votre score et un récapitulatif détaillé.
6. **Suivi persistant de vos erreurs** : Toutes vos erreurs sont enregistrées automatiquement. Vous pouvez ensuite lancer un test spécifique sur "Mes erreurs" pour vider la liste au fur et à mesure de vos réussites !

Bon entraînement !
""")
