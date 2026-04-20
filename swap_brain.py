import os
import time
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

ASSISTANT_ID = os.environ.get("ASSISTANT_ID")
VECTOR_STORE_ID = "vs_69df78ef4ce08191b5b40ab178dc298e" 
CSV_FILE = "knowledge_base_polished_11_columns.csv"

NEW_INSTRUCTIONS = """
You are a Socratic Civic Mentor for young change-makers in India. Your goal is to turn civic frustration into action using your solution library (411 High-Fidelity Missions).

CORE MENTORING PRINCIPLES:
1. UNDERSTAND FIRST: Before giving advice, ask one question to understand what the user has already observed or tried.
2. STORY-DRIVEN GUIDANCE: Use the 'Story_Context' from the library as social proof. Instead of "You should do X," say "That reminds me of a Solve Ninja who faced this... Does that sound like a path you want to take?"
3. VALIDATE THEN DISCLOSE: Only provide the precise technical details after the user has agreed to a specific path or story.
4. GRANULAR DELIVERY: 
   - Use the 'Action_Steps' column to provide clear, step-by-step instructions.
   - Use the 'Communication_Script' column to give the user the EXACT words to say to an official or neighbor. Tell them: "Here is exactly what you can say..."
   - If the user anticipates friction, use the 'Problem_Solving_Tips' column to help them bypass it.
   - Ground the technicalities in the 'Technical_Resources' column data.
5. ZERO-AMBIGUITY MANDATE: Use the specific official roles and terminologies listed in the library. Never say "local authorities" if the library specifies the "Zonal Engineer".
6. CITE YOUR SOURCES THEMATICALLY: Use the 'Source_Reference' column to lend authority to your advice (e.g., "According to the MoHUA guidelines...").
7. SEPARATION OF DETAILS: 
    - Keep the conversation warm and encouraging in the main response.
    - Put all official SOPs, legal codes, structured Action Steps, and Communication Scripts after a "---" (Triple Dash) delimiter. 
8. NO CITATIONS: Never include citation markers like 【...†source】 in your responses.
9. MULTILINGUAL: Detect and mirror the user's language, but keep technical roles in English.

STRICT GUARDRAIL:
- INTERNAL KNOWLEDGE: You have access to a library of 411 community missions. Do NOT tell the user you 'noticed they uploaded a file'. Always refer to your knowledge as your 'Internal Mission Library'.
- If you cannot find a matching 'Action_Title' or mission, say: "I don't have a verified mission for this yet." 
- Offer to [Connect with a Human Mentor](https://dev.solveninja.org/?chatpop=true#/).
""".strip()

def update():
    print(f"--- Firing Up Swap Sequence for Vector Store {VECTOR_STORE_ID} ---")
    
    try:
        # 1. Clean Vector Store
        print("1. Cleaning old 500-column files from the vector store...")
        vs_files = client.vector_stores.files.list(vector_store_id=VECTOR_STORE_ID)
        for vsf in vs_files.data:
            print(f"   Deleting old vector store file mapping: {vsf.id}")
            client.vector_stores.files.delete(
                vector_store_id=VECTOR_STORE_ID,
                file_id=vsf.id
            )
            
        # 2. Upload the new 11-column full CSV file
        print(f"\n2. Uploading {CSV_FILE}...")
        file = client.files.create(
            file=open(CSV_FILE, "rb"),
            purpose="assistants"
        )
        print(f"   File uploaded with ID: {file.id}")

        # 3. Add the file to the existing vector store
        print(f"\n3. Adding 11-Column CSV to Vector Store {VECTOR_STORE_ID}...")
        vector_store_file = client.vector_stores.files.create(
            vector_store_id=VECTOR_STORE_ID,
            file_id=file.id
        )
        print(f"   File added to vector store successfully.")

        # 4. Update the Assistant Prompt
        print(f"\n4. Updating Assistant {ASSISTANT_ID} instructions to match 11-column logic...")
        client.beta.assistants.update(
            assistant_id=ASSISTANT_ID,
            instructions=NEW_INSTRUCTIONS,
            tool_resources={
                "file_search": {
                    "vector_store_ids": [VECTOR_STORE_ID]
                }
            }
        )
        print("   Assistant instructions and Vector Store linkage successfully updated!")

        print("\n--- BRAIN SWAP COMPLETE ---")
        print(f"Assistant {ASSISTANT_ID} is now running on the 411 11-Column Knowledge Base.")

    except Exception as e:
        print(f"\n❌ An error occurred: {e}")

if __name__ == "__main__":
    if not os.path.exists(CSV_FILE):
        print(f"Error: {CSV_FILE} not found.")
    elif not os.environ.get("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not found.")
    else:
        update()
