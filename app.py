import streamlit as st
import openai
import os

# Optional: use Streamlit secrets or environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")  # or st.secrets["OPENAI_API_KEY"]

st.set_page_config(page_title="Annotation Assistant", page_icon="📐")

st.title("📐 Drawing Annotation Assistant")
st.markdown("Ask a question and get help based on your annotation knowledge.")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input box
user_prompt = st.chat_input("Ask something like: annotations for precast box beam...")

if user_prompt:
    # Display user message
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    # Call OpenAI
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",  # or "gpt-4"
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant for civil engineering drawing annotations."},
                        {"role": "user", "content": user_prompt},
                    ]
                )
                reply = response.choices[0].message["content"]
            except Exception as e:
                reply = f"❌ Error: {str(e)}"

            st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
