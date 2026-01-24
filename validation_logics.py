import os, uuid
import json 
from datetime import datetime
from dotenv import load_dotenv  
from flask import Flask, render_template, request, redirect, url_for, flash, session, Blueprint, jsonify
from azure.storage.blob import BlobServiceClient
import tempfile
import re

from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from openai import AzureOpenAI

from langchain.text_splitter import RecursiveCharacterTextSplitter
from azure.search.documents import SearchClient


load_dotenv()

blob_service = BlobServiceClient.from_connection_string(os.getenv("AZURE_STORAGE_CONNECTION_STRING"))
container_name = "credimate-data"
container_client = blob_service.get_container_client(container_name)

form_recognizer_endpoint = os.getenv("AZURE_FORMRECOGNIZER_ENDPOINT")
form_recognizer_key = os.getenv("AZURE_FORMRECOGNIZER_KEY")

# Initialize Azure Document Intelligence Client
document_client = DocumentAnalysisClient(
    endpoint=form_recognizer_endpoint,
    credential=AzureKeyCredential(form_recognizer_key)
)

def run_file_integrity_check(user):
    return True 

#--------- AADHAR -------------------------------------------------------

def get_aadhaar_blob_path(user):
    prefix = f"User_{user.id}_{user.first_name}/docs/"
    valid_extensions = [".pdf", ".jpg", ".jpeg", ".png"]

    blob_list = container_client.list_blobs(name_starts_with=prefix)

    for blob in blob_list:
        if re.match(r".*aadharCardFile.*\.(pdf|jpg|jpeg|png)$", blob.name, re.IGNORECASE):
            return blob.name

    return None

def validate_aadhar(user):
    blob_path = get_aadhaar_blob_path(user)

    if not blob_path:
        return False, "Aadhaar document not found"
    
    try:
        blob_client = container_client.get_blob_client(blob_path)

        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(blob_path)[-1]) as tmp_file:
            tmp_file.write(blob_client.download_blob().readall())
            temp_path = tmp_file.name

        result = analyze_aadhaar_logic(temp_path)

        os.remove(temp_path)

        # Decision
        if result:
            return True
        else:
            return False

    except Exception as e:
        print("[ERROR] Aadhaar validation:", e)
        return jsonify(success=False, message="Aadhaar validation error")
    
def analyze_aadhaar_logic(file_path):
    print("inside aadhar logic")
    result_json = {
        "document": "aadhaar",
        "key_values": {},
        "text": "",
        "issues": [],
        "valid": True
    }

    try:
        with open(file_path, "rb") as f:
            poller = document_client.begin_analyze_document("prebuilt-layout", document=f)
            result = poller.result()

        extracted_text = []
        for page in result.pages:
            for line in page.lines:
                extracted_text.append(line.content)

        full_text = " ".join(extracted_text)
        full_text_lower = full_text.lower()
        result_json["text"] = full_text

        # Extract Aadhaar Number
        match_aadhaar = re.search(r"\b\d{4}[ \t]?\d{4}[ \t]?\d{4}\b", full_text)
        if match_aadhaar:
            result_json["key_values"]["aadhaar_number"] = match_aadhaar.group().replace(" ", "")

        # Extract Gender
        match_gender = re.search(r"\b(MALE|FEMALE|M/F)\b", full_text, re.IGNORECASE)
        if match_gender:
            result_json["key_values"]["gender"] = match_gender.group()

        # Extract Date of Birth
        match_dob = re.search(r"\b(\d{2}/\d{2}/\d{4}|\d{4})\b", full_text)
        if match_dob:
            result_json["key_values"]["birth_info"] = match_dob.group()

        # Tampering Checks
        if not any(kw in full_text_lower for kw in ["government of india", "unique identification authority"]):
            result_json["issues"].append("Missing Govt/UIDAI authority reference")
        if "aadhaar" not in full_text_lower:
            result_json["issues"].append("Missing Aadhaar word")
        if "gender" not in result_json["key_values"]:
            result_json["issues"].append("Missing gender")
        if "birth_info" not in result_json["key_values"]:
            result_json["issues"].append("Missing DOB or YOB")
        if "aadhaar_number" not in result_json["key_values"]:
            result_json["issues"].append("Missing or invalid Aadhaar number")

        if result_json["issues"]:
            result_json["valid"] = False

    except Exception as e:
        result_json["valid"] = False
        result_json["issues"].append(f"Error analyzing Aadhaar: {str(e)}")

    print(result_json)

    return result_json["valid"]


