# SOP Query AI  
**A Retrieval-Augmented Q&A Chatbot for Safety SOP Documents**

---

## 🚀 Overview

SOP Query AI is an AI-powered chatbot designed to help users quickly retrieve information from large and complex Standard Operating Procedure (SOP) documents.

In industries like power stations, operators rely on extensive manuals for safety and operations. These documents are often hundreds of pages long, making manual searching slow, inefficient, and prone to error.

This project enables users to ask natural language questions and receive accurate, source-backed answers directly from SOP documents.

---

## 💡 Problem

- SOP manuals are long and complex  
- Manual searching is time-consuming  
- Important procedures can be missed  
- Delays can increase operational and safety risks  

---

## 🧠 Solution

We built a Retrieval-Augmented Generation (RAG) chatbot that:

- Accepts natural language queries  
- Retrieves relevant content from SOP documents  
- Generates answers grounded strictly in retrieved data  
- Provides document names and page numbers for verification  

The system prioritizes **accuracy, traceability, and safety**.

---

## ⚙️ Key Features

- 🔍 Hybrid Search (Vector + Keyword)  
- 📄 Multi-format support (PDF, DOCX, XLSX)  
- 🧩 Structure-aware chunking (preserves SOP steps)  
- 🖼️ Multimodal retrieval (text + diagrams)  
- 📌 Source citations with page references  
- 🛡️ Hallucination control via strict grounding  

---

## 🏗️ System Architecture

### 1. Document Indexing (Offline)
- Upload documents to storage  
- Split into structured chunks  
- Generate embeddings  
- Store in search index  

### 2. Query Processing (Online)
- Convert user query into embedding  
- Perform hybrid retrieval  
- Assemble context  
- Generate response using LLM  

---

## 🧪 Evaluation

- **Precision@5:** ~0.94  
- **Faithfulness:** Majority of responses fully grounded  

The system demonstrates strong retrieval accuracy and reliability for SOP-based queries.

---

## 🛠️ Tech Stack

**Backend**
- Python, FastAPI  

**Frontend**
- Streamlit  

**AI / NLP**
- OpenAI (GPT-4o-mini, embeddings)  

**Cloud**
- Azure Blob Storage  
- Azure AI Search  

**Data Processing**
- PyMuPDF, python-docx, pandas  

---

## 📂 Project Structure
