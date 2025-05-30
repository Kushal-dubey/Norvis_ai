import os
import filetype
import PyPDF2
import time
import re
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError


# Memory and Intent Agents
from shared_memory.memory import SharedMemory
from intent_agents import InvoiceAgent, RFQAgent, ComplaintAgent, RegulationAgent

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables")

client = OpenAI(api_key=api_key)

# Toggle between actual OpenAI API or mock for testing
USE_MOCK_API = True


# ---------------------- MOCK API FOR TESTING PURPOSES ----------------------
def mock_chat_completion_create(*args, **kwargs):
    messages = kwargs.get('messages', [])
    user_message = ""
    for msg in messages:
        if msg.get('role') == 'user':
            user_message = msg.get('content', "").lower()
            break

    if "invoice" in user_message:
        intent = "Invoice"
    elif "rfq" in user_message:
        intent = "RFQ"
    elif "complaint" in user_message:
        intent = "Complaint"
    elif "regulation" in user_message:
        intent = "Regulation"
    else:
        intent = "Other"

    class MockChoice:
        def __init__(self, content):
            self.message = type('obj', (object,), {'content': content})

    class MockResponse:
        def __init__(self, intent):
            self.choices = [MockChoice(intent)]

    return MockResponse(intent)


# ---------------------- MAIN CLASSIFIER AGENT ----------------------
class ClassifierAgent:
    def __init__(self, db_path="shared_memory.db"):
        self.memory = SharedMemory(db_path)

    def detect_format(self, input_data):
        if isinstance(input_data, str) and os.path.isfile(input_data):
            kind = filetype.guess(input_data)
            if kind:
                if kind.mime == 'application/pdf':
                    return "PDF"
                elif kind.mime == 'application/json':
                    return "JSON"
                else:
                    return "Unknown"
            else:
                return "Unknown"
        elif isinstance(input_data, str):
            if "@" in input_data and ("from:" in input_data.lower() or "to:" in input_data.lower()):
                return "Email"
            else:
                return "Text"
        else:
            return "Unknown"

    def extract_pdf_text(self, pdf_path):
        text = ""
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() or ""
        return text

    def parse_email(self, raw_email_text):
        sender_match = re.search(r"From:\s*(.*)", raw_email_text, re.IGNORECASE)
        sender = sender_match.group(1).strip() if sender_match else "Unknown Sender"
        parts = raw_email_text.split('\n\n', 1)
        body = parts[1].strip() if len(parts) > 1 else ""
        return sender, body





    def classify_intent(self, content, retries=3, delay=5):
        prompt = f"Classify the intent of this text into one of: Invoice, RFQ, Complaint, Regulation, Other.\n\nText:\n{content}\n\nIntent:"

        for attempt in range(retries):
            try:
                if USE_MOCK_API:
                    response = mock_chat_completion_create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are an intent classification assistant."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=10,
                        temperature=0
                    )
                else:
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are an intent classification assistant."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=10,
                        temperature=0
                    )

                intent = response.choices[0].message.content.strip()
                return intent

            except OpenAIError as e:
                print(f"OpenAI API error during call (attempt {attempt + 1}): {e}")
                if "insufficient_quota" in str(e).lower():
                    break
                time.sleep(delay)
                delay *= 2
            except Exception as e:
                print(f"General error during call (attempt {attempt + 1}): {e}")
                time.sleep(delay)
                delay *= 2

        return "Unknown"

    def route_input(self, input_data):
        format_ = self.detect_format(input_data)

        if format_ == "PDF":
            content = self.extract_pdf_text(input_data)
            sender = "Unknown Sender"
        elif format_ == "JSON":
            with open(input_data, 'r') as f:
                content = f.read()
            sender = "Unknown Sender"
        elif format_ == "Email":
            sender, content = self.parse_email(input_data)
        else:
            content = input_data
            sender = "Unknown Sender"

        intent = self.classify_intent(content)

        # Log to shared memory
        self.memory.log_memory(
            source="classifier_agent",
            content="Input file classified",
            result=f"Intent identified: {intent}",
            extracted_values=f"{{'intent': '{intent}'}}",
            thread_id="thread_001",
            type_="Classifier"
        )

        # Route to specific intent agent
        if intent == "Invoice":
            agent = InvoiceAgent()
            agent.process(content)
        elif intent == "RFQ":
            agent = RFQAgent()
            agent.process(content)
        elif intent == "Complaint":
            agent = ComplaintAgent()
            agent.process(content)
        elif intent == "Regulation":
            agent = RegulationAgent()
            agent.process(content)
        else:
            print(f"[ClassifierAgent] No specific agent found for intent: {intent}")

        return {
            "format": format_,
            "intent": intent,
            "sender": sender,
            "content": content
        }
    # ✅ Add this OUTSIDE of the ClassifierAgent class
# classifier_agent/classifier.py

def classify_input_file(file_path):
    """
    Dummy classifier logic that checks file extension and returns (type, intent)
    """
    if file_path.endswith(".pdf"):
        return "PDF", "Invoice"
    elif file_path.endswith(".json"):
        return "JSON", "Complaint"
    elif file_path.endswith(".txt"):
        return "Email", "RFQ"
    else:
        return "Unknown", "Unknown"




# ---------------------- FOR DEBUGGING & TESTING ----------------------

if __name__ == "__main__":
    agent = ClassifierAgent()

    # Example 1: PDF file input
    test_input_pdf = "sample_inputs/sample_invoice.pdf"
    result_pdf = agent.route_input(test_input_pdf)
    print(f"Detected Format: {result_pdf['format']}")
    print(f"Detected Intent: {result_pdf['intent']}")

    # Example 2: Email raw text input
    test_input_email = """From: user@example.com
To: support@example.com
Subject: Complaint about the invoice

Dear team,
I have an issue with my recent invoice. Please look into this.
Regards,
User"""

    result_email = agent.route_input(test_input_email)
    print(f"Detected Format: {result_email['format']}")
    print(f"Detected Intent: {result_email['intent']}")
    print(f"Sender Email: {result_email['sender']}")


