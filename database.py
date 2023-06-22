from deta import Deta
import streamlit as st
from environment import load_env_variables, get_api_key
import datetime
import re


load_env_variables()
DETA_KEY = get_api_key("DETA_KEY")
deta = Deta(DETA_KEY)

db_users = deta.Base("users_db")
db_books = deta.Base("books")
db_art = deta.Base("art")


### User Database ###
def insert_user(username, name, password):
    return db_users.put({"key": username, "name": name, "password": password})


def fetch_all_users():
    res = db_users.fetch()
    return res.items


def get_user(username):
    return db_users.get(username)


def update_user(username, updates):
    return db_users.update(updates, username)


def delete_user(username):
    return db_users.delete(username)


### Books Database ###
def insert_book(title, author, content, img_urls):
    current_date = datetime.date.today().strftime("%Y-%m-%d")
    db_books.put(
        {
            "key": title,
            "author": author,
            "content": content,
            "img_url": img_urls,
            "date": current_date,
        }
    )


def insert_art(title, content, img_urls):
    current_date = datetime.date.today().strftime("%Y-%m-%d")
    db_art.put(
        {
            "key": title,
            "content": content,
            "img_url": img_urls,
            "date": current_date,
        }
    )


@st.cache_data()
def fetch_all_books():
    all_books = db_books.fetch()
    response = all_books.items

    # Sort the books by date in descending order
    sorted_books = sorted(response, key=lambda x: x["date"], reverse=True)

    # Initialize empty lists to store the extracted information
    titles = []
    authors = []
    contents = []
    img_urls_list = []

    # Loop through the sorted books
    for book in sorted_books:
        title = book["key"]
        author = book["author"]
        content = book["content"]
        img_urls = book["img_url"]

        # Append the extracted values to the corresponding lists
        titles.append(title)
        authors.append(author)
        contents.append(content)
        img_urls_list.append(img_urls)

    # Loop through the extracted values for all books
    for i in range(len(titles)):
        title = titles[i]
        author = authors[i]
        content = contents[i]
        image_urls = img_urls_list[i]

        # Display the images in two columns
        expander = st.expander(
            title
        )  # Use the current book title for the expander title

        # Display the images in the expander
        with expander:
            col1, col2 = st.columns(2)  # Create two columns
            for j, image_url in enumerate(image_urls):
                # Extract the caption from the image_url
                match = re.search(r"_(\w+)_\d+\.png", image_url)
                caption = match.group(1) if match else ""

                # Determine the column to display the image based on the index
                column = col1 if j % 2 == 0 else col2

                # Display the image with the extracted caption
                with column:
                    st.image(image_url, caption=caption)

            # Display the title and content inside the expander
            st.title(title)
            st.markdown(content)


@st.cache_data()
def fetch_all_art():
    all_art = db_art.fetch()
    art_response = all_art.items

    # Sort the books by date in descending order
    sorted_art = sorted(art_response, key=lambda x: x["date"], reverse=True)

    # Initialize empty lists to store the extracted information
    art_titles = []
    art_contents = []
    art_img_urls_list = []

    # Loop through the sorted books
    for art in sorted_art:
        art_title = art["key"]
        art_content = art["content"]
        art_img_urls = art["img_url"]

        # Append the extracted values to the corresponding lists
        art_titles.append(art_title)
        art_contents.append(art_content)
        art_img_urls_list.append(art_img_urls)

    # Loop through the extracted values for all books
    for i in range(len(art_titles)):
        art_title = art_titles[i]
        art_content = art_contents[i]
        art_image_urls = art_img_urls_list[i]

        # Display the images in two columns
        expander = st.expander(
            art_title
        )  # Use the current book title for the expander title

        # Display the images in the expander
        with expander:
            col1, col2 = st.columns(2)  # Create two columns
            for j, art_image_url in enumerate(art_image_urls):
                # Extract the caption from the image_url
                match = re.search(r"_(\w+)_\d+\.png", art_image_url)
                caption = match.group(1) if match else ""

                # Determine the column to display the image based on the index
                column = col1 if j % 2 == 0 else col2

                # Display the image with the extracted caption
                with column:
                    st.image(art_image_url, caption=caption)

            # Display the title and content inside the expander
            st.title(art_title)
            st.markdown(art_content)
