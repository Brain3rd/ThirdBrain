import os
import streamlit as st
from streamlit_extras.add_vertical_space import add_vertical_space
from _summarizer import summarizer
import dropbox
from dropbox.exceptions import AuthError
import math
from environment import load_env_variables, get_api_key


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

    def input_form():
        width = st.sidebar.select_slider("Image Width", (512, 640, 683, 768, 896))
        height = st.sidebar.select_slider("Image Height", (512, 640, 683, 768, 896))
        engine = st.sidebar.selectbox(
            "Engine",
            (
                "stable-diffusion-v1-5",
                "stable-diffusion-512-v2-1",
                "stable-diffusion-768-v2-1",
                "stable-diffusion-xl-beta-v2-2-2",
            ),
        )
        with st.form("Summarize Book", clear_on_submit=True):
            text_input = st.text_input(
                "Enter Book to Summarize or Leave Empty for Random Book",
                value="",
            )
            submit_button = st.form_submit_button("Submit")

        if submit_button:
            st.cache_data.clear()
            summarizer(text_input, width, height, engine)

    @st.cache_data()
    def display_book_summaries(num_summaries=None):
        if "title" not in st.session_state:
            st.session_state.title = ""
        if "audio" not in st.session_state:
            st.session_state.audio = {}
        if "url" not in st.session_state:
            st.session_state.url = {}

        try:
            # List all files and folders in the /books folder of Dropbox
            result = dbx.files_list_folder("/books", recursive=True)
            entries = result.entries
        except dropbox.exceptions.AuthError as e:
            # Handle authentication error
            st.error(f"Dropbox authentication failed: {e}")
            return

        # Filter out folders from the entries
        folders = [
            entry
            for entry in entries
            if isinstance(entry, dropbox.files.FolderMetadata)
        ]

        # Reverse the order of the books displayed
        folders.reverse()

        for folder in folders:
            folder_name = os.path.basename(folder.path_display).replace("_", " ")

            # Extract the title from the folder name
            if folder_name not in st.session_state["title"]:
                if folder_name != "books":
                    st.session_state.title = str(folder_name)

            expander = st.expander(st.session_state.title)

            # Get the files inside the folder
            folder_files = [
                entry
                for entry in entries
                if isinstance(entry, dropbox.files.FileMetadata)
                and os.path.dirname(entry.path_display) == folder.path_display
            ]

            # Separate image files and text file
            image_files = [
                file for file in folder_files if file.path_display.endswith(".png")
            ]
            text_file = [
                file for file in folder_files if file.path_display.endswith(".txt")
            ]

            # Calculate the number of columns needed for the images
            num_images = len(image_files)
            num_columns = 2  # Number of columns for the images
            num_rows = math.ceil(num_images / num_columns)

            # Display the images in two columns
            with expander:
                image_urls = []  # List to store the temporary links of all images

                col1, col2 = st.columns(2)  # Create two columns

                for i, image_file in enumerate(image_files):
                    try:
                        shared_link_metadata = dbx.sharing_create_shared_link_with_settings(
                            image_file.path_display,
                            dropbox.sharing.SharedLinkSettings(
                                requested_visibility=dropbox.sharing.RequestedVisibility.public
                            ),
                        )
                    except dropbox.exceptions.ApiError as e:
                        if e.error.is_shared_link_already_exists():
                            # A shared link already exists, retrieve the existing links for the file
                            links = dbx.sharing_list_shared_links(
                                image_file.path_display
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
                    res = shared_link_url.replace(
                        "www.dropbox.com", "dl.dropboxusercontent.com"
                    ).split("?")[0]

                    # Add the permanent link to the list
                    image_urls.append(res)

                    # Determine the column to display the image based on the index
                    if i % num_columns == 0:
                        column = col1
                    else:
                        column = col2

                    # Display the image in the respective column
                    with column:
                        st.image(
                            res,
                            caption=os.path.splitext(image_file.name)[0],
                        )

                if st.session_state.title not in st.session_state.url:
                    st.session_state.url[st.session_state.title] = []
                    st.session_state.url[st.session_state.title].extend(
                        image_urls
                    )  # Add all temporary links to the session state

            # Display the text files without columns
            with expander:
                for txt_file in text_file:
                    # Download the file content
                    _, res = dbx.files_download(txt_file.path_display)
                    st.session_state.file_content = res.content.decode("utf-8")

                    # Store title and file content in st.session_state.audio
                    st.session_state.audio[
                        st.session_state.title
                    ] = st.session_state.file_content

                    # Display the text
                    st.title(st.session_state.title)
                    st.markdown(st.session_state.file_content)

            # Break the loop if the specified number of summaries is reached
            if (
                num_summaries is not None
                and len(st.session_state.audio) >= num_summaries
            ):
                break

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
        display_book_summaries()
