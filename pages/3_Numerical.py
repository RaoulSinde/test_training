import sys
import os
import streamlit as st

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.quiz_logic import render_quiz

st.set_page_config(page_title="Raisonnement Numérique", page_icon="🔢")

render_quiz("numerical")
