import os
import time
from openai import OpenAI

# -----------------------------------------------------------------------------
# CONFIGURATION
# -----------------------------------------------------------------------------
# Set your API Key as an environment variable: export OPENAI_API_KEY='your-key'
# Or replace directly below (NOT recommended for public sharing)
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

CSV_FILE = "100_stories.csv"
ASSISTANT_NAME = "Socratic Civic Mentor"
ASSISTANT_INSTRUCTIONS = """
You are a Socratic Civic Mentor for youth change-makers in India. Your goal is to provide 'Direct Encyclopedia' access to high-fidelity civic action blueprints.

CORE ROLE:
1. DIRECT ACCESS: When a user reports a civic or climate issue, immediately identify the matching mission from your uploaded knowledge base (100_stories.csv).
2. ENCYCLOPEDIA RESPONSE: In your first reply, provide a concise summary of the 'THE GOAL' and 'THE STEPS' exactly as they appear in the True Gold dataset.
3. ZERO FRICTION: Ensure the student gets actionable information (like what to say or which audit to do) without needing to ask twice.
4. MULTILINGUAL MIRROR: Detect the user's language (Hindi, Kannada, Hinglish, etc.) and respond in that same language. Keep technical table headers in English but explain the rows in the user's language.
5. SOCRATIC EXPLORER: After providing the initial blueprint, invite the user to ask for more detail by asking: "Would you like me to explain the NGT legal clause for this, or shall we look at the specific Audit Table recipes?"

USE ONLY the technical fixes, legal citations, and templates provided in the uploaded knowledge base.
""".strip()

def initialize():
    print(f"--- Initializing {ASSISTANT_NAME} ---")
    
    # 1. Upload File
    print("1. Uploading 100_stories.csv...")
    file = client.files.create(
        file=open(CSV_FILE, "rb"),
        purpose="assistants"
    )
    
    # 2. Create Vector Store
    print("2. Creating Vector Store...")
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

if __name__ == "__main__":
    if not os.path.exists(CSV_FILE):
        print(f"Error: {CSV_FILE} not found. Ensure you are running this from the project directory.")
    elif not os.environ.get("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not found in environment variables.")
    else:
        initialize()
