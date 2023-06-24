import streamlit as st
from streamlit_extras.add_vertical_space import add_vertical_space
import dropbox
from dropbox.exceptions import AuthError
import database as db
import _writer as wr
import _artist as ar
import cloud as cl
import re


EBOOK_FOLDER = "ebooks"

TITLE = "Chapter Master"
ABOUT = """
    Chapter Master is an advanced AI tool powered by ChatGPT and Stable Diffusion. With Chapter Master, you can effortlessly create, title, and outline your book, chapter by chapter. This innovative tool also generates captivating image prompts to enhance your storytelling.

    ✍️ Write with Ease:
    Let ChatGPT assist you in crafting engaging chapters for your book. From writing the story arc to outlining key plot points, Chapter Master streamlines the writing process and fuels your creativity.

    🎨 Stunning Visuals:
    Enrich your book with visually stunning cover art and captivating images for each chapter. Thanks to Stable Diffusion, Chapter Master offers a seamless integration of visual artistry into your storytelling experience.

    Whether you're an aspiring author or a seasoned writer, Chapter Master empowers you to bring your book to life, making the writing journey smoother and more immersive than ever before. Unleash your creativity and unlock the full potential of your storytelling with Chapter Master.
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
if "steps" not in st.session_state:
    st.session_state.steps = 30
if "samples" not in st.session_state:
    st.session_state.samples = 2
if "engine" not in st.session_state:
    st.session_state.engine = ""
if "width" not in st.session_state:
    st.session_state.width = 512
if "height" not in st.session_state:
    st.session_state.height = 512
if "num_of_chapters" not in st.session_state:
    st.session_state.num_of_chapters = 0

if st.session_state.authentication_status:
    st.sidebar.markdown("Stable Diffusion Settings")

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

    st.session_state.width, st.session_state.height = map(int, size.split("x"))

    st.session_state.samples = st.sidebar.slider("Samples", 0, 10, 2, 1)
    st.session_state.steps = st.sidebar.slider("Steps", 30, 100, 50, 1)
    st.session_state.engine = st.sidebar.selectbox(
        "Engine",
        (
            "stable-diffusion-v1-5",
            "stable-diffusion-512-v2-1",
            "stable-diffusion-768-v2-1",
            "stable-diffusion-xl-beta-v2-2-2",
        ),
        3,
    )

    # Selectbox for book to read or write a new one
    all_written_ebooks = ("Write a New eBook",) + db.fetch_all_ebook_titles()
    ebook_to_write = st.selectbox("Choose an eBook to Write:", all_written_ebooks, 0)
    if ebook_to_write == "Write a New eBook":
        new_topic = st.form("New eBook")
        with new_topic:
            # Generate new Title and Outline for the book
            user_input_text = st.text_input("Enter a topic for the eBook: ")
            user_input_button = st.form_submit_button("Submit")
            if user_input_button:
                st.sidebar.info("Brainstormin Title Options...")
                ebook_title = wr.new_ebook(user_input_text)
                st.sidebar.success(ebook_title)
                st.sidebar.info("Writing Book Outline...")
                ebook_table_of_contet = wr.table_of_content(
                    ebook_title, user_input_text
                )
                st.sidebar.success("Table of Contents is ready!")
                st.experimental_rerun()

    else:
        # Choose an existig book to read or continue writing
        ebook_title = ebook_to_write
        current_table_of_content = db.get_table_of_content(ebook_title)
        if current_table_of_content:
            # Create expander for the Table of content
            table_of_content_expander = st.expander("Table of Content")
            with table_of_content_expander:
                # Load book cover urls from database
                urls = db.get_ebook_cover(ebook_title)
                # Display the urls in two columns
                if urls:
                    col1, col2 = st.columns(2)  # Create two columns
                    for j, cover_url in enumerate(urls):
                        # Extract the caption from the image_url
                        match = re.search(r"_(\w+)_\d+\.png", cover_url)
                        caption = match.group(1) if match else ""

                        # Determine the column to display the image based on the index
                        column = col1 if j % 2 == 0 else col2

                        # Display the image with the extracted caption
                        with column:
                            st.image(cover_url, caption=caption)

                # Display cover arts
                is_cover_prompt = db.get_cover_prompt(ebook_title)
                if is_cover_prompt:
                    st.markdown(is_cover_prompt)
                add_vertical_space(1)
                # Display the Table of content
                st.markdown(current_table_of_content)
                add_vertical_space(1)

                # Button to generate Cover image drawed from the book Outline
                cover_art_button = st.button("Generate Cover Art")
                if cover_art_button:
                    cover_prompt = ar.get_image_prompt(current_table_of_content)
                    dalle_image = ar.create_dalle_image(
                        cover_prompt, st.session_state.samples, dalle_num=False
                    )
                    stable_image = ar.create_stable_image(
                        cover_prompt,
                        st.session_state.width,
                        st.session_state.height,
                        st.session_state.engine,
                        st.session_state.samples,
                        st.session_state.steps,
                    )
                    # Save cover images to the cloud storage
                    ar.save_chapter_img(
                        ebook_title, "Cover", dalle_image, stable_image, dalle_num=False
                    )

                    # Save cover prompt and urls to database
                    db.insert_cover_prompt(ebook_title, cover_prompt)
                    cl.display_files_and_save_to_database(ebook_title, "Cover")
                    st.experimental_rerun()

            # Display all the already written chapters
            selected_ebook = db.db_ebook.get(ebook_title)
            chapters = []
            for key, value in selected_ebook.items():
                if key.startswith("chapter_"):
                    chapters.append(value)
                    chapter = key.replace("_", " ").capitalize()
                    chapter_expander = st.expander(chapter)
                    with chapter_expander:
                        # Display all the chapter images with 2 columns
                        urls = db.get_chapter_art(ebook_title, chapter)

                        if urls:
                            col1, col2 = st.columns(2)  # Create two columns
                            for j, cover_url in enumerate(urls):
                                # Extract the caption from the image_url
                                match = re.search(r"_(\w+)_\d+\.png", cover_url)
                                caption = match.group(1) if match else ""

                                # Determine the column to display the image based on the index
                                column = col1 if j % 2 == 0 else col2

                                # Display the image with the extracted caption
                                with column:
                                    st.image(cover_url, caption=caption)

                        # Display chapter arts
                        is_chapter_prompt = db.get_chapter_prompt(ebook_title, chapter)
                        if is_chapter_prompt:
                            st.markdown(is_chapter_prompt)
                        add_vertical_space(1)
                        # Display the chapter text
                        st.markdown(value)
                        add_vertical_space(2)

                        # Button for the Chapter images
                        chapter_art_button = st.button(f"Generate {chapter} Art")
                        if chapter_art_button:
                            chapter_prompt = ar.get_image_prompt(value)
                            dalle_image = ar.create_dalle_image(
                                chapter_prompt,
                                st.session_state.samples,
                                dalle_num=False,
                            )
                            stable_image = ar.create_stable_image(
                                chapter_prompt,
                                st.session_state.width,
                                st.session_state.height,
                                st.session_state.engine,
                                st.session_state.samples,
                                st.session_state.steps,
                            )
                            # Save Chapter images to the cloud storage
                            ar.save_chapter_img(
                                ebook_title,
                                chapter,
                                dalle_image,
                                stable_image,
                                dalle_num=False,
                            )

                            # Save cthe Chapter prompt and image urls to database
                            db.insert_image_prompt(ebook_title, chapter, chapter_prompt)
                            cl.display_files_and_save_to_database(ebook_title, chapter)
                            st.experimental_rerun()

        # Insert form to write new chapter
        new_chapter = st.form("New Chapter")
        with new_chapter:
            chapter_input = st.text_area("Copy and Paste a Chapter to Write:")
            # Button to write the given chapter
            chapter_input_button = st.form_submit_button("Submit")
            if chapter_input_button:
                st.sidebar.info("Writing the chapter...")
                write_new_chapter = wr.write_chapter(
                    ebook_title,
                    len(chapters) + 1,
                    current_table_of_content,
                    chapter_input,
                )
                st.sidebar.success(f"Chapter {len(chapters) + 1} written!")
                st.cache_data.clear()
                st.experimental_rerun()
