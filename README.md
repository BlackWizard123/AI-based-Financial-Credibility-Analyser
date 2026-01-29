

<img width="3600" height="800" alt="logo" src="https://github.com/user-attachments/assets/bbb5a9f5-3213-490c-826b-411e4fd97767" />

# 🏦 AI-Powered KYC & Financial Credibility Assessment Platform

## 📌 Executive Summary
This project addresses a critical bottleneck in digital onboarding and financial assessment using Microsoft Azure’s AI ecosystem. The platform automates KYC document validation, detects document tampering, and evaluates financial credibility using intelligent, rule-driven and LLM-based analysis.

The system produces a transparent, structured PDF report containing identity verification results, financial metrics, risk indicators, and eligibility insights—enabling faster, safer, and smarter decision-making for BFSI institutions.

---

## ❗ Problem Statement
Manual KYC and income verification processes are:

* **Time-consuming** and operationally expensive
* **Error-prone** due to human intervention
* **Highly vulnerable** to document tampering and fraud

Financial institutions struggle to reliably verify documents such as PAN, Aadhaar, CIBIL reports, payslips, Form-16, and bank statements, while ensuring data consistency and authenticity at scale.

---

## 🎯 Objective
Build a secure, end-to-end AI-driven platform that:

1. **Validates** multiple KYC and financial documents
2. **Detects** document tampering via metadata inspection
3. **Uses OCR and AI** for deep financial analysis
4. **Generates** a downloadable PDF report with actionable insights

---

# 🧠 Technical Architecture

## 🧩 Logical Flow
```
Frontend (Flask)
     ↓  
Azure Blob Storage (Document Upload)  
     ↓  
Tamper Detection & Metadata Analysis
     ↓   
Azure Document Intelligence (OCR & Template Validation)  
     ↓  
Embedding Generation
     ↓  
Azure AI Search (Vector Retrieval)  
     ↓  
LLM-based Financial & Credibility Analysis
     ↓  
PDF Report Generator
```

## 🤖 Technology Justification

| Component | Reason |
| :--- | :--- |
| **Flask** | Lightweight and flexible; enables rapid frontend-backend integration and easy deployment as a microservice. |
| **Azure Blob Storage** | Provides secure, scalable, and durable storage for unstructured document uploads with built-in encryption and SAS token support. |
| **Azure AI Document Intelligence** | Industry-leading OCR and layout analysis; handles prebuilt models for IDs (PAN/Aadhaar) and complex table extraction from financial statements. |
| **Azure AI Search** | Fully managed vector database for high-performance retrieval; unifies keyword and vector search (hybrid search) to reduce LLM hallucinations. |
| **LLM (Azure OpenAI / Local)** | Provides context-aware reasoning for financial eligibility and risk assessment; ensures data is grounded in the retrieved document context. |
| **WeasyPrint / PDFKit** | Converts HTML/CSS templates into structured, professional PDF reports; supports modern CSS (Flexbox) for high-quality branding. |

---

# 🏗️ System Architecture

<img width="2029" height="914" alt="diagram-export-6-9-2025-12_59_58-PM (1)" src="https://github.com/user-attachments/assets/eab6a200-efc7-46af-83bf-bc61d0832963" />

---

# ⚙️ Execution & Setup Instructions

### 1️⃣ Azure Setup
* Provision Azure services (**Blob Storage**, **AI Foundry**, **AI Search**)
* Ensure **API access keys** and **Endpoints** are generated and saved

### 2️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 3️⃣ Configure Environment Variables
```.env
AZURE_STORAGE_CONNECTION_STRING = ""
AZURE_FORMRECOGNIZER_ENDPOINT = ""
AZURE_FORMRECOGNIZER_KEY = ""

AZURE_OAI_EMBEDDING_DEPLOYMENT = ""
AZURE_OAI_ENDPOINT = ""
AZURE_OAI_KEY = ""
AZURE_OAI_DEPLOYMENT = ""

AZURE_SEARCH_ENDPOINT = ""
AZURE_SEARCH_KEY = ""
AZURE_SEARCH_INDEX = ""
```

### 4️⃣ Run the Application
```bash
python app.py
```

### 5️⃣ Access the App
Open your browser and navigate to:
```bash
http://127.0.0.1:5000
```

---

# 🔄 Automated Backend Workflow

### 📥 Document Upload
Accepts multiple formats including **PAN**, **Aadhaar**, **CIBIL**, **Bank Statements**, **Payslips**, and **Form-16**.

