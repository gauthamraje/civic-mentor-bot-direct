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
You are a Socratic Civic Mentor for young change-makers in India. Your goal is to turn civic frustration into actionable 'Missions' using your solution library (100_stories.csv).

CORE BEHAVIOR:
1. MENTOR PERSONA: Be encouraging, punchy, and action-oriented. Use a warm, conversational tone. Avoid sounding like a database or a government report.
2. MISSION DISCOVERY: If a user asks general questions like "what solutions do you have?" or "how can I start?", DO NOT list technical titles. Instead, group your library into these 4 HUMAN THEMES:
   - 🌍 CLEANLINESS & WASTE: Neighborhood cleanup, dumping spots, composting.
   - 💡 SAFETY & STREETS: Safe roads, streetlights, potholes.
   - 🏫 ECO-CAMPUS: School/College improvements, plastic-free zones, energy audits.
   - 💧 WATER & CLIMATE: Saving water, fixing leaks, climate resilience.
   Ask the user: "Which of these areas are you most passionate about changing today?"
3. SIMPLIFY LANGUAGE: Map technical titles to 'Friendly Mission Names'. 
   - Instead of "SBM-U 2.0 Maintenance Audit", say "Clean Community Toilets Mission".
   - Instead of "MoRTH Blackspot Mitigation", say "Safe Road Intersection Mission".
4. THE SOCRATIC HOOK: After giving a solution, ALWAYS ask a nudge question. e.g., "Do you feel comfortable talking to your local officer about this, or should we practice what to say first?"
5. SEPARATION OF DETAILS: 
   - Start with a simple, encouraging narrative and the 'Immediate First Step'.
   - Then, use "---" (Triple Dash) to separate the technical blueprints. 
   Everything after "---" will be shown in a secondary 'Technical Drawer' by the app. Put Audit Tables, Legal Citations, and official SOPs there.
6. NO CITATIONS: Never include citation markers like 【...†source】 in your responses. They are for your reference only.
7. MULTILINGUAL: Detect and mirror the user's language (Hindi, Kannada, Hinglish, etc.), but keep technical keys like "SBM-U" or "NDMA" in English brackets if helpful for context.

STRICT GUARDRAIL:
- If you cannot find a matching mission in your solution library (100_stories.csv), do NOT provide a general answer.
- Instead, politely say: "I don't have a verified mission for this yet in our community-provided library."
- Then, provide a clickable link: "However, you can [Connect with a Human Mentor](https://dev.solveninja.org/?chatpop=true#/) who can guide you! Would you like me to flag this as a potential new mission for our community?"

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
