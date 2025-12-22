# CapstoneForge - AI-Powered Capstone Report Generation System

![CapstoneForge](https://img.shields.io/badge/AI-Powered-blue)
![Status](https://img.shields.io/badge/Status-Production%20Ready-green)
![Backend](https://img.shields.io/badge/Backend-FastAPI-blue)
![Frontend](https://img.shields.io/badge/Frontend-React%2018-blue)
![License](https://img.shields.io/badge/License-Educational-lightgrey)

---

**CapstoneForge** is a developing AI-powered system that automatically generates institution-compliant capstone reports (15+ pages) from reference files and user-provided titles. (Currently Limited to 1 institution)

---

## 🌟 Features

### Core Capabilities

- **Multi-Format Support**: Upload PDF, DOCX, PPTX, PNG, JPG files
- **Intelligent Extraction**: Automatic heading detection, section extraction, OCR fallback
- **RAG Pipeline**: Semantic chunking, embeddings, FAISS vector store
- **Multi-Model AI Support**: Ollama with automatic fallback
- **Complete Reports**: 15+ sections including cover, abstract, all chapters
- **Multiple Formats**: Export to DOCX and PDF

---

## 📘 Report Sections Generated

1. Cover Page  
2. Declaration  
3. Bonafide Certificate  
4. Acknowledgement  
5. Abstract  
6. Table of Contents  
7. Introduction  
8. Literature Review  
9. System Analysis  
10. System Design  
11. Methodology  
12. Implementation  
13. Results and Discussion  
14. Conclusion  
15. Future Enhancements  
16. References  
17. Appendix  

---

## 🏗️ Architecture

### Backend (FastAPI + Python)

- **Document Extraction**: PyPDF2, python-docx, python-pptx, Tesseract OCR  
- **RAG Pipeline**: sentence-transformers, FAISS  
- **AI Generation**: Ollama 
- **Document Building**: python-docx, LibreOffice/docx2pdf  
- **Storage**: Local filesystem (production: S3/MinIO)

### Frontend (React + Vite)

- **Framework**: React 18, Vite  
- **Routing**: React Router  
- **Styling**: Tailwind CSS with glassmorphism  
- **HTTP Client**: Axios  

---

## 📋 Prerequisites

### Required

- Python 3.11+
- Node.js 18+
- Tesseract OCR
- LibreOffice (for PDF conversion)
- Ollama

### Optional

- Redis (for advanced task queuing)

---

## 🚀 Installation

### 1. Clone Repository

```bash
cd Capstone-Forage
````

---

### 2. Backend Setup

#### Install Python Dependencies

```bash
# Activate virtual environment
.\\venv\\Scripts\\activate

# Install dependencies
pip install -r backend\\requirements.txt
```

---

#### Configure Environment Variables

```bash
# Copy example env file
copy .env.example .env

# Edit .env and add your keys
notepad .env
```

**Required Environment Variables:**

```env

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:[sample]
OLLAMA_MODEL=model_1
OLLAMA_MODEL_FALLBACK_1=model_2
OLLAMA_MODEL_FALLBACK_2=model_3

# AI Settings
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
MAX_TOKENS=8000
TEMPERATURE=0.7

# File Upload Settings
MAX_UPLOAD_SIZE=52428800
UPLOAD_DIR=./uploads
GENERATED_DIR=./generated

# Vector Store
FAISS_INDEX_DIR=./faiss_indexes

# LibreOffice Path (for PDF conversion)
LIBREOFFICE_PATH=C:\\Program Files\\LibreOffice\\program\\soffice.exe

# CORS Settings
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# Tesseract OCR Path
TESSERACT_CMD=C:\\Program Files\\Tesseract-OCR\\tesseract.exe

```

---

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Return to root
cd ..
```

---

## 🎯 Usage

### Start Backend Server

```bash
# Activate venv
.\\venv\\Scripts\\activate


cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend will run on:
`[http://localhost:8000](http://0.0.0.0:8000)`

---

### Start Frontend Development Server

```bash
cd frontend
npm run dev
```

Frontend will run on:
` http://localhost:5173/`

---

### Generate a Report

1. **Open Browser**: Navigate to `http://localhost:5173`
2. **Go to Generate**: Click "Generate Report" or navigate to `/generate`
3. **Upload File**: Drag and drop or select your reference file (PDF, DOCX, PPTX, image)
4. **Fill Details**: Enter project title and optional metadata
5. **Generate**: Click "Generate Report"
6. **Monitor Progress**: System will process and generate report
7. **Download**: Go to "My Reports" and download DOCX/PDF

---

## 📁 Project Structure

```
cap_builder/
├── backend/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── requirements.txt
│   ├── extractors/
│   │   ├── pdf_extractor.py
│   │   ├── docx_extractor.py
│   │   ├── pptx_extractor.py
│   │   └── image_extractor.py
│   ├── rag/
│   │   ├── chunker.py
│   │   ├── embedder.py
│   │   ├── vector_store.py
│   │   └── retriever.py
│   ├── generators/
│   │   ├── ai_client.py
│   │   ├── section_generator.py
│   │   └── viva_generator.py
│   ├── document_builder/
│   │   ├── docx_builder.py
│   │   └── pdf_converter.py
│   └── routes/
│       ├── upload.py
│       ├── generate.py
│       └── download.py
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   ├── components/
│   │   │   └── Header.jsx
│   │   └── pages/
│   │       ├── Home.jsx
│   │       ├── Generate.jsx
│   │       └── Reports.jsx
│   ├── package.json
│   └── vite.config.js
├── uploads/
├── generated/
├── faiss_indexes/
└── .env
```
---

## 🎨 UI Features

* Glassmorphism Design
* Gradient Animations
* Drag-and-Drop Upload
* Real-time Status
* Fully Responsive

---

## 📊 Performance

* Upload: < 30 seconds for 50MB files
* Extraction: 1–2 minutes for 50-page documents
* Generation: 5–10 minutes
* Total: ~10–15 minutes end-to-end

---

## 🚧 Limitations (V1)

* No built-in plagiarism detection
* No LMS integration
* Single-user mode
* Local storage only

---

## 🔮 Future Enhancements

* Multi-language support
* Custom template builder
* Faculty review workflow
* Version control
* Plagiarism detection
* AI diagram generation
* LMS integration

---

## 📝 License

This project is for educational purposes.

---

## 🤝 Contributing

This is a self project. Contributions welcome.

---

## 📧 Support

Please refer to the troubleshooting section above for common issues.

---

**Built with ❤️ using AI, Python, React, and modern web technologies**

```


