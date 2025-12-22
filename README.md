# CapstoneForge - AI-Powered Capstone Report Generation System

![CapstoneForge](https://img.shields.io/badge/AI-Powered-blue)
![Status](https://img.shields.io/badge/Status-Production%20Ready-green)
![Backend](https://img.shields.io/badge/Backend-FastAPI-blue)
![Frontend](https://img.shields.io/badge/Frontend-React%2018-blue)
![License](https://img.shields.io/badge/License-Educational-lightgrey)

---

**CapstoneForge** is a complete, production-ready AI-powered system that automatically generates institution-compliant capstone reports (15+ pages) from reference files and user-provided titles.

---

## 🌟 Features

### Core Capabilities

- **Multi-Format Support**: Upload PDF, DOCX, PPTX, PNG, JPG files
- **Intelligent Extraction**: Automatic heading detection, section extraction, OCR fallback
- **RAG Pipeline**: Semantic chunking, embeddings, FAISS vector store
- **Dual AI Support**: OpenAI GPT-4 + Google Gemini with automatic fallback
- **Complete Reports**: 15+ sections including cover, abstract, all chapters, viva Q&A
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
18. Viva Q&A Pack (15+ questions with answers)

---

## 🏗️ Architecture

### Backend (FastAPI + Python)

- **Document Extraction**: PyPDF2, python-docx, python-pptx, Tesseract OCR  
- **RAG Pipeline**: sentence-transformers, FAISS  
- **AI Generation**: OpenAI API, Google Gemini API  
- **Document Building**: python-docx, LibreOffice/docx2pdf  
- **Database**: Supabase (PostgreSQL)  
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
- Supabase account (free tier)
- OpenAI API key OR Google Gemini API key

### Optional

- Redis (for advanced task queuing)

---

## 🚀 Installation

### 1. Clone Repository

```bash
cd cap_builder
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
# Supabase
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_role_key

# AI API Keys (provide at least one)
OPENAI_API_KEY=your_openai_api_key
GEMINI_API_KEY=your_gemini_api_key

# JWT Secret
SECRET_KEY=your_random_secret_key_here

# Paths (update if different)
LIBREOFFICE_PATH=C:\\Program Files\\LibreOffice\\program\\soffice.exe
TESSERACT_CMD=C:\\Program Files\\Tesseract-OCR\\tesseract.exe
```

---

#### Setup Supabase Database

1. Go to your Supabase project
2. Navigate to SQL Editor
3. Run the SQL script from `backend/schema.sql`

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

# Start FastAPI server
cd backend
python main.py
```

Backend will run on:
`http://localhost:8000`

---

### Start Frontend Development Server

```bash
cd frontend
npm run dev
```

Frontend will run on:
`http://localhost:3000`

---

### Generate a Report

1. **Open Browser**: Navigate to `http://localhost:3000`
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
│   ├── schema.sql
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

## 🔧 API Endpoints

### Upload File

```http
POST /api/upload
Content-Type: multipart/form-data
```

### Generate Report

```http
POST /api/generate
Content-Type: application/json
```

### Download Report

```http
GET /api/download/{report_id}?format=docx
GET /api/download/{report_id}?format=pdf
```

### List Reports

```http
GET /api/reports
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

## 🔒 Security

* JWT-based authentication (ready for implementation)
* Supabase Row Level Security (RLS)
* File type and size validation
* API rate limiting (recommended)

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

This is a capstone project. Contributions welcome after initial release.

---

## 📧 Support

Please refer to the troubleshooting section above for common issues.

---

**Built with ❤️ using AI, Python, React, and modern web technologies**

```
