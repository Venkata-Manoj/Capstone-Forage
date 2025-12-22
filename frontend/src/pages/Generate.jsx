import { useState } from 'react'
import axios from 'axios'
import { useNavigate } from 'react-router-dom'
import FilePreview from '../components/FilePreview'
import ProgressBar from '../components/ProgressBar'

export default function Generate() {
    const navigate = useNavigate()
    const [formData, setFormData] = useState({
        title: '',
        student_name: '',
        roll_no: '',
        department: '',
        faculty_name: '',
        submission_date: new Date().toISOString().split('T')[0]
    })
    const [file, setFile] = useState(null)
    const [uploading, setUploading] = useState(false)
    const [generating, setGenerating] = useState(false)
    const [uploadProgress, setUploadProgress] = useState(0)
    const [progressMessage, setProgressMessage] = useState('')
    const [error, setError] = useState(null)
    const [isDragOver, setIsDragOver] = useState(false)

    const handleInputChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        })
    }

    const handleFileChange = (e) => {
        const selectedFile = e.target.files[0]
        if (selectedFile) {
            setFile(selectedFile)
            setError(null)
        }
    }

    const handleDrop = (e) => {
        e.preventDefault()
        setIsDragOver(false)
        const droppedFile = e.dataTransfer.files[0]
        if (droppedFile) {
            setFile(droppedFile)
            setError(null)
        }
    }

    const handleDragOver = (e) => {
        e.preventDefault()
        setIsDragOver(true)
    }

    const handleDragLeave = (e) => {
        e.preventDefault()
        setIsDragOver(false)
    }

    const handleRemoveFile = () => {
        setFile(null)
        setError(null)
    }

    const handleSubmit = async (e) => {
        e.preventDefault()
        setError(null)

        if (!file) {
            setError('Please select a file')
            return
        }

        if (!formData.title) {
            setError('Please enter a project title')
            return
        }

        try {
            // Step 1: Upload file
            setUploading(true)
            setUploadProgress(10)
            setProgressMessage('Uploading file...')

            const uploadFormData = new FormData()
            uploadFormData.append('file', file)
            uploadFormData.append('title', formData.title)
            uploadFormData.append('student_name', formData.student_name)
            uploadFormData.append('roll_no', formData.roll_no)
            uploadFormData.append('faculty_name', formData.faculty_name)

            setUploadProgress(30)
            const uploadResponse = await axios.post('/api/upload', uploadFormData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            })

            const fileId = uploadResponse.data.file_id
            setUploadProgress(60)
            setProgressMessage(`File uploaded! Extracted ${uploadResponse.data.stats.total_chunks} chunks`)

            // Step 2: Generate report
            setUploadProgress(70)
            setUploading(false)
            setGenerating(true)
            setProgressMessage('Initializing AI generation...')

            // Extract year from submission date
            const year = new Date(formData.submission_date).getFullYear()

            setUploadProgress(80)
            const generateResponse = await axios.post('/api/generate', {
                file_id: fileId,
                ...formData,
                year: year
            })

            const reportId = generateResponse.data.report_id
            setUploadProgress(100)
            setProgressMessage('Report generation started successfully!')

            // Redirect to reports page
            setTimeout(() => {
                navigate('/reports')
            }, 2000)

        } catch (err) {
            console.error('Error:', err)
            setError(err.response?.data?.detail || 'An error occurred')
            setUploading(false)
            setGenerating(false)
            setUploadProgress(0)
            setProgressMessage('')
        }
    }

    return (
        <div className="max-w-4xl mx-auto px-4 py-8">
            <div className="text-center mb-12 animate-fade-in">
                <h1 className="text-5xl font-bold mb-4 gradient-text">
                    Generate Capstone Report
                </h1>
                <p className="text-lg" style={{ color: 'var(--color-text-secondary)' }}>
                    Upload your reference files and let AI create a comprehensive capstone report
                </p>
            </div>

            <form onSubmit={handleSubmit} className="glass-strong p-8 rounded-2xl animate-slide-up">
                {/* File Upload */}
                <div className="mb-8">
                    <label className="block text-sm font-semibold mb-3" style={{ color: 'var(--color-text)' }}>
                        Reference File *
                    </label>

                    {!file ? (
                        <div
                            onDrop={handleDrop}
                            onDragOver={handleDragOver}
                            onDragLeave={handleDragLeave}
                            className={`
                                border-2 border-dashed rounded-2xl p-12 text-center 
                                transition-all duration-300 cursor-pointer
                                ${isDragOver ? 'drag-over scale-105' : 'border-gray-300 dark:border-gray-600'}
                                hover:border-primary-500 hover:bg-opacity-50
                            `}
                            style={{
                                borderColor: isDragOver ? 'var(--color-primary)' : undefined,
                                backgroundColor: isDragOver ? 'rgba(99, 102, 241, 0.05)' : undefined
                            }}
                        >
                            <input
                                type="file"
                                onChange={handleFileChange}
                                accept=".pdf,.docx,.pptx,.png,.jpg,.jpeg"
                                className="hidden"
                                id="file-upload"
                            />
                            <label htmlFor="file-upload" className="cursor-pointer">
                                <div className="text-7xl mb-4 animate-bounce">📁</div>
                                <p className="text-xl font-semibold mb-2" style={{ color: 'var(--color-text)' }}>
                                    Drop your file here or click to browse
                                </p>
                                <p className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>
                                    Supports PDF, DOCX, PPTX, PNG, JPG (Max 50MB)
                                </p>
                            </label>
                        </div>
                    ) : (
                        <FilePreview file={file} onRemove={handleRemoveFile} />
                    )}
                </div>

                {/* Project Title */}
                <div className="mb-6">
                    <label className="block text-sm font-semibold mb-2" style={{ color: 'var(--color-text)' }}>
                        Project Title *
                    </label>
                    <input
                        type="text"
                        name="title"
                        value={formData.title}
                        onChange={handleInputChange}
                        className="input-field"
                        placeholder="e.g., AI-Based Traffic Management System"
                        required
                    />
                </div>

                {/* Student Details */}
                <div className="grid md:grid-cols-2 gap-6 mb-6">
                    <div>
                        <label className="block text-sm font-semibold mb-2" style={{ color: 'var(--color-text)' }}>
                            Student Name(s)
                        </label>
                        <input
                            type="text"
                            name="student_name"
                            value={formData.student_name}
                            onChange={handleInputChange}
                            className="input-field"
                            placeholder="Your name"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-semibold mb-2" style={{ color: 'var(--color-text)' }}>
                            Registration Number
                        </label>
                        <input
                            type="text"
                            name="roll_no"
                            value={formData.roll_no}
                            onChange={handleInputChange}
                            className="input-field"
                            placeholder="e.g., 21CS001"
                        />
                    </div>
                </div>

                {/* Course Name */}
                <div className="mb-6">
                    <label className="block text-sm font-semibold mb-2" style={{ color: 'var(--color-text)' }}>
                        Course Name and Code
                    </label>
                    <input
                        type="text"
                        name="department"
                        value={formData.department}
                        onChange={handleInputChange}
                        className="input-field"
                        placeholder="e.g., Computer Science (CS101)"
                    />
                </div>

                {/* Faculty and Date */}
                <div className="grid md:grid-cols-2 gap-6 mb-8">
                    <div>
                        <label className="block text-sm font-semibold mb-2" style={{ color: 'var(--color-text)' }}>
                            Supervisor/Advisor Name
                        </label>
                        <input
                            type="text"
                            name="faculty_name"
                            value={formData.faculty_name}
                            onChange={handleInputChange}
                            className="input-field"
                            placeholder="Faculty name"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-semibold mb-2" style={{ color: 'var(--color-text)' }}>
                            Date of Submission
                        </label>
                        <input
                            type="date"
                            name="submission_date"
                            value={formData.submission_date}
                            onChange={handleInputChange}
                            className="input-field"
                        />
                    </div>
                </div>

                {/* Error Message */}
                {error && (
                    <div className="mb-6 p-4 rounded-xl animate-fade-in" style={{
                        backgroundColor: 'rgba(239, 68, 68, 0.1)',
                        border: '1px solid rgba(239, 68, 68, 0.3)',
                        color: 'var(--color-error)'
                    }}>
                        <div className="flex items-center gap-2">
                            <span className="text-xl">⚠️</span>
                            <span className="font-medium">{error}</span>
                        </div>
                    </div>
                )}

                {/* Progress */}
                {(uploading || generating) && (
                    <div className="mb-6 p-6 rounded-xl glass animate-fade-in">
                        <div className="flex items-center gap-3 mb-4">
                            <div className="animate-spin text-2xl">
                                {uploading ? '⚙️' : '🤖'}
                            </div>
                            <span className="font-semibold text-lg" style={{ color: 'var(--color-text)' }}>
                                {progressMessage}
                            </span>
                        </div>
                        <ProgressBar
                            progress={uploadProgress}
                            variant={generating ? 'primary' : 'success'}
                            showPercentage={true}
                        />
                    </div>
                )}

                {/* Submit Button */}
                <button
                    type="submit"
                    disabled={uploading || generating}
                    className="btn-primary w-full text-lg py-4 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-3"
                >
                    {uploading ? (
                        <>
                            <span className="animate-spin">⏳</span>
                            <span>Uploading...</span>
                        </>
                    ) : generating ? (
                        <>
                            <span className="animate-spin">🤖</span>
                            <span>Generating...</span>
                        </>
                    ) : (
                        <>
                            <span>🚀</span>
                            <span>Generate Report</span>
                        </>
                    )}
                </button>

                {/* Help Text */}
                <p className="mt-4 text-center text-sm" style={{ color: 'var(--color-text-secondary)' }}>
                    Generation typically takes 10-15 minutes. You'll be redirected to view your report.
                </p>
            </form>
        </div>
    )
}
