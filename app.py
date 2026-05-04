from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from memory import store_memory, retrieve_memory, is_duplicate, update_memory
from memory_extractor import extract_memory, classify_intent
import json

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini")

conversation_history = [
    {"role": "system", "content": "You are a helpful AI assistant with memory."}
]

MAX_MEMORY = 20


def trim_memory():
    global conversation_history
    if len(conversation_history) > MAX_MEMORY:
        conversation_history[:] = [conversation_history[0]] + conversation_history[
            -MAX_MEMORY:
        ]


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


def chat(user_input):
    global conversation_history

    past_memories = retrieve_memory(user_input)
    memory_context = ""
    if past_memories:
        memory_context = "Relevant past memories:\n" + "\n".join(past_memories)

    conversation_history.append({"role": "user", "content": user_input})

    trim_memory()

    messages = conversation_history.copy()

    if memory_context:
        messages.insert(1, {"role": "system", "content": memory_context})
    tool = {"type": "web_search_preview"}

    llm_with_tools = llm.bind_tools([tool])

    response = llm_with_tools.invoke(messages)

    assistant_reply = response.content

    conversation_history.append({"role": "assistant", "content": assistant_reply})

    intent_data = classify_intent(user_input)
    intent = intent_data.get("intent")
    if intent == "store":
        memory_data = extract_memory(user_input)
        print("memory_data => ", memory_data)
        if isinstance(memory_data, str):
            memory_data = json.loads(memory_data)
            if memory_data.get("store"):
                memory_text = memory_data["memory"]
                memory_type = memory_data.get("type", "general")

                updated = update_memory(memory_text, memory_type)

                if not updated:
                    if not is_duplicate(memory_text):
                        store_memory(memory_text, memory_type)
                    else:
                        print("⚠️ Duplicate skipped")

    return assistant_reply