#-------------------------------------------------------------------------


#--------- PAN -----------------------------------------------------------

def get_pan_blob_path(user):
    prefix = f"User_{user.id}_{user.first_name}/docs/"
    valid_extensions = [".pdf", ".jpg", ".jpeg", ".png"]

    blob_list = container_client.list_blobs(name_starts_with=prefix)

    for blob in blob_list:
        if re.match(r".*panCardFile.*\.(pdf|jpg|jpeg|png)$", blob.name, re.IGNORECASE):
            return blob.name

def validate_pan(user):
    blob_path = get_pan_blob_path(user)

    if not blob_path:
        return False, "PAN document not found"
    
    try:
        blob_client = container_client.get_blob_client(blob_path)

        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(blob_path)[-1]) as tmp_file:
            tmp_file.write(blob_client.download_blob().readall())
            temp_path = tmp_file.name

        result = analyze_pan_logic(temp_path)

        os.remove(temp_path)

        # Decision
        if result:
            return True
        else:
            return False

    except Exception as e:
        print("[ERROR] PAN validation:", e)
        return jsonify(success=False, message="PAN validation error")

def analyze_pan_logic(file_path):
    result_json = {
        "document": "pan",
        "key_values": {},
        "text": "",
        "issues": [],
        "valid": True
    }

    try:
        with open(file_path, "rb") as f:
            poller = document_client.begin_analyze_document("prebuilt-layout", document=f)
            result = poller.result()

        extracted_text = []
        for page in result.pages:
            for line in page.lines:
                extracted_text.append(line.content)

        full_text = " ".join(extracted_text)
        full_text_upper = full_text.upper()
        result_json["text"] = full_text

        # Normalize text for tampering checks
        normalized_text = re.sub(r"[^\w\s]", "", full_text_upper)

        # PAN number extraction (allowing spaces between blocks)
        match_pan = re.search(r"\b([A-Z]{5})\s*([0-9]{4})\s*([A-Z])\b", full_text_upper)
        if match_pan:
            pan_number = "".join(match_pan.groups())
            result_json["key_values"]["pan_number"] = pan_number
        else:
            result_json["issues"].append("Missing or invalid PAN number format")

        # Basic keyword tamper check (with fuzzy alternatives)
        required_keywords = ["INCOME TAX", "GOVT OF INDIA", "PERMANENT ACCOUNT NUMBER"]
        if not any(keyword in normalized_text for keyword in required_keywords):
            result_json["issues"].append("Missing PAN government or authority info")

        # Name extraction (loosened fallback)
        name_matches = re.findall(r"(NAME\s*:?[\sA-Z]+)", full_text_upper)
        if name_matches:
            cleaned_name = name_matches[0].split(":")[-1].strip()
            result_json["key_values"]["name"] = cleaned_name

        # Final validity
        if result_json["issues"]:
            result_json["valid"] = False

    except Exception as e:
        result_json["valid"] = False
        result_json["issues"].append(f"Error analyzing PAN: {str(e)}")

    print(result_json)
    return result_json["valid"]

#-------------------------------------------------------------------------

def confirm_kyc_status(user):
    return True

#--------- read documents -----------------------------------------------------------

def flatten_document_context(result_json):
    lines = []
    lines.append(f"Document: {result_json.get('document', 'unknown')}")
       
    # Key-Value Pairs
    key_values = result_json.get("key_values", {})
    if key_values:
        lines.append("Key Values:")
        for k, v in key_values.items():
            lines.append(f" - {k}: {v}")
    
    # Tables (optional, simplified)
    tables = result_json.get("tables", [])
    if tables:
        lines.append("Tables (preview):")
        for i, table in enumerate(tables):
            lines.append(f" Table {i+1}:")
            for row in table:
                lines.append("".join(str(cell) for cell in row))
            lines.append("")  # space between tables
    
    # Full raw text
    lines.append("Extracted Text:")
    lines.append(result_json.get("text", ""))  
    lines.append("\n" + "-"*50 + "\n")
    return "\n".join(lines)

