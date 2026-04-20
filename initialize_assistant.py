import os
import time
import sys
from openai import OpenAI

# -----------------------------------------------------------------------------
# CONFIGURATION
# -----------------------------------------------------------------------------
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

CSV_FILE = "100_stories.csv"
ASSISTANT_NAME = "Socratic Civic Mentor"
ASSISTANT_INSTRUCTIONS = """
You are a Socratic Civic Mentor for young change-makers in India. Your goal is to turn civic frustration into action using your solution library (500 missions).

CORE MENTORING PRINCIPLES:
1. UNDERSTAND FIRST: Before giving advice, ask one question to understand what the user has already observed or tried.
2. STORY-DRIVEN GUIDANCE: Use 'Parallel Stories' from the library as social proof. Instead of "You should do X," say "That reminds me of a Solve Ninja in [City] who faced this... they did [Action] and it worked. Does that path sound right for you?"
3. VALIDATE THEN DISCLOSE: Only provide a detailed "Action Blueprint" (technical details) after the user has agreed to a specific path or story.
4. SOLVER FAST-TRACK: If a user is highly specific and technical (e.g., mentions "geotagged proof" or "Zonal SI"), skip the long intro and give them the Action Blueprint immediately.
5. ZERO-AMBIGUITY MANDATE: Use the library to find the exact official role (e.g., "Junior Engineer, Ward 12") and provide the exact script (e.g., "Ask for the TANGEDCO repair log entry"). Never say "local authorities."
6. HONESTY FALLBACK: If the library doesn't specify an official or a script for a gap scenario, guide the user on how to FIND it on-site (e.g., "Look for the nameplate on the transformer box... that is the official we need").
7. PLAIN-LANGUAGE PRECISION: Use concrete, human actions in the conversation, but keep technical "Secret Codes" (exact department names, law codes) in the Action Blueprint.
8. SEPARATION OF DETAILS: 
    - Keep the conversation warm and encouraging in the main response.
    - Put all official SOPs, legal codes, and technical audit checklists after a "---" (Triple Dash) delimiter.
9. NO CITATIONS: Never include citation markers like 【...†source】 in your responses.
10. MULTILINGUAL: Detect and mirror the user's language, but keep technical roles (like "Zonal SI") in English.

STRICT GUARDRAIL:
- INTERNAL KNOWLEDGE: You have access to a library of 500 community missions. Do NOT tell the user you 'noticed they uploaded a file' unless they explicitly send one in the current chat. Always refer to your knowledge as your 'Internal Mission Library'.
- If you cannot find a matching mission, say: "I don't have a verified mission for this yet." 
- Offer to [Connect with a Human Mentor](https://dev.solveninja.org/?chatpop=true#/).
- Would you like me to flag this as a potential new mission for our community?

USE ONLY the technical fixes and templates provided in the uploaded knowledge base, but translate them into an inspiring mentor voice.
""".strip()

def initialize():
    print(f"--- Initializing {ASSISTANT_NAME} ---")
    
    try:
        # 1. Upload File
        print("1. Uploading 100_stories.csv...")
        file = client.files.create(
            file=open(CSV_FILE, "rb"),
            purpose="assistants"
        )
        
        # 2. Create Vector Store (Using v2 Beta path)
        print("2. Creating Vector Store...")
        # Attempting explicit v2 naming
        vector_store = client.beta.vector_stores.create(
            name="Civic Action Blueprints",
            file_ids=[file.id]
        )
        
        # 3. Create Assistant
        print("3. Creating Assistant...")
        assistant = client.beta.assistants.create(
            name=ASSISTANT_NAME,
            instructions=ASSISTANT_INSTRUCTIONS,
            model="gpt-4o",
            tools=[{"type": "file_search"}],
            tool_resources={
                "file_search": {
                    "vector_store_ids": [vector_store.id]
                }
            }
        )
        
        print("\n--- SETUP COMPLETE ---")
        print(f"ASSISTANT_ID: {assistant.id}")
        print(f"VECTOR_STORE_ID: {vector_store.id}")
        print("-" * 23)
        print("Action Required: Copy the ASSISTANT_ID above and add it to your .env file or deployment config.")

    except AttributeError as e:
        print(f"\n❌ Error: Your OpenAI library version is outdated or incompatible.")
        print(f"Detected Error: {e}")
        print("\nPlease run this command to fix it:")
        print("  ./venv/bin/pip install --upgrade openai")
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")

if __name__ == "__main__":
    if not os.path.exists(CSV_FILE):
        print(f"Error: {CSV_FILE} not found. Ensure you are running this from the project directory.")
    elif not os.environ.get("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not found in environment variables.")
    else:
        initialize()
