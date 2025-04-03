# Import packages
import streamlit as st
import pandas as pd
import sys
import os
from pathlib import Path

# import backend.rag_process

# Set Python path
current_dir = os.path.dirname(__file__)
parent_dir = str(Path(current_dir).resolve().parents[0])
sys.path.append(parent_dir)

from backend.rag_process import rag_process
from backend.ghg_assistant import GHGAssistant

rag_class = rag_process()
ai_assistant = GHGAssistant(
    max_completion_tokens = 800) # that has memory and adds the disclaimer so far

st.title("GHG Consultant")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("Say Something"):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # response = f"Echo: {prompt}"
    relevant_chunks = rag_class.query_documents(question=prompt)
    response = ai_assistant.generate_response(
        user_prompt = prompt,
        context = '\n\n'.join(relevant_chunks)
    )

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})