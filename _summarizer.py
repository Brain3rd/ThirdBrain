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


def read_file_contents():
    try:
        # List all files and folders in the /books folder of Dropbox
        result = dbx.files_list_folder("/books", recursive=True)
        entries = result.entries
    except dropbox.exceptions.AuthError as e:
        # Handle authentication error
        # st.error(f"Dropbox authentication failed: {e}")
        return

    # Filter out folders from the entries
    folders = [
        entry for entry in entries if isinstance(entry, dropbox.files.FolderMetadata)
    ]

    all_folders = []
    for folder in folders:
        folder_name = os.path.basename(folder.path_display).replace("_", " ")
        if folder_name == "books":
            pass
        else:
            all_folders.append(folder_name)

    return all_folders


all_books = read_file_contents()


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


def get_book(books):
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
                As a seasoned artist and photographer, you possess extensive expertise and skill honed over the years. Your journey has been filled with invaluable experiences, where you've embraced failures as valuable lessons and triumphed in your pursuit of capturing breathtaking visuals.
                """,
                    },
                    {
                        "role": "user",
                        "content": f"Generate a short textual representation of an image using keywords from the book summary: {summary}",
                    },
                    {
                        "role": "assistant",
                        "content": """
                    Generate a short written depiction of the book's essence by incorporating key terms extracted from the provided summary. Emphasize the visual mood, theme, and genre of the book. Consider a suitable color scheme that aligns with the intended atmosphere. Use evocative language to describe visuals that reflect the plot, themes, or significant elements of the book. Image should not contain any written text.

Creating Breathtaking Visuals example prompts: 

1. Portrait photo of an elderly Asia old warrior chief with tribal panther makeup. Use blue on red colors, capture a side profile with the chief looking away. Focus on the serious eyes. Utilize a 50mm lens for portrait photography and incorporate hard rim lighting techniques. (Beta, AR 2:3, Upbeta)

2. Take a portrait photo of Keanu Reeves as an Asia old warrior chief with tribal panther makeup. Use blue on red colors, capture a side profile with Keanu looking away. Focus on his serious eyes. Utilize a 50mm lens for portrait photography and incorporate hard rim lighting techniques. (Beta, AR 2:3, Upbeta)

3. Portrait photo of an African old warrior chief with tribal panther makeup. Use gold on white colors, capture a side profile with the chief looking away. Focus on the serious eyes. Utilize a 50mm lens for portrait photography and incorporate hard rim lighting techniques. (Beta, AR 2:3)

4. Take a portrait photo of a 68-year-old man in blue robes, emphasizing his role as a priest. Capture the essence of National Geographic with a portrait that showcases his age and wisdom. Utilize natural light and a 50mm lens for a detailed and impactful photo. (S 625, Q 2, IW 3)

5. Capture an ultrarealistic portrait of a native American old woman with cinematic lighting. Aim for an award-winning photo with no color, emphasizing black and white tones. Utilize an 80mm lens to capture the intricate details and create a powerful image. (Beta, Upbeta)

6. Take a headshot portrait photo in the style of Mucha. Focus on rendering a sharp and elegant image using the Octane render technique. Aim for detailed and award-winning photography that stands out as a masterpiece. Experiment with rim lighting to add drama. (Rim lit, perfect focus)

7. Create a vibrant professional studio portrait of a young goth woman with piercing green eyes. Aim for an attractive, casual, and friendly look while adding dramatic lighting effects. Capture the essence of a femme fatale with a gold ankh necklace. Strive for an award-winning image that impresses with its groundbreaking aesthetic. (Testp, AR 3:4, Upbeta)

8. Capture a medium shot side profile portrait photo of Takeshi Kaneshiro as a warrior chief. Use blue on red colors with tribal panther makeup. Make sure he is looking away with serious eyes. Utilize a 50mm lens and incorporate hard rim lighting techniques for an impactful image. (AR 2:3, Beta, Upbeta)

9. Take a stunning photo of a gorgeous young Swiss girl sitting by a window with headphones on. She should be wearing a white bra with a translucent shirt over it. Focus on her soft lips and beach blonde hair. Use octane render or Unreal Engine to create a photorealistic and highly detailed image. (AR 9:16, S 5000, Testp, Upbeta)

10. Capture a portrait photo of an old man named Tattles as he cries while sitting on a bed with gauges in his ears. Capture him looking away with serious eyes. Utilize a 50mm lens for portrait photography and incorporate hard rim lighting techniques. Capture the raw emotions in the image. (AR 2:3, Beta, Upbeta)

These prompts will guide you in creating stunning and breathtaking visuals that showcase your unique style and expertise. Have fun experimenting with these ideas and further honing your skills as an artist and photographer.
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
        all_books.append(st.session_state.new_book)

    else:
        books = book_picker()
        st.session_state.new_book = get_book(books)

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
