import os
import openai
from typing import List
import time
import requests
import base64
import dropbox
import streamlit as st


# Openai Keys
openai.api_key = st.secrets.OPENAI_API_KEY


# Stable.ai Keys
api_host = os.getenv("API_HOST", "https://api.stability.ai")
url = f"{api_host}/v1/user/account"
engine_id = "stable-diffusion-v1-5"
api_key = st.secrets.STABILITY_API_KEY
if api_key is None:
    raise Exception("Missing Stability API key.")


# Dropbox Keys
APP_KEY = st.secrets.APP_KEY
APP_SECRET = st.secrets.APP_SECRET
DROPBOX_REFRESH_TOKEN = st.secrets.DROPBOX_REFRESH_TOKEN


dbx = dropbox.Dropbox(
    app_key=APP_KEY, app_secret=APP_SECRET, oauth2_refresh_token=DROPBOX_REFRESH_TOKEN
)


# Looping parameters for error handling
MAX_ATTEMPTS = 2
DELAY_SECONDS = 10


def read_file_contents(file_name: str, encoding="utf-8") -> List[str]:
    with open(file_name, "r", encoding=encoding) as f:
        contents = f.read()
    return contents.splitlines()


all_books = set(read_file_contents("book_titles.txt"))


# Get random book
def book_picker():
    books = [
        {
            "role": "system",
            "content": f"""
            You are a professional life coach with great knowledge of charisma and leadership. Having witnessed a wide range of experiences, overcome challenges, and achieved success in life, you will choose books that teach users to better their lives.
        """,
        },
        {
            "role": "user",
            "content": f"""
        Give me a random book from all time best selling self help books.
        Different than these books:
        {all_books}
        """,
        },
        {
            "role": "assistant",
            "content": """
        Desired format:
        Book Title by Author Name

        Undesired format:
        "Book Title" by Aurhor name
        Book Title: Author name
        """,
        },
        {
            "role": "assistant",
            "content": """
        Give me just text in form of derired format, notthing else. No = or . or : either. 
        """,
        },
    ]
    return books


def get_book(books: List[dict], file_name: str, encoding="utf-8") -> str:
    st.sidebar.info("Selecting random book...")
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = openai.ChatCompletion.create(
                messages=books, model="gpt-3.5-turbo", max_tokens=50
            )
            book = (
                response["choices"][0]["message"]["content"]
                .replace(".", "")
                .replace("=", "")
                .replace(":", "")
                .replace("'", "")
                .replace(",", "")
                .replace('"', "")
            )
            # If the code execution is successful, break out of the loop
            break
        except Exception as e:
            # Handle RateLimitError
            st.sidebar.error(
                f"Attempt{attempt} failed. Rate limit exceeded. Error message: {e}\nWaiting a bit and trying again..."
            )
        # Wait for the specified delay before the next attempt
        time.sleep(DELAY_SECONDS)

    while book in all_books:
        try:
            # Book has already been selected, choose a different one
            st.sidebar.warning(
                "Oh, you've read this book already. Choosing a different book..."
            )

            response = openai.ChatCompletion.create(
                messages=[
                    {
                        "role": "system",
                        "content": f"""
                        You are a professional life coach with great knowledge of charisma and leadership. Having witnessed a wide range of experiences, overcome challenges, and achieved success in life, you will choose books that teach users to better their lives.
                    """,
                    },
                    {
                        "role": "user",
                        "content": f"""
                    I have read this book already, please give me a different book. NOT THESE BOOKS, PLEASE: {all_books}
                    """,
                    },
                    {
                        "role": "assistant",
                        "content": """
                    Desired format:
                    Book Title by Author Name

                    Undesired format:
                    "Book Title" by Aurhor name
                    Book Title: Author name
                    """,
                    },
                    {
                        "role": "assistant",
                        "content": """
                    Give me just text in form of derired format, notthing else. No = or . or : either. 
                    """,
                    },
                ],
                model="gpt-3.5-turbo",
                max_tokens=50,
            )
            book = (
                response["choices"][0]["message"]["content"]
                .replace(".", "")
                .replace("=", "")
                .replace(":", "")
                .replace("'", "")
                .replace(",", "")
                .replace('"', "")
            )
            # If the code execution is successful, break out of the loop
            break
        except Exception as e:
            # Handle RateLimitError
            st.sidebar.error(
                f"Attempt{attempt} failed. Rate limit exceeded. Error message: {e}\nWaiting a bit and trying again..."
            )
        # Wait for the specified delay before the next attempt
        time.sleep(DELAY_SECONDS)

    all_books.add(book)
    with open(file_name, "a", encoding=encoding) as f:
        f.write(f"{book}\n")

    st.sidebar.success(f"{book}")

    return book


