import os
import time
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

ASSISTANT_ID = os.environ.get("ASSISTANT_ID")
# We retrieved this during research
VECTOR_STORE_ID = "vs_69df78ef4ce08191b5b40ab178dc298e" 
DOCX_FILE = "400_stories.docx"

NEW_INSTRUCTIONS = """
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
""".strip()

def update():
    print(f"--- Updating Knowledge for Assistant {ASSISTANT_ID} ---")
    
    try:
        # 1. Upload the new DOCX file
        print(f"1. Uploading {DOCX_FILE}...")
        file = client.files.create(
            file=open(DOCX_FILE, "rb"),
            purpose="assistants"
        )
        print(f"   File uploaded with ID: {file.id}")

        # 2. Add the file to the existing vector store
        print(f"2. Adding file to Vector Store {VECTOR_STORE_ID}...")
        vector_store_file = client.vector_stores.files.create(
            vector_store_id=VECTOR_STORE_ID,
            file_id=file.id
        )
        print(f"   File added to vector store.")

        # 3. Update Assistant Instructions
        print("3. Updating Assistant instructions...")
        client.beta.assistants.update(
            assistant_id=ASSISTANT_ID,
            instructions=NEW_INSTRUCTIONS,
            tool_resources={
                "file_search": {
                    "vector_store_ids": [VECTOR_STORE_ID]
                }
            }
        )
        print("   Assistant instructions updated.")

        print("\n--- UPDATE COMPLETE ---")
        print(f"Assistant {ASSISTANT_ID} is now using 500 stories.")

    except Exception as e:
        print(f"\n❌ An error occurred: {e}")

if __name__ == "__main__":
    if not os.path.exists(DOCX_FILE):
        print(f"Error: {DOCX_FILE} not found.")
    elif not os.environ.get("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not found.")
    else:
        update()
