from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from memory import store_memory, retrieve_memory, is_duplicate, update_memory
from memory_extractor import extract_memory
import json
import os

load_dotenv(override=True)

llm = ChatOpenAI(model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"))

MAX_MEMORY = 20


def trim_memory(conversation_history, user_id):
    if len(conversation_history) > MAX_MEMORY:
        conversation_history = [conversation_history[0]] + conversation_history[1:][
            -MAX_MEMORY:
        ]
        user_conversations[user_id] = conversation_history


def extract_text_from_response(response):
    """
    Converts structured LLM response → clean string
    """

    # If already string
    if isinstance(response, str):
        return response

    # If dict like {"response": [...]}
    if isinstance(response, dict) and "response" in response:
        response = response["response"]

    # If list (your case)
    if isinstance(response, list):
        texts = []

        for item in response:
            if isinstance(item, dict):
                if item.get("type") == "text":
                    texts.append(item.get("text", ""))

        return "\n".join(texts)

    return str(response)


user_conversations = {}


def chat(user_id, user_input):
    # Create history for new user
    if user_id not in user_conversations:
        user_conversations[user_id] = [
            {"role": "system", "content": "You are a helpful AI assistant."}
        ]

    conversation_history = user_conversations[user_id]

    past_memories = retrieve_memory(user_id, user_input)
    memory_context = ""
    if past_memories:
        memory_context = "Relevant past memories:\n" + "\n".join(past_memories)

    conversation_history.append({"role": "user", "content": user_input})

    trim_memory(conversation_history, user_id)

    messages = conversation_history.copy()

    if memory_context:
        messages.insert(1, {"role": "system", "content": memory_context})
    tool = {"type": "web_search_preview"}

    llm_with_tools = llm.bind_tools([tool])

    response = llm_with_tools.invoke(messages)

    assistant_reply = response.content

    conversation_history.append({"role": "assistant", "content": assistant_reply})

    memory_data = extract_memory(user_input)

    print("memory_data => ", memory_data)

    if memory_data.get("store"):
        memory_text = memory_data["memory"]
        memory_type = memory_data.get("type", "general")

        updated = update_memory(user_id, memory_text, memory_type)

        if not updated:
            if not is_duplicate(user_id, memory_text):
                store_memory(user_id, memory_text, memory_type)
            else:
                print("⚠️ Duplicate skipped")

    return assistant_reply
