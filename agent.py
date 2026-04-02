import os
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate


load_dotenv()  # loads .env file

# Initialize Groq LLM
llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama-3.1-8b-instant"
)

# Prompt template
template = """
Write a short, natural LinkedIn message.

Context:
- Name: {name}
- Role: {role}
- Company: {company}

Rules:
- Keep it under 3-4 lines
- Sound human, not salesy
- Mention something relevant to their role/company
- Subtly express interest in opportunities
- End politely

Message:
"""

prompt = PromptTemplate(
    input_variables=["name", "role", "company"],
    template=template
)

def generate_message(name, role, company):
    chain = prompt | llm
    response = chain.invoke({
        "name": name,
        "role": role,
        "company": company
    })
    return response.content.strip()

def classify_reply(message):
    prompt = f"""
Classify this LinkedIn reply:

Message: "{message}"

Return JSON:
{{
  "response": "interested / not_interested / neutral",
  "notes": "short summary",
  "priority": "High / Medium / Low"
}}
"""

    response = llm.invoke(prompt)

    import json
    return json.loads(response.content)