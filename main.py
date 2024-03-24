import openai
import time
import streamlit as st
import streamlit.secrets as secrets

openai.api_key = secrets["OPENAI_API_KEY"]




def main():

    if 'client' not in st.session_state:
        # Initialize the client
        st.session_state.client = openai.OpenAI()

        st.session_state.file = st.session_state.client.files.create(
            file=open("farmer_disease_gpt_RAG.pdf", "rb"),
            purpose='assistants'
        )

        # Step 1: Create an Assistant
        st.session_state.assistant = st.session_state.client.beta.assistants.create(
            name="farmer helper bot",
            instructions="you are a helper bot for farmers.you will ask for how you can help them today.they can ask many questions about crop diseases,finance,climate,government policies,etc . if they try and tell synptoms for their plant,you will use the knowledge base given to patiently understand the symptoms of the disease described by the farmer and try to accurately find the solution.you will also give them solutions regarding their financial questions and many other areas",
            model="gpt-3.5-turbo-0125",
            file_ids=[st.session_state.file.id],
            tools=[{"type": "retrieval"}]
        )

        # Step 2: Create a Thread
        st.session_state.thread = st.session_state.client.beta.threads.create()

    user_query = st.text_input("Enter your query:", "You can ask any questions related to crop diseases")

    if st.button('Submit'):
        # Step 3: Add a Message to a Thread
        message = st.session_state.client.beta.threads.messages.create(
            thread_id=st.session_state.thread.id,
            role="user",
            content=user_query
        )

        # Step 4: Run the Assistant
        run = st.session_state.client.beta.threads.runs.create(
            thread_id=st.session_state.thread.id,
            assistant_id=st.session_state.assistant.id,
            instructions="Please address the farmer patiently and give accurate answers.give all the information like what caused the disease and what is the best solution?"
        )

        while True:
            # Wait for 5 seconds
            time.sleep(5)

            # Retrieve the run status
            run_status = st.session_state.client.beta.threads.runs.retrieve(
                thread_id=st.session_state.thread.id,
                run_id=run.id
            )

            # If run is completed, get messages
            if run_status.status == 'completed':
                messages = st.session_state.client.beta.threads.messages.list(
                    thread_id=st.session_state.thread.id
                )

                # Loop through messages and print content based on role
                for msg in messages.data:
                    role = msg.role
                    content = msg.content[0].text.value
                    st.write(f"{role.capitalize()}: {content}")
                break
            else:
                st.write("Waiting for the Assistant to process...")
                time.sleep(5)

if __name__ == "__main__":
    main()
