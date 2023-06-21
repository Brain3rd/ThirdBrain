from _artist import art_generator
import streamlit as st
from streamlit_extras.add_vertical_space import add_vertical_space
from environment import load_env_variables, get_api_key
import dropbox
from dropbox.exceptions import AuthError
import os
import math
import streamlit_authenticator as stauth
import database as db


TITLE = "Photo Artist"
ABOUT = """
    Welcome to Photo Artist, where creativity meets artificial intelligence. Our innovative platform harnesses the power of ChatGPT, Stable Diffusion, and DALL-E to create captivating art experiences.

    With Photo Artist, you can input your artistic ideas, and ChatGPT will generate a written textual representation of your vision. This unique collaboration between human imagination and AI algorithms brings your ideas to life in a new and exciting way.

    But that's not all. We go beyond words and venture into the realm of visuals. Through the integration of Stable Diffusion and DALL-E, our platform transforms those textual representations into breathtaking images. Prepare to be amazed as your artistic concepts materialize into stunning visuals.

    Unleash your creativity with Photo Artist and witness the synergy of AI and human imagination. Explore the possibilities, immerse yourself in the realm of art, and discover the beauty of AI-assisted creation. Start your artistic journey today and experience the magic of our platform.
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
    add_vertical_space(1)
    st.write("💡 Note: API key required!")


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

        st.markdown("Stable Diffusion Settings")

        size = st.select_slider(
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

        samples = st.slider("Samples", 0, 10, 2, 1)
        steps = st.slider("Steps", 30, 100, 50, 1)
        engine = st.selectbox(
            "Engine",
            (
                "stable-diffusion-v1-5",
                "stable-diffusion-512-v2-1",
                "stable-diffusion-768-v2-1",
                "stable-diffusion-xl-beta-v2-2-2",
            ),
            3,
        )
        add_vertical_space(1)
        user_input_name = st.text_input(
            "**Name your Art:**",
            value="",
        )

        with st.form("Art", clear_on_submit=True):
            user_input = st.text_area(
                "Enter a description of an art to generate:",
                value="",
            )
            user_input_button = st.form_submit_button("Submit")
            add_vertical_space(1)
        if user_input_button:
            st.cache_data.clear()
            st.session_state.user_input = user_input
            st.sidebar.info(st.session_state.user_input)
            st.session_state.user_input_name = user_input_name
            st.sidebar.info(st.session_state.user_input_name)
            art_generator(
                st.session_state.user_input,
                st.session_state.user_input_name,
                width,
                height,
                engine,
                samples,
                steps,
            )

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

            expander = st.expander(st.session_state.art_title, expanded=False)

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
                    # Get shared link for the image file
                    try:
                        shared_link_metadata = dbx.sharing_create_shared_link_with_settings(
                            art_image_file.path_display,
                            dropbox.sharing.SharedLinkSettings(
                                requested_visibility=dropbox.sharing.RequestedVisibility.public
                            ),
                        )
                    except dropbox.exceptions.ApiError as e:
                        if e.error.is_shared_link_already_exists():
                            # A shared link already exists, retrieve the existing links for the file
                            links = dbx.sharing_list_shared_links(
                                art_image_file.path_display
                            ).links
                            shared_link_metadata = links[
                                0
                            ]  # Assuming there is only one existing link, you can modify this logic based on your requirements
                        else:
                            # Handle other types of ApiError if needed
                            raise e

                    # Extract the URL from the shared link metadata
                    shared_link_url = shared_link_metadata.url

                    # Modify the shared link URL to force file download
                    art_res = shared_link_url.replace(
                        "www.dropbox.com", "dl.dropboxusercontent.com"
                    ).split("?")[0]

                    # Add the permanent link to the list
                    art_image_urls.append(art_res)

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
                    st.markdown(st.session_state.art_file_content)
            # Break the loop if the specified number of summaries is reached
            if num_art is not None and len(st.session_state.audio) >= num_art:
                break

    art_form()
    display_art()
