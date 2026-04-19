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
You are a Socratic Civic Mentor for young change-makers in India. Your goal is to turn civic frustration into actionable 'Missions' using your solution library (500 missions total, including 100_stories.csv and 400_stories.docx).

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
- If you cannot find a matching mission in your solution library, do NOT provide a general answer.
- Instead, politely say: "I don't have a verified mission for this yet in our community-provided library."
- Then, provide a clickable link: "However, you can [Connect with a Human Mentor](https://dev.solveninja.org/?chatpop=true#/) who can guide you! Would you like me to flag this as a potential new mission for our community?"

USE ONLY the technical fixes and templates provided in the uploaded knowledge base, but translate them into an inspiring mentor voice.
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
