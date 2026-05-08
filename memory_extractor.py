from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
import json

load_dotenv(override=True)

llm = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def extract_memory(user_input):
    prompt = f"""
You are an AI memory system.

Analyze the user's message.

Your tasks:
1. Detect intent:
   - "store" → user shares personal information, goals, preferences, facts
   - "retrieve" → user asks about previous memories
   - "other" → anything else

2. If intent is "store":
   Extract concise long-term memory.

Return ONLY valid JSON.

Format:

{{
    "intent": "store | retrieve | other",
    "store": true/false,
    "memory": "<memory text>",
    "type": "goal | preference | personal | behavior"
}}

If no memory should be stored:

{{
    "intent": "other",
    "store": false
}}

Examples:

Input:
"I want to become an AI engineer"

Output:
{{
    "intent": "store",
    "store": true,
    "memory": "User's goal is to become an AI engineer",
    "type": "goal"
}}

Input:
"What is my goal?"

Output:
{{
    "intent": "retrieve",
    "store": false
}}

Input:
"What is Python?"

Output:
{{
    "intent": "other",
    "store": false
}}

User Message:
{user_input}

IMPORTANT:
- Return ONLY JSON
- No markdown
- No explanation

**DO NOT GIVE ANY PREAMBLE**
"""

    response = llm.invoke(prompt)

    content = response.content

    try:
        return json.loads(content)
    except:
        return {"store": False}