def read_uploaded_documents(user):
    folder_prefix = f"User_{user.id}_{user.first_name}/docs/"
    failures = []

    document_map = {
        "payslip1File": analyze_payslip,
        "payslip2File": analyze_payslip,
        "payslip3File": analyze_payslip,
        "bankStatementFile": analyze_bank_statement,
        "creditReportFile": analyze_cibil_report
    }

    combined_text = ""

    for doc_key, analysis_func in document_map.items():
        try:
            # Step 1: Find the blob (support any extension)
            matching_blob = None
            for blob in container_client.list_blobs(name_starts_with=folder_prefix):
                if doc_key in blob.name:
                    matching_blob = blob.name
                    break

            if not matching_blob:
                failures.append(f"{doc_key} not found in blob storage")
                continue

            # Step 2: Download to temp file
            ext = os.path.splitext(matching_blob)[-1]
            blob_client = container_client.get_blob_client(matching_blob)

            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp_file:
                tmp_file.write(blob_client.download_blob().readall())
                temp_path = tmp_file.name

            # Step 3: Run analysis
            result = analysis_func(temp_path)

            chunk = flatten_document_context(result)
            combined_text += chunk + "\n"

            os.remove(temp_path)

            if not result.get("valid", True):
                issues = result.get("issues", [])
                failures.append(f"{doc_key} failed: " + "; ".join(issues))

        except Exception as e:
            failures.append(f"{doc_key} raised error: {str(e)}")

    print(failures)

    if failures:
        return False
    else:
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode='w', encoding='utf-8') as temp_file:
                temp_file.write(combined_text)
                context_path = temp_file.name

            blob_path = f"User_{user.id}_{user.first_name}/context/combined_context.txt"
            with open(context_path, "rb") as f:
                container_client.upload_blob(name=blob_path, data=f, overwrite=True)

            os.remove(context_path)
            return True
        
        except Exception as e:
            return False, f"Failed to save context: {str(e)}"

def analyze_payslip(file_path):
    print("\n📄 Payslip Analysis Started...\n")

    result_json = {
        "document": "pay slip",
        "key_values": {},
        "tables": [],
        "text": "",
        "net_income": None,
        "eligible": False,
        "issues": [],
        "valid": True
    }

    try:
        with open(file_path, "rb") as f:
            poller = document_client.begin_analyze_document("prebuilt-document", document=f)
            result = poller.result()

        extracted_text = ""
        for page in result.pages:
            for line in page.lines:
                extracted_text += line.content + "\n"

        # ✅ Extract Key-Value Pairs
        key_value_dict = {}
        if result.key_value_pairs:
            for kv in result.key_value_pairs:
                key = kv.key.content.strip() if kv.key else ""
                value = kv.value.content.strip() if kv.value else ""
                key_value_dict[key.lower()] = value
        result_json["key_values"] = key_value_dict

        # ✅ Extract Tables
        for table in result.tables:
            current_table = []
            row = []
            last_row_index = 0
            for cell in table.cells:
                if cell.row_index != last_row_index:
                    result_json["tables"].append(row)
                    row = []
                    last_row_index = cell.row_index
                row.append(cell.content)
            if row:
                result_json["tables"].append(row)

        # ✅ Find Net Salary
        net_keywords = [
            "net pay", "take home", "net salary", "net amount", "salary credited"
        ]
        net_income = None

        # Try from key-values
        for key, value in key_value_dict.items():
            if any(k in key for k in net_keywords):
                net_income = value
                break

        # Try from raw text
        if not net_income:
            match = re.search(r"(net\s+(pay|salary|amount|income)[^\d]*)(₹?\s?\d[\d,]*)", extracted_text, re.IGNORECASE)
            if match:
                net_income = match.group(3)

        # Normalize net income
        if net_income:
            result_json["net_income"] = net_income
            net_numeric = int(re.sub(r"[^\d]", "", net_income))
            if net_numeric >= 25000:
                result_json["eligible"] = True
            else:
                result_json["eligible"] = False
        else:
            result_json["issues"].append("Net income could not be detected.")

    except Exception as e:
        result_json["issues"].append(f"Error during payslip analysis: {str(e)}")

    return result_json

