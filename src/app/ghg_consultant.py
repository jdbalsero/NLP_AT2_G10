import streamlit as st
import asyncio

def display_ghg_consultant():

    rag_class = st.session_state.rag_class

    st.header("GHG Consultant")

    if not rag_class.embedding_class.has_embeddings():
        st.warning(
            "No local embeddings were found in `chroma_persistent_storage/`. "
            "Restore the folder or generate embeddings from the PDFs below."
        )
        if st.button("Generate embeddings locally"):
            with st.spinner("Building embeddings from source PDFs..."):
                result = rag_class.run_embedding_process()
            if result == "Process Complete":
                st.success("Embeddings generated successfully.")
                st.rerun()
            st.error(result)
        return

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):  
            st.markdown(message["content"])

    # React to user input
    if prompt:= st.chat_input("Say Something"):
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

            with st.spinner("🍃 Generating Response..."):
                # try:
                #     response = asyncio.run(rag_class.generate_response(
                #         question=prompt, 
                #         relevant_chunks=relevant_chunks, 
                #         results_metadata=results_metadata
                #     ))
                # except Exception as e:
                #     response = f"Error generating response: {str(e)}"
                response = rag_class.generate_response(
                        question=prompt, 
                        relevant_chunks=relevant_chunks, 
                        results_metadata=results_metadata
                    )
                
            placeholder.markdown(response)
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
