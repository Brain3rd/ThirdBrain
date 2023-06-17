from dotenv import load_dotenv
import os
import streamlit as st
from streamlit_extras.add_vertical_space import add_vertical_space
from _summarizer import summarizer
import dropbox
from dropbox.exceptions import AuthError

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


if "authentication_status" not in st.session_state:
    st.session_state.authentication_status = ""

if st.session_state.authentication_status:
    # Dropbox keys
    APP_KEY = st.secrets.APP_KEY
    APP_SECRET = st.secrets.APP_SECRET
    DROPBOX_REFRESH_TOKEN = st.secrets.DROPBOX_REFRESH_TOKEN
    dbx = dropbox.Dropbox(
        app_key=APP_KEY,
        app_secret=APP_SECRET,
        oauth2_refresh_token=DROPBOX_REFRESH_TOKEN,
    )

    with st.sidebar:
        st.title(TITLE)
        st.markdown(ABOUT)
        add_vertical_space(2)
        st.write("💡 Note: API key required!")

    def input_form():
        with st.form("Summarize Book", clear_on_submit=True):
            text_input = st.text_input(
                "Enter Book to Summarize or Leave Empty for Random Book",
                value="",
            )
            submit_button = st.form_submit_button("Submit")

        if submit_button:
            summarizer(text_input)
            # Clear the cache
            # st.cache_data.clear()
            st.cache_data.clear()

    @st.cache_data
    def display_book_summaries(num_summaries=None):
        if "title" not in st.session_state:
            st.session_state.title = ""
        if "image_url" not in st.session_state:
            st.session_state.image_url = ""
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
                st.session_state.title = folder_name

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

            # Display the images in the expander
            with expander:
                image_urls = []  # List to store the temporary links of all images

                for image_file in image_files:
                    # Get temporary link for the image file
                    res = dbx.files_get_temporary_link(image_file.path_display).link
                    image_urls.append(res)  # Add the temporary link to the list

                    # Display the image
                    st.image(
                        res,
                        caption=os.path.splitext(image_file.name)[0],
                    )

                if st.session_state.title not in st.session_state.url:
                    st.session_state.url[st.session_state.title] = []
                    st.session_state.url[st.session_state.title].extend(
                        image_urls
                    )  # Add all temporary links to the session state

            # Display the text file in the expander
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
                    st.write(st.session_state.file_content)

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
