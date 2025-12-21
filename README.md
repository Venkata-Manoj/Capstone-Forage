# CapstoneForge - AI-Powered Capstone Report Generation System

![CapstoneForge](https://img.shields.io/badge/AI-Powered-blue) ![Status](https://img.shields.io/badge/Status-Production%20Ready-green)

**CapstoneForge** is a complete, production-ready AI-powered system that automatically generates institution-compliant capstone reports (15+ pages) from reference files and user-provided titles.

## 🌟 Features

### Core Capabilities

- **Multi-Format Support**: Upload PDF, DOCX, PPTX, PNG, JPG files
- **Intelligent Extraction**: Automatic heading detection, section extraction, OCR fallback
- **RAG Pipeline**: Semantic chunking, embeddings, FAISS vector store
- **Dual AI Support**: OpenAI GPT-4 + Google Gemini with automatic fallback
- **Complete Reports**: 15+ sections including cover, abstract, all chapters, viva Q&A
- **Multiple Formats**: Export to DOCX and PDF

### Report Sections Generated

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

## 🚀 Installation

### 1. Clone Repository

```bash
cd cap_builder
```

### 2. Backend Setup

#### Install Python Dependencies

```bash
# Activate virtual environment
.\\venv\\Scripts\\activate

# Install dependencies
pip install -r backend\\requirements.txt
```

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

#### Setup Supabase Database

1. Go to your Supabase project
2. Navigate to SQL Editor
3. Run the SQL script from `backend/schema.sql`

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Return to root
cd ..
```

## 🎯 Usage

### Start Backend Server

```bash
# Activate venv
.\\venv\\Scripts\\activate

# Start FastAPI server
cd backend
python main.py
```

Backend will run on: `http://localhost:8000`

### Start Frontend Development Server

```bash
cd frontend
npm run dev
```

Frontend will run on: `http://localhost:3000`

### Generate a Report

1. **Open Browser**: Navigate to `http://localhost:3000`
2. **Go to Generate**: Click "Generate Report" or navigate to `/generate`
3. **Upload File**: Drag and drop or select your reference file (PDF, DOCX, PPTX, image)
4. **Fill Details**: Enter project title and optional metadata
5. **Generate**: Click "Generate Report"
6. **Monitor Progress**: System will process and generate report
7. **Download**: Go to "My Reports" and download DOCX/PDF

## 📁 Project Structure

```
cap_builder/
├── backend/
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # Configuration management
│   ├── database.py             # Supabase client
│   ├── requirements.txt        # Python dependencies
│   ├── schema.sql              # Database schema
│   ├── extractors/             # Document extraction
│   │   ├── pdf_extractor.py
│   │   ├── docx_extractor.py
│   │   ├── pptx_extractor.py
│   │   └── image_extractor.py
│   ├── rag/                    # RAG pipeline
│   │   ├── chunker.py
│   │   ├── embedder.py
│   │   ├── vector_store.py
│   │   └── retriever.py
│   ├── generators/             # AI generation
│   │   ├── ai_client.py        # Dual AI support
│   │   ├── section_generator.py
│   │   └── viva_generator.py
│   ├── document_builder/       # Document creation
│   │   ├── docx_builder.py
│   │   └── pdf_converter.py
│   └── routes/                 # API endpoints
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
├── uploads/                    # Uploaded files
├── generated/                  # Generated reports
├── faiss_indexes/              # Vector store indexes
└── .env                        # Environment variables
```

## 🔧 API Endpoints

### Upload File

```http
POST /api/upload
Content-Type: multipart/form-data

file: <file>
title: string
student_name: string (optional)
roll_no: string (optional)
faculty_name: string (optional)
```

### Generate Report

```http
POST /api/generate
Content-Type: application/json

{
  "file_id": "uuid",
  "title": "string",
  "student_name": "string",
  "roll_no": "string",
  "department": "string",
  "institution": "string",
  "faculty_name": "string",
  "year": 2024
}
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

## 🎨 UI Features

- **Glassmorphism Design**: Modern, premium UI with backdrop blur
- **Gradient Animations**: Smooth, eye-catching animations
- **Drag-and-Drop Upload**: Intuitive file upload
- **Real-time Status**: Live progress tracking
- **Responsive Design**: Works on all screen sizes

## ⚙️ Configuration

### AI Provider Priority

The system tries providers in this order:

1. OpenAI (if API key provided)
2. Google Gemini (if API key provided)

If one fails, it automatically falls back to the other.

### Embedding Model

Default: `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions)

### Chunk Size

Default: 800 characters with 200 character overlap

### PDF Conversion

Primary: LibreOffice (better quality)
Fallback: docx2pdf

## 🐛 Troubleshooting

### Tesseract Not Found

```bash
# Install Tesseract OCR from:
# https://github.com/UB-Mannheim/tesseract/wiki

# Update path in .env:
TESSERACT_CMD=C:\\Program Files\\Tesseract-OCR\\tesseract.exe
```

### LibreOffice Not Found

```bash
# Install LibreOffice from:
# https://www.libreoffice.org/download/

# Update path in .env:
LIBREOFFICE_PATH=C:\\Program Files\\LibreOffice\\program\\soffice.exe
```

### AI API Errors

- Check API keys in `.env`
- Verify API quotas/limits
- Check internet connection
- System will automatically fallback to alternate provider

### Supabase Connection Issues

- Verify `SUPABASE_URL` and `SUPABASE_KEY`
- Check if database schema is created
- Verify RLS policies allow operations

## 📊 Performance

- **Upload**: < 30 seconds for 50MB files
- **Extraction**: 1-2 minutes for 50-page documents
- **Generation**: 5-10 minutes for complete report
- **Total**: ~10-15 minutes end-to-end

## 🔒 Security

- JWT-based authentication (ready for implementation)
- Row Level Security (RLS) in Supabase
- File type validation
- File size limits (50MB default)
- API rate limiting (recommended for production)

## 🚧 Limitations (V1)

- No built-in plagiarism detection
- No direct LMS integration
- No multi-user authentication (single-user mode)
- Local file storage (use S3 for production)

## 🔮 Future Enhancements

- [ ] Multi-language support
- [ ] Custom template builder
- [ ] Faculty review workflow
- [ ] Version control with Git integration
- [ ] Plagiarism API integration
- [ ] AI-powered diagram generation
- [ ] Direct LMS submission

## 📝 License

This project is for educational purposes.

## 🤝 Contributing

This is a capstone project. Contributions welcome after initial release.

## 📧 Support

For issues and questions, please check the troubleshooting section above.

---

**Built with ❤️ using AI, Python, React, and modern web technologies**
#   C a p s t o n e - F o r a g e  
 