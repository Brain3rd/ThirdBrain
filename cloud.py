import os
import streamlit as st
import dropbox
import math
from environment import load_env_variables, get_api_key
from database import insert_book, insert_art, insert_ebook_art


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


@st.cache_data()
def display_book_summaries_and_save_to_database(num_summaries=None):
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
        entry for entry in entries if isinstance(entry, dropbox.files.FolderMetadata)
    ]

    # Reverse the order of the books displayed
    folders.reverse()

    for folder in folders:
        folder_name = os.path.basename(folder.path_display).replace("_", " ")

        # Extract the title from the folder name
        if folder_name not in st.session_state["title"]:
            if folder_name != "books":
                st.session_state.title = str(folder_name)

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
        expander = st.expander(st.session_state.title)
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
                    elif isinstance(e.error, dropbox.exceptions.InternalServerError):
                        # Handle InternalServerError and continue to the next iteration
                        st.sidebar.error(
                            f"InternalServerError occurred for file {image_file.path_display}. Skipping..."
                        )
                        continue

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

                # Split the string by the delimiter "by"
                split_string = st.session_state.title.split("by")
                # Extract the author name (assuming it is the second part after splitting)
                author_name = split_string[1].strip()

                st.sidebar.info("Saving to database")
                insert_book(
                    st.session_state.title,
                    author_name,
                    st.session_state.file_content,
                    image_urls,
                )
                st.sidebar.success("Database updated!")
                st.cache_data.clear()
                st.experimental_rerun()

        # Break the loop if the specified number of summaries is reached
        if num_summaries is not None and len(st.session_state.audio) >= num_summaries:
            break


@st.cache_data()
def display_art_and_save_to_database(num_art=None):
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
        art_folder_name = os.path.basename(art_folder.path_display).replace("_", " ")

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

                st.sidebar.info("Saving to database")
                insert_art(
                    st.session_state.art_title,
                    st.session_state.art_file_content,
                    art_image_urls,
                )

                st.sidebar.success("Database updated!")
                st.cache_data.clear()
                st.experimental_rerun()

        # Break the loop if the specified number of summaries is reached
        if num_art is not None and len(st.session_state.art_prompt) >= num_art:
            break


@st.cache_data()
def display_files_and_save_to_database(ebook_title, chapter):
    try:
        # List all files and folders in the /books folder of Dropbox
        all_art = dbx.files_list_folder(f"/ebooks/{ebook_title}", recursive=True)
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
        art_folder_name = os.path.basename(art_folder.path_display).replace("_", " ")

        # Extract the title from the folder name

        art_title = str(art_folder_name)
        if art_title == chapter:
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

            art_image_urls = []

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

            insert_ebook_art(ebook_title, chapter, art_image_urls)
