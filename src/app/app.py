# #Async Callbacks workaround
import asyncio
# try:
#     asyncio.get_running_loop()
# except RuntimeError:
#     asyncio.set_event_loop(asyncio.new_event_loop())

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

rag_class = rag_process()

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

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        placeholder = st.empty()

        # Get both chunks and metadata
        relevant_chunks, results_metadata = rag_class.query_documents(question=prompt)

        with st.spinner("🌍🍃 Generating Response..."):
            try:
                response = asyncio.run(rag_class.generate_response(
                    question=prompt, 
                    relevant_chunks=relevant_chunks, 
                    results_metadata=results_metadata
                ))
            except Exception as e:
                response = f"Error generating response: {str(e)}"

        placeholder.markdown(response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})