import os
import time
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
ASSISTANT_ID = os.environ.get("ASSISTANT_ID")

def verify():
    print(f"--- Verifying Assistant Retrieval ---")
    
    # 1. Create a thread
    thread = client.beta.threads.create()
    print(f"Created thread: {thread.id}")

    # 2. Add a message asking about a new mission
    # Mission #222 was about Mayor's nudge and infrastructure
    user_query = "What is the 'Mayor's Nudge' mission and what is the first step?"
    
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_query
    )
    print(f"User: {user_query}")

    # 3. Running assistant
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=ASSISTANT_ID
    )
    print(f"Started run: {run.id}")

    # 4. Polling
    while True:
        run_status = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        if run_status.status == "completed":
            break
        elif run_status.status == "failed":
            print(f"Run failed: {run_status.last_error}")
            return
        print("Waiting for response...")
        time.sleep(2)

    # 5. Get messages
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    last_message = messages.data[0]
    
    print(f"\nAssistant Response:\n{last_message.content[0].text.value}")

if __name__ == "__main__":
    verify()
