import streamlit as st
import requests
from model import *

st.set_page_config(
    page_title="Chat-app",
    page_icon="🗯",
    layout="wide",
)

chat_bot = chat_bot()


# Initialize session state for tracking user input and responses
if 'responses' not in st.session_state:
    st.session_state.responses = []
    
# Select model and training parameter
selected_model =chat_bot.models[0]
temperature =  1.5

# Define the URL of the backend chat API
backend_url = "http://127.0.0.1:5000/chat_stream" #local testing
#backend_url = "http://fastapi:5000/chat_stream"

# Function to handle sending messages and receiving responses
def handle_message(user_input):
    if user_input:

        # Add the user input to the session state
        st.session_state.responses.append({'user': user_input, 'bot': None})
        
        # Prepare an empty container to update the bot's response in real-time
        response_container = st.empty()

        # Send the user input to the backend API
        response = requests.post(backend_url, json={"message": user_input, "model":selected_model, "temperature":temperature}, stream=True)

        if response.status_code == 200:
            bot_response = ""
            
            # Collect the batch response
            for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
                bot_response += chunk
            
                # Display the bot's response with adaptable height
                response_container.markdown(f"""
                <div style="background-color:#f0f0f0; padding:10px; border-radius:5px;">
                    <p style="font-family:Arial, sans-serif;">{bot_response.strip()}</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Update the latest bot response in session state
                st.session_state.responses[-1]['bot'] = bot_response.strip()
            
                
        else:
            response_container.markdown("<p style='color:red;'>Error: Unable to get a response from the server.</p>", unsafe_allow_html=True)

        # Clear the input box for the next question
        st.session_state.current_input = ""


# Display the chat history
def display_chat_history():
    with st.container():
        for response in st.session_state.responses[::-1]:

            st.markdown(f"""
            <div style="background-color:#e0e0e0; padding:10px; border-radius:5px;">
                <p style="font-family:Arial, sans-serif;"><strong>You:</strong> {response['user']}</p>
                <p style="font-family:Arial, sans-serif;"><strong>Bot:</strong> {response['bot']}</p>
            </div>
            """, unsafe_allow_html=True)


def main():

    col1, col2, col3 = st.columns([1,0.03,1])
    with col1:

        # Display the chat history first
        st.write("<p style='text-align: center; font-weight: bold;'>Chat History</p>", unsafe_allow_html=True)

        display_chat_history()
    with col3:
        st.write("<p style='text-align: center; font-weight: bold;'>Chat</p>", unsafe_allow_html=True)
        # Input text box for user input
        if 'current_input' not in st.session_state:
            st.session_state.current_input = ""
        user_input = st.text_input("You:", st.session_state.current_input)

        if st.button("Send"):
            handle_message(user_input)



if __name__ == "__main__":
    main()