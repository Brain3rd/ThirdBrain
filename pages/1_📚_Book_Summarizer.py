import os
import streamlit as st
from streamlit_extras.add_vertical_space import add_vertical_space
from _summarizer import summarizer
import dropbox
from dropbox.exceptions import AuthError
import math
from cloud import display_book_summaries_and_save_to_database
from database import fetch_all_books


BOOK_FOLDER = "books"

TITLE = "Book Summarizer"
ABOUT = """
    Experience the power of AI-generated book summaries with our Book Summarizer tool. Harnessing the capabilities of ChatGPT, our tool provides concise and insightful summaries of books. Whether you're a busy reader seeking quick overviews or a researcher looking to gather key points, our Book Summarizer has got you covered.

    But that's not all. We go beyond text and incorporate the visual realm with the help of DALL-E and Stability AI. Our tool generates captivating image prompts related to the book content, adding an immersive and visually stimulating element to your reading experience.

    Unlock the potential of AI-driven book summarization and visual enhancement with our Book Summarizer tool. Start exploring the world of knowledge in a whole new way.
    """
about_content = "\n".join([line for line in ABOUT.splitlines() if line.strip()])


st.set_page_config(
    page_icon="📚",
    page_title=TITLE,
    layout="wide",
    initial_sidebar_state="auto",
    menu_items={"About": f"{TITLE}{about_content}"},
)

with st.sidebar:
    st.title(TITLE)
    st.markdown(ABOUT)
    add_vertical_space(2)
    st.write("💡 Note: API keys required!!")


if "authentication_status" not in st.session_state:
    st.session_state.authentication_status = ""

if st.session_state.authentication_status:

    def input_form():
        st.sidebar.markdown("**Stable Diffusion**")

        size = st.sidebar.select_slider(
            "Image Size",
            (
                "896x512",
                "768x512",
                "683x512",
                "640x512",
                "512x512",
                "512x640",
                "512x683",
                "512x768",
                "512x896",
            ),
            value="512x512",
        )

        width, height = map(int, size.split("x"))

        book_art_samples = st.sidebar.slider("Samples", 0, 10, 2, 1)
        book_art_steps = st.sidebar.slider("Steps", 30, 100, 30, 1)
        book_art_engine = st.sidebar.selectbox(
            "Engine",
            (
                "stable-diffusion-v1-5",
                "stable-diffusion-512-v2-1",
                "stable-diffusion-768-v2-1",
                "stable-diffusion-xl-beta-v2-2-2",
            ),
            3,
        )

        with st.form("Book", clear_on_submit=True):
            text_input = st.text_input(
                "Submit a Book to Summarize or Leave Empty for a Random Book:",
                value="",
            )
            text_input_button = st.form_submit_button("Submit")
            add_vertical_space(1)

        if text_input_button:
            summarizer(
                text_input,
                width,
                height,
                book_art_engine,
                book_art_samples,
                book_art_steps,
            )
            display_book_summaries_and_save_to_database(1)

    ### Option to use Local File Storage ###
    # def display_book_summaries():
    #     post_folders = os.listdir(BOOK_FOLDER)
    #     # Sort the folders by their last modified timestamp in descending order
    #     sorted_folders = sorted(
    #         post_folders,
    #         key=lambda x: os.path.getmtime(os.path.join(BOOK_FOLDER, x)),
    #         reverse=True,
    #     )
    #     for post_folder in sorted_folders:
    #         post_folder_path = os.path.join(BOOK_FOLDER, post_folder)
    #         text_file = os.path.join(post_folder_path, f"{post_folder}.txt")
    #         dalle_image = os.path.join(post_folder_path, f"{post_folder}_dalle_0.png")
    #         stability_image = os.path.join(
    #             post_folder_path, f"{post_folder}_stability_0.png"
    #         )

    #         # Read the title from the file name
    #         title = post_folder.replace("_", " ")

    #         with st.expander(title):
    #             # Display the images next to each other
    #             col1, col2 = st.columns(2)
    #             with col1:
    #                 st.image(dalle_image, caption="DALL-E Image")
    #             with col2:
    #                 st.image(stability_image, caption="Stability AI Image")

    #             # Display the title
    #             st.title(title)

    #             # Read the text from the file
    #             with open(text_file, "r") as f:
    #                 text = f.read()

    #             # Display the text
    #             st.write(text)
    #         # st.markdown("---")

    # Run the app
    if __name__ == "__main__":
        input_form()
        fetch_all_books()