def analyze_bank_statement(file_path):
    print("\n🏦 Bank Statement Analysis Started...\n")
    result_json = {
        "document": "bank_statement",
        "key_values": {},
        "tables": [],
        "text": "",
        "issues": [],
        "valid": True
    }

    try:
        with open(file_path, "rb") as f:
            poller = document_client.begin_analyze_document("prebuilt-document", document=f)
            result = poller.result()

        # Extract full text
        full_text = " ".join([line.content for page in result.pages for line in page.lines])
        result_json["text"] = full_text

        # Extract key-value pairs
        for kv in result.key_value_pairs:
            if kv.key and kv.value:
                key = kv.key.content.strip()
                value = kv.value.content.strip()
                result_json["key_values"][key] = value

        # Extract tables
        for table in result.tables:
            table_data = []
            for row_idx in range(table.row_count):
                row_data = {}
                for col_idx in range(table.column_count):
                    cell = next((c for c in table.cells if c.row_index == row_idx and c.column_index == col_idx), None)
                    if cell:
                        row_data[f"col_{col_idx}"] = cell.content
                table_data.append(row_data)
            result_json["tables"].append(table_data)

        # Simple validations (optional)
        if not result_json["tables"]:
            result_json["issues"].append("No transaction table found.")
        if not any(keyword in full_text.lower() for keyword in ["account", "bank", "transaction"]):
            result_json["issues"].append("Does not appear to be a bank statement.")

        if result_json["issues"]:
            result_json["valid"] = False

    except Exception as e:
        result_json["valid"] = False
        result_json["issues"].append(f"Error analyzing bank statement: {str(e)}")

    return result_json

def analyze_cibil_report(file_path):
    print("\n📊 CIBIL Report Analysis Started...\n")
    result_json = {
        "document": "cibil_report",
        "key_values": {},
        "tables": [],
        "text": "",
        "issues": [],
        "valid": True
    }

    try:
        with open(file_path, "rb") as f:
            poller = document_client.begin_analyze_document("prebuilt-document", document=f)
            result = poller.result()

        full_text = " ".join([line.content for page in result.pages for line in page.lines])
        result_json["text"] = full_text

        for kv in result.key_value_pairs:
            if kv.key and kv.value:
                key = kv.key.content.strip()
                value = kv.value.content.strip()
                result_json["key_values"][key] = value

        for table in result.tables:
            table_data = []
            for row_idx in range(table.row_count):
                row_data = {}
                for col_idx in range(table.column_count):
                    cell = next((c for c in table.cells if c.row_index == row_idx and c.column_index == col_idx), None)
                    if cell:
                        row_data[f"col_{col_idx}"] = cell.content
                table_data.append(row_data)
            result_json["tables"].append(table_data)

        # Basic validation
        if not any(keyword in full_text.lower() for keyword in ["cibil", "score", "credit report"]):
            result_json["issues"].append("Does not appear to be a CIBIL report.")

        if result_json["issues"]:
            result_json["valid"] = False

    except Exception as e:
        result_json["valid"] = False
        result_json["issues"].append(f"Error analyzing CIBIL report: {str(e)}")

    return result_json

#-------------------------------------------------------------------------

#--------- RAG -----------------------------------------------------------


def analyze_documents(user):
    print("inside ana doc")
    questions = [
        {
            "key": "net_income_check",
            "question": "What is the user's net monthly income based on payslips?",
            "rule": "Net monthly income must be above ₹25,000 for eligibility."
        },
        {
            "key": "salary_consistency",
            "question": "Is the salary consistent across the submitted payslips?",
            "rule": "Salary must be roughly the same each month to ensure job stability."
        },
        {
            "key": "pan_match",
            "question": "Does the PAN number match across payslips, bank, and CIBIL documents?",
            "rule": "PAN mismatch is a red flag."
        },
        {
            "key": "cibil_score",
            "question": "What is the user's CIBIL score?",
            "rule": "CIBIL score must be 750 or higher for ideal credibility."
        }
    ]
    result = run_rag_embedding_pipeline(user)
    if not result:
        return False
    
    responses = run_all_credimate_questions(user.id, questions)
    if not responses:
        return False
    
    print(responses)

    return True