### 🔒 Tamper Detection
Performs deep **metadata inspection** using `PyPDF2` and `PyExif` to identify software inconsistencies or unauthorized edits.

### 🧾 Template Validation
Executes **layout and structural checks** using **Azure AI Foundry** to ensure the uploaded documents match official government or banking templates.

### 👁️ OCR & Field Extraction
Extracts critical data points such as **Name**, **salary**, and **account details** via `Tesseract` and `pdfplumber` for structured processing.

### 📊 Financial Metric Computation
Applies **rule-based and formula-driven logic** to calculate key ratios:
* **FOIR** (Fixed Obligation to Income Ratio)
* **DSCR** (Debt Service Coverage Ratio)
* **Trend Analysis** (Income stability and spending patterns)

### 🤖 LLM Analysis
Performs **credibility and eligibility evaluation** using **GPT-4** to interpret financial health beyond raw numbers.

### 📄 PDF Report Generation
Consolidates findings into a **Markdown-based summary** rendered into a professional report via **WeasyPrint**.

---

# 🎥 System Walkthrough (Demo Video)

Click the image below to watch the full application walkthrough 👇 
**(Open in new tab)**

[![AI-Powered KYC Demo](https://img.youtube.com/vi/Xn0EQ41-b-M/hqdefault.jpg)](https://youtu.be/Xn0EQ41-b-M)

---

## 🗺️ UI Flow Overview

### Step 1: Registration / Login
* **User signs up** using name, email, and password.
* Secure authentication layer to protect sensitive financial data.

### Step 2: Document Upload
* **Dedicated slots** for each specific document type (PAN, Aadhaar, etc.).
* **Live status indicators** to show upload progress and file receipt.

### Step 3: Validation Progress View
Real-time validation steps with completion ticks to provide transparency:
* **PAN Validation** ✅
* **Aadhaar Match** ✅
* **CIBIL Integrity** ✅
* **Income Verification** ✅

### Step 4: Final Report Page
* **Financial metrics dashboard** showing key ratios and credibility scores at a glance.
* **One-click PDF download** for the comprehensive assessment report.

---

# 📊 Sample Output Metrics

| Metric | Value |
| :--- | :--- |
| **FOIR** (Fixed Obligation to Income Ratio) | 22% |
| **DSCR** (Debt Service Coverage Ratio) | 2.1 |
| **CIBIL Score** | 752 |
| **Avg Bank Balance** | ₹48,000 |
| **Eligibility Score** | 8.5 / 10 |

---

# ✨ Key Features
* **Categorized document upload** – Simplified handling for various financial and ID formats.
* **Metadata inspection & layout validation** – Instant fraud detection and document verification.
* **Automated financial metric extraction** – Programmatic parsing of bank statements and payslips.
* **LLM-based eligibility evaluation** – Intelligent assessment of financial credibility.
* **Professional PDF report generation** – Instant, structured reports for decision-makers.

---

# 🚀 Future Enhancements
* **DigiLocker Integration** – Fetch verified documents directly via official APIs.
* **UPI / Bank APIs** – Transition to live income and real-time balance verification.
* **Aadhaar Biometric Validation** – Implement real-time identity checks via biometric data.
* **RAG-based Q&A** – Enable context-aware questioning on the uploaded document corpus.
* **Audit Trails & Logs** – Provide full explainability and traceability for banking compliance.
* **SaaS Scaling** – Offer a white-label onboarding solution for global BFSI institutions.

---

# 💼 Business Potential
* **Applicable to banks, NBFCs, and fintech platforms.**
* **Enables automated loan approval workflows**, significantly decreasing turnaround time.
* **Reduces fraud risk** and operational overhead costs through AI automation.

---

# 📈 Expected Outcomes
* **60–80% reduction** in manual verification effort.
* **Faster and more accurate** credit decisions based on objective data.
* **Ready-to-use onboarding reports** formatted specifically for institutional requirements.

---

# 🌍 Real-World Impact
* **Onboarding time reduced** from days to minutes.
* **Fraud prevention** at the initial upload stage, protecting the institution.
* **Lending driven by intelligent financial profiles** rather than just static scores.
* **Transparent, human-readable reports** that simplify complex data for end users.

---

# 📬 Contact
For queries, collaboration, or enhancements, feel free to reach out.

⭐ **If you find this project useful, don’t forget to star the repository!**