def summarize_book(book: str) -> str:
    st.sidebar.info("Summarizing...")
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = openai.ChatCompletion.create(
                messages=[
                    {
                        "role": "system",
                        "content": """
                    You are a professional writer and book summarizer. To write effective content, both "perplexity" and "burstiness" are important. Perplexity assesses text complexity and burstiness evaluates sentence variation. People often write with a mix of long and short sentences, while machine-generated sentences tend to be uniform. You need to ensure a suitable balance of both perplexity and burstiness.

                    Remember that while summarizing, it's crucial to maintain the integrity of the author's ideas and voice. Use your own words to explain the concepts, but ensure that you capture the essence of the original content accurately.
                    """,
                    },
                    {
                        "role": "user",
                        "content": f"Summarize this book: {book}",
                    },
                    {
                        "role": "assistant",
                        "content": """
                    Desired format:
                    Introduction: Provide a brief overview of the book's purpose, author's background, and any relevant context.
                    Key points: Identify the main concepts or ideas presented in the book. Summarize each key point concisely and clearly. Use bullet points or numbered lists to organize the information.
                    Insights and Examples: Highlight the most insightful and impactful moments from the book. Explain how these insights can be applied in real-life situations. Provide relevant examples or anecdotes to illustrate the author's ideas.
                    Practical Application: Offer practical steps or strategies derived from the book's teachings. Describe how readers can implement the ideas in their own lives. Include actionable tips or exercises to reinforce the concepts.
                    Quotes: Select notable quotes from the author that encapsulate important concepts or provide inspiration. Use quotation marks and attribute the quotes to the author, "Quote" Author Name
                    Conclusion: Summarize the overall message of the book. Express your own thoughts and reflections on the book's content and potential impact.
                    """,
                    },
                ],
                model="gpt-3.5-turbo-16k",
            )
            # If the code execution is successful, break out of the loop
            break
        except Exception as e:
            # Handle RateLimitError
            st.sidebar.error(
                f"Attempt{attempt} failed. Rate limit exceeded. Error message: {e}\nWaiting a bit and trying again..."
            )
        # Wait for the specified delay before the next attempt
        time.sleep(DELAY_SECONDS)

    summary = response["choices"][0]["message"]["content"]

    st.sidebar.success("Book summarized!")

    return summary


def get_cover_prompt(summary):
    st.sidebar.info("Creating prompt for the images...")
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = openai.ChatCompletion.create(
                messages=[
                    {
                        "role": "system",
                        "content": """
                        You are a professional artist and book cover generator.
                        """,
                    },
                    {
                        "role": "user",
                        "content": f"""
                        Provide a short textual description of an cover image for the book. User will use it as a prompt to create DALL-E image. Here is summary of the book: {summary}
                        """,
                    },
                    {
                        "role": "assistant",
                        "content": """
                        Prompt should not exceed 300 characters. Image should not contain any written text or words. Reflect the mood, theme, and genre of the book. Select a color scheme that reflects the mood and theme of the book. Use visuals that relate to the book's plot, themes, or key elements.
                        """,
                    },
                ],
                model="gpt-3.5-turbo",
            )
            # If the code execution is successful, break out of the loop
            break
        except Exception as e:
            # Handle RateLimitError
            st.sidebar.error(
                f"Attempt{attempt} failed. Rate limit exceeded. Error message: {e}\nWaiting a bit and trying again..."
            )
        # Wait for the specified delay before the next attempt
        time.sleep(DELAY_SECONDS)

    image_prompt = response["choices"][0]["message"]["content"]

    st.sidebar.success("Image prompt created!")
    return image_prompt


def create_dalle_image(prompt):
    st.sidebar.info("Drawing DALL-E image...")
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            image_response = openai.Image.create(
                prompt=prompt,
                n=1,
                size="1024x1024",
                response_format="b64_json",  # Get image data instead of url
            )
            # If the code execution is successful, break out of the loop
            break
        except Exception as e:
            # Handle RateLimitError
            st.sidebar.error(
                f"Attempt{attempt} failed. Rate limit exceeded. Error message: {e}\nWaiting a bit and trying again..."
            )
        # Wait for the specified delay before the next attempt
        time.sleep(DELAY_SECONDS)

    # Return url instead of b64_json
    # image_url = image_response["data"][0]["url"]

    st.sidebar.success("DALL-E image created!")
    return image_response


