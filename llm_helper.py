import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize GitHub Marketplace LLM client
client = OpenAI(
    base_url="https://models.github.ai/inference",
    api_key=os.getenv("GITHUB_TOKEN")  # must match your .env variable
)

SYSTEM_PROMPT = """You are a healthcare triage assistant for educational purposes only.
Rules:
1) Always return valid JSON ONLY. No extra commentary outside JSON.
2) The JSON schema must be exactly one of:
   - Ask mode: {"mode":"ask","question":"<follow-up question>"}
   - Answer mode: {"mode":"answer","conditions":[{"name":"...","confidence":"high|medium|low","reason":"..."}],"next_steps":["..."],"disclaimer":"..."}
3) If insufficient information, use Ask mode. If you have enough info, use Answer mode.
4) NEVER give prescriptions or dosages. If the user reports emergency red flags (chest pain, severe breathing trouble, fainting, blue lips), return Answer mode immediately with a single high-priority next_step telling them to seek emergency care.
5) When generating Answer mode, map symptoms to **possible medical conditions**, include **confidence levels** and reasons.
6) Keep Ask mode prompts short and focused (one question).
7) Return only the JSON (no extra text).
"""

def call_llm(messages):
    # Ensure messages are properly formatted for the LLM
    full_messages = [{'role': 'system', 'content': SYSTEM_PROMPT}] + messages
    try:
        resp = client.chat.completions.create(
            model="openai/gpt-4o-mini",  # smaller safer model for testing
            messages=full_messages,
            temperature=0.0,
            max_tokens=1000,
            top_p=1
        )

        text = resp.choices[0].message.content.strip()

        # Quick validation: ensure JSON
        try:
            obj = json.loads(text)
            # Ensure Answer mode has required keys
            if obj.get("mode") == "answer":
                obj.setdefault("conditions", [])
                obj.setdefault("next_steps", [])
                obj.setdefault("disclaimer", "This response is for educational purposes only.")
            return json.dumps(obj)  # Return safe JSON string
        except json.JSONDecodeError:
            # Return fallback error JSON
            print("LLM returned invalid JSON. Raw:", text)
            return json.dumps({
                "mode": "answer",
                "conditions": [],
                "next_steps": ["Error parsing LLM output. Please try again."],
                "disclaimer": "LLM output was invalid."
            })

    except Exception as e:
        print("LLM call failed:", e)
        return json.dumps({
            "mode": "answer",
            "conditions": [],
            "next_steps": ["Error calling LLM. Please try again."],
            "disclaimer": "LLM call failed."
        })
