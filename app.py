import streamlit as st
import openai
import pandas as pd
import csv
import requests
import io

st.set_page_config(page_title="AnnotationBOT", page_icon="📐")
st.title("📐 AnnotationBOT")
st.markdown("Ask for drawing annotation suggestions based on a curated annotation database.")
# Set up OpenAI client
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# --- Load CSV from GitHub and parse it into dicts ---

@st.cache_data
def load_and_format_database(url, max_entries=None):
    response = requests.get(url)
    file_like = io.StringIO(response.text)
    reader = csv.DictReader(file_like)
    data = []
    for row in reader:
        data.append(row)
        if max_entries and len(data) >= max_entries:
            break
    return data

# GitHub raw CSV URL
csv_url = "https://raw.githubusercontent.com/YOUR-USERNAME/YOUR-REPO/main/Database_1000.csv"
database = load_and_format_database(csv_url, max_entries=200)

# --- Format database as prompt text ---

def format_database_as_prompt(data):
    prompt = "Here's the civil engineering annotations database:\n\n"
    for i, entry in enumerate(data, 1):
        drawing = entry.get("Drawing", "N/A")
        description = entry.get("Description", "N/A")
        annotations = entry.get("Annotation", "N/A")
        prompt += f"{i}. Drawing: {drawing}\n Description: {description}\n   Annotations: {annotations}\n\n"
    return prompt

database_prompt = format_database_as_prompt(database)

# --- Chat interface ---

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_prompt = st.chat_input("Ask something like: annotations for precast box beam...")

if user_prompt:
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    # Build full prompt with database context
    system_prompt = (
        "You are a helpful assistant for civil engineering construction drawings. "
        "Use the database of past annotations to suggest relevant notes."
    )

    full_user_prompt = f"{database_prompt}\n\nUser query: {user_prompt}"

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": full_user_prompt},
                ]
            )
            reply = response.choices[0].message.content
            st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})

            # Optional: show cost
            usage = response.usage
            total_cost = (usage.prompt_tokens / 1000) * 0.0005 + (usage.completion_tokens / 1000) * 0.0015
            st.info(f"Estimated cost: ${total_cost:.6f}")
