from dotenv import load_dotenv
import os
import streamlit as st
from streamlit_chat import message
from streamlit_extras.colored_header import colored_header
from streamlit_extras.add_vertical_space import add_vertical_space


if "authentication_status" not in st.session_state:
    st.session_state.authentication_status = ""

if st.session_state.authentication_status:
    TITLE = "ChatBot - Third Brain"
    ABOUT = """
        Engage in dynamic conversations with our advanced Conversational ChatBot, powered by ChatGPT. Our ChatBot utilizes cutting-edge language technology, including Langchain and ChatGPT, to deliver interactive and natural interactions.

        With Langchain, our ChatBot understands and responds to a wide range of languages, breaking down communication barriers and fostering global connections. Whether you're looking for casual chat, information, or even language practice, our ChatBot is here to provide an immersive and engaging experience.

        Experience the future of conversational AI with ChatGPT and Langchain. Interact with our intelligent ChatBot and explore the limitless possibilities of natural language understanding and communication. Start a conversation today and see how our ChatBot can enrich your online experience.
        """

    about_content = "\n".join([line for line in ABOUT.splitlines() if line.strip()])

    st.set_page_config(
        page_icon="💬",
        page_title=TITLE,
        layout="wide",
        initial_sidebar_state="auto",
        menu_items={"About": f"{TITLE}{about_content}"},
    )

    if "audio" not in st.session_state:
        st.session_state.audio = {}

    audiobook = st.selectbox(
        "Choose your book",
        list(st.session_state.audio.keys()),
    )

    # Create a column layout.
    col1, col2 = st.columns(2)

    with col1:
        # Create a button to play audiobook.
        if st.button(
            label="Read Book",  # name on the button
            help="Click to Read Book",  # hint text (on hover)
            key="read_audiobook",  # key to be used for the button
            type="primary",  # red default streamlit button
        ):
            selected_book = audiobook
            selected_file_content = st.session_state.audio[selected_book]

            # Perform the desired action with the selected book and its file content
            # For example, you can use text-to-speech to read the audiobook
            # or display the file content in another component
            # Display the image URLs
            for url in st.session_state.url[selected_book]:
                st.image(url, caption="Image")

            st.write(selected_file_content)
