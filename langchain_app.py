from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import StrOutputParser
from langchain.schema.runnable import Runnable
from langchain.schema.runnable.config import RunnableConfig
from langchain.memory import ConversationBufferMemory
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from operator import itemgetter

import chainlit as cl
memory = ConversationBufferMemory(return_messages=True)

@cl.on_chat_start
async def on_chat_start():
    await cl.Message(content="Coffee with Ai!").send()

@cl.on_chat_start
async def chat_start():
    model = ChatOpenAI(model="gpt-4-0125-preview", temperature=0.2, streaming=True)
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You're a very knowledgeable historian who provides accurate and eloquent answers to historical questions.",
        ),
        MessagesPlaceholder(variable_name="history"),
        (
            "human",
            "{question}"
        ),
    ])

    memory.load_memory_variables({})
    {'history': []}

    runnable = RunnablePassthrough.assign(history=RunnableLambda(memory.load_memory_variables) | itemgetter("history")) | prompt | model | StrOutputParser()

    cl.user_session.set("runnable", runnable)

@cl.on_message
async def on_message(message: cl.Message):
    Runable = cl.user_session.get("runnable")
    msg = cl.Message(content="")

    async for chunk in Runable.astream(
        {"question":message.content},
        config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
    ):
        await msg.stream_token(chunk)

    memory.save_context({"input":message.content}, {"output": msg.content})
    memory.load_memory_variables({})

    await msg.send()


@cl.password_auth_callback
def auth_callback(username: str, password: str):
    # Fetch the user matching username from your database
    # and compare the hashed password with the value stored in the database
    #print(username, password)
    print(type(username), type(password))
    if (username, password) == ("Trinabh", "tinu"):
        return cl.User(
            identifier="admin", metadata={"role": "admin", "provider": "credentials"}
        )
    else:
        return None
    