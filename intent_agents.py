from shared_memory.memory import SharedMemory
from datetime import datetime

class InvoiceAgent:
    def __init__(self, db_path="shared_memory.db"):
        self.memory = SharedMemory(db_path)

    def process(self, content):
        print("Processing Invoice content...")
        result = f"Processed invoice snippet: {content[:100]}"
        extracted_values = f'{{"snippet": "{content[:100]}"}}'
        self.memory.log_memory(
            source="invoice_agent",
            content=content,
            result=result,
            extracted_values=extracted_values,
            type_="Invoice",
            thread_id="thread_invoice"
        )
        print("Invoice processing logged.")


class RFQAgent:
    def __init__(self, db_path="shared_memory.db"):
        self.memory = SharedMemory(db_path)

    def process(self, content):
        print("Processing RFQ content...")
        result = f"Processed RFQ snippet: {content[:100]}"
        extracted_values = f'{{"snippet": "{content[:100]}"}}'
        self.memory.log_memory(
            source="rfq_agent",
            content=content,
            result=result,
            extracted_values=extracted_values,
            type_="RFQ",
            thread_id="thread_rfq"
        )
        print("RFQ processing logged.")


class ComplaintAgent:
    def __init__(self, db_path="shared_memory.db"):
        self.memory = SharedMemory(db_path)

    def process(self, content):
        print("Processing Complaint content...")
        result = f"Processed complaint snippet: {content[:100]}"
        extracted_values = f'{{"snippet": "{content[:100]}"}}'
        self.memory.log_memory(
            source="complaint_agent",
            content=content,
            result=result,
            extracted_values=extracted_values,
            type_="Complaint",
            thread_id="thread_complaint"
        )
        print("Complaint processing logged.")


class RegulationAgent:
    def __init__(self, db_path="shared_memory.db"):
        self.memory = SharedMemory(db_path)

    def process(self, content):
        print("Processing regulation content...")
        result = f"Processed regulation snippet: {content[:100]}"
        extracted_values = f'{{"snippet": "{content[:100]}"}}'
        self.memory.log_memory(
            source="regulation_agent",
            content=content,
            result=result,
            extracted_values=extracted_values,
            type_="Regulation",
            thread_id="thread_regulation"
        )
        print("Regulation processing logged.")
