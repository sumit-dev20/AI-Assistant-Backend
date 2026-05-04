from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
import json

load_dotenv()

llm = ChatOpenAI()


def extract_memory(user_input):
    prompt = f"""
You are a memory extraction AI.

Decide if the following conversation contains important long-term memory about the user.

If YES, return JSON:
{{
    "store": true,
    "memory": "<short concise memory>",
    "type": "<goal | preference | personal | behavior>"
}}

If NO, return:
{{
    "store": false
}}


Examples:

Input:
User: I want to become an AI engineer
Output:
{{"store": true, "memory": "User's goal is to become an AI engineer", "type": "goal"}}

Input:
User: What is Python?
Output:
{{"store": false}}

Input:
User: I like working out in the morning
Output:
{{"store": true, "memory": "User prefers morning workouts", "type": "preference"}}


Conversation:
User: {user_input}

**DO NOT GIVE ANY PREAMBLE**
"""

    response = llm.invoke(prompt)

    content = response.content

    try:
        return json.loads(content)
    except:
        return {"store": False}


def classify_intent(user_input):
    response = llm.invoke(
        [
            {
                "role": "system",
                "content": """
Classify user intent into one of:

- "store" → user is sharing personal info (goal, preference, fact)
- "retrieve" → user is asking about past info
- "other" → anything else

Examples:

"I want to become AI engineer" → store
"My name is Sumit" → store
"I like gym in morning" → store

"What is my goal" → retrieve
"Tell me my dream" → retrieve
"Do you remember my name" → retrieve

"What is Python" → other

Return JSON:
{"intent": "..."}
""",
            },
            {"role": "user", "content": user_input},
        ]
    )

    return json.loads(response.content)