def create_stable_image(prompt):
    st.sidebar.info("Drawing Stable image...")
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = requests.post(
                f"{api_host}/v1/generation/{engine_id}/text-to-image",
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "Authorization": f"Bearer {api_key}",
                },
                json={
                    "text_prompts": [{"text": f"{prompt}"}],
                    "cfg_scale": 7,
                    "clip_guidance_preset": "FAST_BLUE",
                    "height": 1024,
                    "width": 1024,
                    "samples": 1,
                    "steps": 30,
                },
            )

            if response.status_code != 200:
                data = "No stability book"
                st.sidebar.error("Stable not in a drawing mood today")
                raise Exception("Non-200 response: " + str(response.text))
            else:
                data = response.json()

            # If the code execution is successful, break out of the loop
            break
        except Exception as e:
            # Handle the specific exception (if known) or catch all exceptions
            st.sidebar.error(
                f"Attempt {attempt} failed. Error message: {str(e)}\nWaiting a bit and trying again..."
            )

        # Wait for the specified delay before the next attempt
        time.sleep(DELAY_SECONDS)

    st.sidebar.success("Stable image created!")

    return data


def save_all(new_book, book_content, dalle_data, stability_data):
    dalle_images = []
    stability_images = []

    try:
        # Create a new folder for the book in Dropbox
        folder_path = f"/books/{new_book}"

        # Check if the folder already exists
        try:
            dbx.files_get_metadata(folder_path)
        except dropbox.exceptions.ApiError as e:
            if (
                isinstance(e.error, dropbox.files.GetMetadataError)
                and e.error.is_path()
                and e.error.get_path().is_not_found()
            ):
                # Folder does not exist, create it
                dbx.files_create_folder(folder_path)
            else:
                # Unexpected error, raise it
                raise e

        # Save summary to txt file
        summary_path = f"{folder_path}/{new_book}.txt"
        summary_data = book_content.encode("utf-8")
        dbx.files_upload(summary_data, summary_path)

        # Save DALL-E images to png
        for i, image in enumerate(dalle_data["data"]):
            image_path = f"{folder_path}/{new_book}_dalle_{i}.png"
            image_data = base64.b64decode(image["b64_json"])
            dbx.files_upload(image_data, image_path)
            dalle_images.append(image_data)

        # Save Stability images to png
        if stability_data != "No stability book":
            for i, image in enumerate(stability_data["artifacts"]):
                image_path = f"{folder_path}/{new_book}_stability_{i}.png"
                image_data = base64.b64decode(image["base64"])
                dbx.files_upload(image_data, image_path)
                stability_images.append(image_data)

    except Exception as e:
        # Handle the specific exception (if known) or catch all exceptions
        st.sidebar.error(f"An error occurred while saving to Dropbox: {str(e)}")

    return dalle_images, stability_images


def summarizer(book_input=None) -> str:
    if "new_expander" not in st.session_state:
        st.session_state.new_expander = ""
    if "new_book" not in st.session_state:
        st.session_state.new_book = ""
    if "book_summary" not in st.session_state:
        st.session_state.book_summary = ""
    if "dalle_cover" not in st.session_state:
        st.session_state.dalle_cover = ""
    if "stable_cover" not in st.session_state:
        st.session_state.stable_cover = ""

    st.sidebar.info("Summarizanion progress started...")
    if book_input:
        st.session_state.new_book = book_input
        all_books.add(st.session_state.new_book)
        with open("book_titles.txt", "a", encoding="utf-8") as f:
            f.write(f"{st.session_state.new_book}\n")
    else:
        books = book_picker()
        st.session_state.new_book = get_book(books, "book_titles.txt")

    st.session_state.book_summary = summarize_book(st.session_state.new_book)
    book_content = f"{st.session_state.new_book}\n\n{st.session_state.book_summary}"

    dalle_prompt = get_cover_prompt(book_content)
    dalle_image = create_dalle_image(dalle_prompt)
    stable_image = create_stable_image(dalle_prompt)

    st.session_state.dalle_cover, st.session_state.stable_cover = save_all(
        st.session_state.new_book,
        st.session_state.book_summary,
        dalle_image,
        stable_image,
    )

    st.session_state.new_expander = st.expander(st.session_state.new_book)
    with st.session_state.new_expander:
        # Display DALL-E images
        for image_data in st.session_state.dalle_cover:
            st.image(image_data)

        # Display stability images
        for image_data in st.session_state.stable_cover:
            st.image(image_data)

        st.title(st.session_state.new_book)
        st.write(st.session_state.book_summary)

    st.sidebar.success("Book summarized!")


if __name__ == "__main__":
    summarizer()
