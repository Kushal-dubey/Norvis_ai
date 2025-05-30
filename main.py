from dotenv import load_dotenv
import os
from shared_memory.memory import SharedMemory
from classifier_agent.classifier import ClassifierAgent
from intent_agents import InvoiceAgent, RFQAgent, ComplaintAgent, RegulationAgent

load_dotenv()
content = "This is sample content to test agent processing."

agent = RegulationAgent()      #Regulatiom
agent.process(content)

agent = ComplaintAgent()    #complaint
agent.process(content)

agent = InvoiceAgent()       #Invoice
agent.process(content)

agent = RFQAgent()          #RFQ
agent.process(content)

api_key = os.getenv("OPENAI_API_KEY")
db_path = os.getenv("DATABASE_PATH")

print("API KEY:", api_key)
print("DB PATH:", db_path)

if __name__ == "__main__":
    print("Starting SharedMemory test...")

    mem = SharedMemory()
    mem.log_memory(
        source="email_agent",
        content="This is the email content",
        result="Email intent classified",
        extracted_values="{'some_key': 'some_value'}",
        thread_id="thread_123",
        type_="Email"
    )
    records = mem.fetch_all()
    for row in records:
         print(f"Record:", row)

    classifier = ClassifierAgent(db_path=db_path if db_path else "shared_memory.db")

    filepaths = [
        "sample_inputs/sample_test_invoice.pdf",
        "sample_inputs/sample_rfq.json",
        "sample_inputs/sample_test_email.txt"
    ]

    for path in filepaths:
        if not os.path.exists(path):
            print(f" File not found: {path}")
            continue

        result = classifier.route_input(path)
        print(f"\n--- File: {path} ---")
        print(f"Format: {result['format']}")
        print(f"Intent: {result['intent']}")
        print(f"Content Snippet: {result['content'][:150]}")
