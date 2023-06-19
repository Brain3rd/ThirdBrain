import streamlit as st
from streamlit_chat import message
from streamlit_extras.colored_header import colored_header
from streamlit_extras.add_vertical_space import add_vertical_space
from hugchat import hugchat
from hugchat.login import Login
from environment import load_env_variables, get_api_key
import streamlit_authenticator as stauth
import database as db


TITLE = "HugChat"
ABOUT = """
Welcome to the HugChat App, an innovative chatbot experience powered by the LLM model. Our chatbot, HugChat, utilizes the advanced capabilities of the OpenAssistant/oasst-sft-6-llama-30b-xor LLM model to provide intelligent and interactive conversations.

Engage in natural and meaningful dialogues with HugChat, as it leverages the power of language processing and understanding to deliver a personalized chat experience. Whether you're looking for information, friendly conversation, or even a virtual shoulder to lean on, HugChat is here to provide a warm and empathetic interaction.

Immerse yourself in the world of conversational AI with the HugChat App. Connect with HugChat today and discover the fascinating possibilities of LLM-powered chatbot technology. Engage, chat, and experience the future of human-like conversations.
"""

about_content = "\n".join([line for line in ABOUT.splitlines() if line.strip()])

st.set_page_config(
    page_icon="🤗",
    page_title=TITLE,
    layout="wide",
    initial_sidebar_state="auto",
    menu_items={"About": f"{TITLE}{about_content}"},
)

# Sidebar contents
with st.sidebar:
    st.title("🤗💬 HugChat App")
    st.markdown(ABOUT)
    add_vertical_space(2)
    st.write("💡 Note: No API key required!")

if "authentication_status" not in st.session_state:
    st.session_state.authentication_status = ""


users = db.fetch_all_users()
usernames = [user["key"] for user in users]
names = [user["name"] for user in users]
hashed_passwords = [user["password"] for user in users]


authenticator = stauth.Authenticate(
    names, usernames, hashed_passwords, "thirdbrain", "chocolate", cookie_expiry_days=20
)

name, st.session_state.authentication_status, username = authenticator.login(
    "Login", "main"
)


if st.session_state.authentication_status == False:
    st.error("Username / Password is Incorrect!")

if st.session_state.authentication_status == None:
    st.warning("Please enter you username and password")

if st.session_state.authentication_status:
    authenticator.logout("Logout", "sidebar")
    load_env_variables()
    # login
    HUGGING_EMAIL = get_api_key("HUGGING_EMAIL")
    HUGGING_PASSWORD = get_api_key("HUGGING_PASSWORD")

    sign = Login(HUGGING_EMAIL, HUGGING_PASSWORD)
    cookies = sign.login()
    sign.saveCookies()

    # Generate empty lists for generated and past.
    ## generated stores AI generated responses
    if "generated" not in st.session_state:
        st.session_state["generated"] = ["I'm HugChat, How may I help you?"]
    ## past stores User's questions
    if "past" not in st.session_state:
        st.session_state["past"] = ["Hi!"]

    # Layout of input/response containers
    response_container = st.container()
    colored_header(label="", description="", color_name="blue-30")
    input_container = st.container()

    # User input
    ## Function for taking user provided prompt as input
    def get_text():
        input_text = st.text_input("You: ", "", key="input")
        return input_text

    ## Applying the user input box
    with input_container:
        user_input = get_text()

    # Response output
    ## Function for taking user prompt as input followed by producing AI generated responses
    def generate_response(prompt):
        chatbot = hugchat.ChatBot(cookies=cookies.get_dict())
        response = chatbot.chat(prompt)
        return response

    ## Conditional display of AI generated responses as a function of user provided prompts
    with response_container:
        if user_input:
            response = generate_response(user_input)
            st.session_state.past.append(user_input)
            st.session_state.generated.append(response)

        if st.session_state["generated"]:
            for i in range(len(st.session_state["generated"])):
                message(st.session_state["past"][i], is_user=True, key=str(i) + "_user")
                message(st.session_state["generated"][i], key=str(i))
