import os
import time
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

ASSISTANT_ID = os.environ.get("ASSISTANT_ID")
VECTOR_STORE_ID = "vs_69df78ef4ce08191b5b40ab178dc298e" 
CSV_FILE = "top_500_stories.csv"

def update():
    print(f"--- Updating Knowledge in Vector Store {VECTOR_STORE_ID} ---")
    
    try:
        # 1. List and remove all existing files in the vector store to avoid duplication
        print("1. Cleaning existing files in the vector store...")
        vs_files = client.vector_stores.files.list(vector_store_id=VECTOR_STORE_ID)
        for vsf in vs_files.data:
            print(f"   Deleting old vector store file mapping: {vsf.id}")
            client.vector_stores.files.delete(
                vector_store_id=VECTOR_STORE_ID,
                file_id=vsf.id
            )
            
        # 2. Upload the new full CSV file
        print(f"\n2. Uploading {CSV_FILE}...")
        file = client.files.create(
            file=open(CSV_FILE, "rb"),
            purpose="assistants"
        )
        print(f"   File uploaded with ID: {file.id}")

        # 3. Add the file to the existing vector store
        print(f"\n3. Adding file to Vector Store {VECTOR_STORE_ID}...")
        vector_store_file = client.vector_stores.files.create(
            vector_store_id=VECTOR_STORE_ID,
            file_id=file.id
        )
        print(f"   File added to vector store successfully.")

        print("\n--- VECTOR UPDATE COMPLETE ---")
        print(f"Vector Store {VECTOR_STORE_ID} now contains the unified 500-mission CSV.")

    except Exception as e:
        print(f"\n❌ An error occurred: {e}")

if __name__ == "__main__":
    if not os.path.exists(CSV_FILE):
        print(f"Error: {CSV_FILE} not found.")
    elif not os.environ.get("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not found.")
    else:
        update()
