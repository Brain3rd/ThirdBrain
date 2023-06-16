from dotenv import load_dotenv
import os
import streamlit as st
from streamlit_chat import message
from streamlit_extras.colored_header import colored_header
from streamlit_extras.add_vertical_space import add_vertical_space

TITLE = "Text Reader - Third Brain"
ABOUT = """
Welcome to the Text Reader App, a powerful tool designed for text reading and accessibility. Our app utilizes advanced AI text-to-speech features to bring written content to life.

With our Text Reader App, you can easily convert text into natural and expressive speech. Whether you have articles, documents, or even eBooks, our app empowers you to listen to your text-based content effortlessly. Enhance your reading experience, save time, and cater to diverse needs with our AI-powered text-to-speech capabilities.

Immerse yourself in the world of accessible information with the Text Reader App. Unlock the potential of AI to transform written content into engaging audio experiences. Start using our app today and embark on a new way of consuming text-based information.
    """

about_content = "\n".join([line for line in ABOUT.splitlines() if line.strip()])

st.set_page_config(
    page_icon="📙",
    page_title=TITLE,
    layout="wide",
    initial_sidebar_state="auto",
    menu_items={"About": f"{TITLE}{about_content}"},
)

if "authentication_status" not in st.session_state:
    st.session_state.authentication_status = ""

if st.session_state.authentication_status:
    with st.sidebar:
        st.title(TITLE)
        st.markdown(ABOUT)
        add_vertical_space(5)
        st.write("💡 Note: API key required!")

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
