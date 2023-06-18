from _artist import art_gerator
import streamlit as st
from streamlit_extras.add_vertical_space import add_vertical_space
from environment import load_env_variables, get_api_key
import dropbox
from dropbox.exceptions import AuthError
import os
import math


TITLE = "Photo Artist"
ABOUT = """
    Experience the power of AI-generated book summaries with our Book Summarizer tool. Harnessing the capabilities of ChatGPT, our tool provides concise and insightful summaries of books. Whether you're a busy reader seeking quick overviews or a researcher looking to gather key points, our Book Summarizer has got you covered.

    But that's not all. We go beyond text and incorporate the visual realm with the help of DALL-E and Stability AI. Our tool generates captivating image prompts related to the book content, adding an immersive and visually stimulating element to your reading experience.

    Unlock the potential of AI-driven book summarization and visual enhancement with our Book Summarizer tool. Start exploring the world of knowledge in a whole new way.
    """
about_content = "\n".join([line for line in ABOUT.splitlines() if line.strip()])

IMAGE_FOLDER = "images"

st.set_page_config(
    page_icon="🎨",
    page_title=TITLE,
    layout="wide",
    initial_sidebar_state="auto",
    menu_items={"About": f"{TITLE}{about_content}"},
)

with st.sidebar:
    st.title(TITLE)
    st.markdown(ABOUT)
    add_vertical_space(2)
    st.write("💡 Note: API key required!")


# Authentication
if "authentication_status" not in st.session_state:
    st.session_state.authentication_status = ""

if st.session_state.authentication_status:
    load_env_variables()
    # Dropbox keys
    APP_KEY = get_api_key("APP_KEY")
    APP_SECRET = get_api_key("APP_SECRET")
    DROPBOX_REFRESH_TOKEN = get_api_key("DROPBOX_REFRESH_TOKEN")
    dbx = dropbox.Dropbox(
        app_key=APP_KEY,
        app_secret=APP_SECRET,
        oauth2_refresh_token=DROPBOX_REFRESH_TOKEN,
    )

    def art_form():
        if "user_input" not in st.session_state:
            st.session_state.user_input = ""
        if "user_input_name" not in st.session_state:
            st.session_state.user_input_name = ""
        with st.form("Art", clear_on_submit=True):
            user_input = st.text_area(
                "Enter a description of an art to generate:",
                value="",
            )
            user_input_button = st.form_submit_button("Submit")
        if user_input_button:
            st.session_state.user_input = user_input
            st.sidebar.info(st.session_state.user_input)
            # print(st.session_state.user_input)

        with st.form("Art name", clear_on_submit=True):
            user_input_name = st.text_input("Name your Art", value="")
            user_input_name_button = st.form_submit_button("Submit")

        if user_input_name_button:
            st.session_state.user_input_name = user_input_name
            # print(st.session_state.user_input)
            # print(st.session_state.user_input_name)
            st.sidebar.info(st.session_state.user_input_name)
            art_gerator(st.session_state.user_input, st.session_state.user_input_name)
            st.cache_data.clear()

    @st.cache_data()
    def display_art(num_art=None):
        if "art_url" not in st.session_state:
            st.session_state.art_url = {}
        if "art_title" not in st.session_state:
            st.session_state.art_title = ""
        if "art_prompt" not in st.session_state:
            st.session_state.art_prompt = {}

        try:
            # List all files and folders in the /books folder of Dropbox
            all_art = dbx.files_list_folder("/images", recursive=True)
            art_entries = all_art.entries
        except dropbox.exceptions.AuthError as e:
            # Handle authentication error
            st.error(f"Dropbox authentication failed: {e}")
            return

        # Filter out folders from the entries
        art_folders = [
            art_entry
            for art_entry in art_entries
            if isinstance(art_entry, dropbox.files.FolderMetadata)
        ]

        # Reverse the order of the books displayed
        art_folders.reverse()

        for art_folder in art_folders:
            art_folder_name = os.path.basename(art_folder.path_display).replace(
                "_", " "
            )

            # Extract the title from the folder name
            if art_folder_name not in st.session_state["art_title"]:
                if art_folder_name != "images":
                    st.session_state.art_title = str(art_folder_name)

            expander = st.expander(st.session_state.art_title)

            # Get the files inside the folder
            art_folder_files = [
                art_entry
                for art_entry in art_entries
                if isinstance(art_entry, dropbox.files.FileMetadata)
                and os.path.dirname(art_entry.path_display) == art_folder.path_display
            ]

            # Separate image files and text file
            art_image_files = [
                file for file in art_folder_files if file.path_display.endswith(".png")
            ]
            art_text_file = [
                file for file in art_folder_files if file.path_display.endswith(".txt")
            ]

            # Calculate the number of columns needed for the images
            num_images = len(art_image_files)
            num_columns = 2  # Number of columns for the images
            num_rows = math.ceil(num_images / num_columns)

            # Display the images in two columns
            with expander:
                art_image_urls = []  # List to store the temporary links of all images

                col1, col2 = st.columns(2)  # Create two columns

                for i, art_image_file in enumerate(art_image_files):
                    # Get temporary link for the image file
                    art_res = dbx.files_get_temporary_link(
                        art_image_file.path_display
                    ).link
                    art_image_urls.append(art_res)  # Add the temporary link to the list

                    # Determine the column to display the image based on the index
                    if i % num_columns == 0:
                        column = col1
                    else:
                        column = col2

                    # Display the image in the respective column
                    with column:
                        st.image(
                            art_res,
                            caption=os.path.splitext(art_image_file.name)[0],
                        )

                if st.session_state.art_title not in st.session_state.art_url:
                    st.session_state.art_url[st.session_state.art_title] = []
                    st.session_state.art_url[st.session_state.art_title].extend(
                        art_image_urls
                    )  # Add all temporary links to the session state

            # Display the text files without columns
            with expander:
                for art_txt_file in art_text_file:
                    # Download the file content
                    _, art_res = dbx.files_download(art_txt_file.path_display)
                    st.session_state.art_file_content = art_res.content.decode("utf-8")

                    # Store title and prompt content in st.session_state.art_prompt.art_propmt
                    st.session_state.art_prompt[
                        st.session_state.art_title
                    ] = st.session_state.art_file_content

                    # Display the text
                    st.title(st.session_state.art_title)
                    st.write(st.session_state.art_file_content)
            # Break the loop if the specified number of summaries is reached
            if num_art is not None and len(st.session_state.audio) >= num_art:
                break

    art_form()
    display_art()