def run_all_credimate_questions(user_id, questions):
    responses = []

    for q in questions:
        full_prompt = f"""
Use the following rule to answer the question.
Rule: {q['rule']}

Question: {q['question']}
"""
        answer = query_rag_azure(user_id, full_prompt)
        responses.append({
            "key": q["key"],
            "question": q["question"],
            "rule": q["rule"],
            "answer": answer
        })

    return responses

def query_rag_azure(user_id, prompt):

    client = AzureOpenAI(
        base_url=f"{os.getenv('AZURE_OAI_ENDPOINT')}/openai/deployments/{os.getenv('AZURE_OAI_DEPLOYMENT')}/extensions",
        api_key=os.getenv("AZURE_OAI_KEY"),
        api_version="2023-09-01-preview"
    )

    extension_config = {
        "dataSources": [{
            "type": "AzureCognitiveSearch",
            "parameters": {
                "endpoint": os.getenv("AZURE_SEARCH_ENDPOINT"),
                "key": os.getenv("AZURE_SEARCH_KEY"),
                "indexName": os.getenv("AZURE_SEARCH_INDEX"),
                "filter": f"user_id eq '{user_id}'"
            }
        }]
    }

    response = client.chat.completions.create(
        model=os.getenv("AZURE_OAI_DEPLOYMENT"),
        temperature=0.8,
        max_tokens=4000,
        messages=[
            {"role": "system", "content": "You are a financial assistant helping analyze KYC and financial documents. Apply rules strictly."},
            {"role": "user", "content": prompt}
        ],
        extra_body=extension_config
    )

    return response.choices[0].message.content

def chunk_user_context(text, chunk_size=1000, chunk_overlap=100):
    print("chunking")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""]
    )
    return splitter.split_text(text)

def generate_azure_embedding(text):
    print("embed gen")

    client = AzureOpenAI(
        api_key=os.getenv("AZURE_OAI_KEY"),
        azure_endpoint=os.getenv("AZURE_OAI_ENDPOINT"),
        api_version="2023-12-01"
    )
    print("error here before")

    response = client.embeddings.create(
        model=os.getenv("AZURE_OAI_EMBEDDING_DEPLOYMENT"),  # e.g. "text-embedding-ada-002"
        input=[text]
    )
    print("error here after")
    return response['data'][0]['embedding']

def upload_chunks_to_search(chunks, user_id):
    print("chunk search")
    search_client = SearchClient(
        endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
        index_name=os.getenv("AZURE_SEARCH_INDEX"),
        credential=AzureKeyCredential(os.getenv("AZURE_SEARCH_KEY"))
    )

    documents = []
    for chunk in chunks:
        embedding = generate_azure_embedding(chunk)
        documents.append({
            "id": str(uuid.uuid4()),
            "chunk": chunk,
            "text_vector": embedding,
            "user_id": str(user_id),
            "parent_id": str(user_id),
            "text_vector": None,
        })

    result = search_client.upload_documents(documents)
    print(result, end="\n\nresult\n\n")
    return result

def run_rag_embedding_pipeline(user):
    print("embedding pipeline")
    try:
        context_path = f"User_{user.id}_{user.first_name}/context/combined_context.txt"
        blob_client = container_client.get_blob_client(context_path)

        if not blob_client.exists():
            return False, "No combined context found for embedding."

        context_text = blob_client.download_blob().readall().decode("utf-8")
        chunks = chunk_user_context(context_text)
        upload_chunks_to_search(chunks, user.id)

        return True, f"RAG embedding completed for user {user.first_name} ({len(chunks)} chunks indexed)."
    except Exception as e:
        return False, f"RAG embedding failed: {str(e)}"
    
# --------------------------------------------------------------------


def run_final_evaluation(user):
    return True

def generate_report(user):
    return True

def wrapup(user):
    return True


    