import streamlit as st
import os
import openai

# MUST be first Streamlit command
st.set_page_config(page_title="Annotation Assistant", page_icon="📐")

# Access the API key from Streamlit secrets
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("📐 Drawing Annotation Assistant")
st.markdown("Ask a question and get help based on your annotation knowledge.")

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input
user_prompt = st.chat_input("Ask something like: annotations for precast box beam...")

if user_prompt:
    # Show user input
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    # Get assistant reply
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant for civil engineering drawing annotations."},
                        {"role": "user", "content": user_prompt},
                    ]
                )
                reply = response.choices[0].message.content
                
                # Calculate usage
                usage = response.usage
                prompt_tokens = usage.prompt_tokens
                completion_tokens = usage.completion_tokens
                
                # Cost per 1K tokens for gpt-3.5-turbo
                input_price = 0.0005
                output_price = 0.0015
                
                # Calculate total cost
                total_cost = (prompt_tokens / 1000) * input_price + (completion_tokens / 1000) * output_price
                
                
            except Exception as e:
                reply = f"❌ Error: {str(e)}"

            st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
            # Show estimated cost
            st.info(f"Estimated cost: ${total_cost:.6f}")
