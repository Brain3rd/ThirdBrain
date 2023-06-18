from environment import load_env_variables, get_api_key
import streamlit as st
from streamlit_chat import message
from streamlit_extras.colored_header import colored_header
from streamlit_extras.add_vertical_space import add_vertical_space
import openai
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.schema import HumanMessage, SystemMessage
from langchain.chains.conversation.memory import ConversationBufferWindowMemory

BOOK_FOLDER = "books"

TITLE = "ChatBot"
ABOUT = """
    Engage in dynamic conversations with our advanced Conversational ChatBot, powered by ChatGPT. Our ChatBot utilizes cutting-edge language technology, including Langchain and ChatGPT, to deliver interactive and natural interactions.

    With Langchain, our ChatBot understands and responds to a wide range of languages, breaking down communication barriers and fostering global connections. Whether you're looking for casual chat, information, or even language practice, our ChatBot is here to provide an immersive and engaging experience.

    Experience the future of conversational AI with ChatGPT and Langchain. Interact with our intelligent ChatBot and explore the limitless possibilities of natural language understanding and communication. Start a conversation today and see how our ChatBot can enrich your online experience.
    """

about_content = "\n".join([line for line in ABOUT.splitlines() if line.strip()])

st.set_page_config(
    page_icon="💬",
    page_title=TITLE,
    layout="wide",
    initial_sidebar_state="auto",
    menu_items={"About": f"{TITLE}{about_content}"},
)

with st.sidebar:
    st.title("ChatGPT")
    st.markdown(ABOUT)
    add_vertical_space(2)
    st.write("💡 Note: API key required!")

if "authentication_status" not in st.session_state:
    st.session_state.authentication_status = ""

if st.session_state.authentication_status:
    load_env_variables()
    openai.api_key = get_api_key("OPENAI_API_KEY")

    if "responses" not in st.session_state:
        st.session_state["responses"] = ["Hey Human"]
    ## past stores User's questions
    if "requests" not in st.session_state:
        st.session_state["requests"] = ["Hi ChatBot"]

    if "buffer_memory" not in st.session_state:
        st.session_state.buffer_memory = ConversationBufferWindowMemory(k=3)

    messages = [
        SystemMessage(
            content="I completely agree. In fact, research has shown that a balance of perplexity and burstiness can lead to higher reader engagement and retention. Perplexity can be measured using mathematical models such as language models, and burstiness can be evaluated using statistical analysis of sentence length variations. It's important to keep in mind that different types of content may require different levels of perplexity and burstiness, so it's important to tailor your writing style accordingly. Additionally, tools such as natural language processing and machine learning algorithms can help automate the process of optimizing perplexity and burstiness in written content."
        ),
        HumanMessage(
            content='To write effective content, both "perplexity" and "burstiness" are important. Perplexity assesses text complexity and burstiness evaluates sentence variation. People often write with a mix of long and short sentences, while machine-generated sentences tend to be uniform. You need to ensure a suitable balance of both perplexity and burstiness.'
        ),
    ]

    llm = ChatOpenAI(model_name="gpt-3.5-turbo")
    llm(messages)

    # Generate empty lists for GPT_generated and past.
    ## GPT_generated stores AI GPT_generated responses
    query_container = st.container()
    colored_header(label="", description="", color_name="blue-30")
    query = st.text_input("Query: ", key="input")

    conversation = ConversationChain(
        llm=llm,
        memory=st.session_state.buffer_memory,
        verbose=False,
    )

    with query_container:
        if query:
            response = conversation.run(query)
            st.session_state.requests.append(query)
            st.session_state.responses.append(response)

        if st.session_state["responses"]:
            for i in range(len(st.session_state["responses"])):
                message(
                    st.session_state["requests"][i], is_user=True, key=str(i) + "_user"
                )
                message(st.session_state["responses"][i], key=str(i))
