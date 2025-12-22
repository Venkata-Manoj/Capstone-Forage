import { useState, useEffect } from 'react'
import axios from 'axios'
import StatusBadge from '../components/StatusBadge'
import StatsCard from '../components/StatsCard'

export default function Reports() {
    const [reports, setReports] = useState([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)
    const [searchQuery, setSearchQuery] = useState('')
    const [filterStatus, setFilterStatus] = useState('all')
    const [sortBy, setSortBy] = useState('date')

    useEffect(() => {
        fetchReports()
        // Poll for updates every 5 seconds
        const interval = setInterval(fetchReports, 5000)
        return () => clearInterval(interval)
    }, [])

    const fetchReports = async () => {
        try {
            const response = await axios.get('/api/reports')
            setReports(response.data.reports)
            setLoading(false)
        } catch (err) {
            console.error('Error fetching reports:', err)
            setError('Failed to load reports')
            setLoading(false)
        }
    }

    const handleDownload = async (reportId, format) => {
        try {
            const response = await axios.get(`/api/download/${reportId}?format=${format}`, {
                responseType: 'blob'
            })

            const url = window.URL.createObjectURL(new Blob([response.data]))
            const link = document.createElement('a')
            link.href = url
            link.setAttribute('download', `report.${format}`)
            document.body.appendChild(link)
            link.click()
            link.remove()
        } catch (err) {
            console.error('Download error:', err)
            alert('Failed to download report')
        }
    }

    // Calculate statistics
    const stats = {
        total: reports.length,
        completed: reports.filter(r => r.status === 'completed').length,
        generating: reports.filter(r => r.status === 'generating' || r.status === 'processing').length,
        failed: reports.filter(r => r.status === 'failed').length
    }

    // Filter and sort reports
    const filteredReports = reports
        .filter(report => {
            const matchesSearch = report.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                report.student_name?.toLowerCase().includes(searchQuery.toLowerCase())
            const matchesFilter = filterStatus === 'all' || report.status === filterStatus
            return matchesSearch && matchesFilter
        })
        .sort((a, b) => {
            if (sortBy === 'date') {
                return new Date(b.created_at) - new Date(a.created_at)
            } else if (sortBy === 'title') {
                return a.title.localeCompare(b.title)
            } else if (sortBy === 'status') {
                return a.status.localeCompare(b.status)
            }
            return 0
        })

    if (loading) {
        return (
            <div className="max-w-7xl mx-auto px-4 py-20">
                <div className="text-center">
                    <div className="text-7xl mb-6 animate-bounce">📚</div>
                    <p className="text-2xl font-semibold" style={{ color: 'var(--color-text)' }}>
                        Loading reports...
                    </p>
                    <div className="mt-8 flex justify-center gap-4">
                        {[1, 2, 3].map(i => (
                            <div key={i} className="skeleton h-32 w-64 rounded-xl" />
                        ))}
                    </div>
                </div>
            </div>
        )
    }

    if (error) {
        return (
            <div className="max-w-7xl mx-auto px-4 py-20">
                <div className="text-center">
                    <div className="text-7xl mb-6">⚠️</div>
                    <p className="text-2xl font-semibold" style={{ color: 'var(--color-error)' }}>
                        {error}
                    </p>
                </div>
            </div>
        )
    }

    return (
        <div className="max-w-7xl mx-auto px-4 py-8">
            {/* Header */}
            <div className="mb-8 animate-fade-in">
                <h1 className="text-5xl font-bold mb-2 gradient-text">
                    My Reports
                </h1>
                <p className="text-lg" style={{ color: 'var(--color-text-secondary)' }}>
                    View and download your generated capstone reports
                </p>
            </div>

            {/* Statistics Dashboard */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8 animate-slide-up">
                <StatsCard
                    icon="📊"
                    label="Total Reports"
                    value={stats.total}
                    variant="primary"
                />
                <StatsCard
                    icon="✅"
                    label="Completed"
                    value={stats.completed}
                    variant="success"
                />
                <StatsCard
                    icon="⚙️"
                    label="In Progress"
                    value={stats.generating}
                    variant="warning"
                />
                <StatsCard
                    icon="❌"
                    label="Failed"
                    value={stats.failed}
                    variant="info"
                />
            </div>

            {/* Filters and Search */}
            <div className="glass-strong p-6 rounded-2xl mb-8 animate-fade-in-up">
                <div className="grid md:grid-cols-3 gap-4">
                    {/* Search */}
                    <div className="md:col-span-1">
                        <label className="block text-sm font-semibold mb-2" style={{ color: 'var(--color-text)' }}>
                            Search
                        </label>
                        <input
                            type="text"
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            placeholder="Search by title or student name..."
                            className="input-field"
                        />
                    </div>

                    {/* Filter by Status */}
                    <div>
                        <label className="block text-sm font-semibold mb-2" style={{ color: 'var(--color-text)' }}>
                            Filter by Status
                        </label>
                        <select
                            value={filterStatus}
                            onChange={(e) => setFilterStatus(e.target.value)}
                            className="input-field"
                        >
                            <option value="all">All Statuses</option>
                            <option value="completed">Completed</option>
                            <option value="generating">Generating</option>
                            <option value="processing">Processing</option>
                            <option value="failed">Failed</option>
                            <option value="pending">Pending</option>
                        </select>
                    </div>

                    {/* Sort */}
                    <div>
                        <label className="block text-sm font-semibold mb-2" style={{ color: 'var(--color-text)' }}>
                            Sort By
                        </label>
                        <select
                            value={sortBy}
                            onChange={(e) => setSortBy(e.target.value)}
                            className="input-field"
                        >
                            <option value="date">Date (Newest First)</option>
                            <option value="title">Title (A-Z)</option>
                            <option value="status">Status</option>
                        </select>
                    </div>
                </div>
            </div>

            {/* Reports List */}
            {filteredReports.length === 0 ? (
                <div className="glass-strong p-20 rounded-2xl text-center animate-fade-in">
                    <div className="text-7xl mb-6">📄</div>
                    <h3 className="text-3xl font-bold mb-3" style={{ color: 'var(--color-text)' }}>
                        {searchQuery || filterStatus !== 'all' ? 'No reports found' : 'No reports yet'}
                    </h3>
                    <p className="text-lg mb-8" style={{ color: 'var(--color-text-secondary)' }}>
                        {searchQuery || filterStatus !== 'all'
                            ? 'Try adjusting your search or filters'
                            : 'Generate your first capstone report to get started'}
                    </p>
                    {!searchQuery && filterStatus === 'all' && (
                        <a href="/generate" className="btn-primary inline-block">
                            🚀 Generate Report
                        </a>
                    )}
                </div>
            ) : (
                <div className="space-y-6">
                    {filteredReports.map((report, index) => (
                        <div
                            key={report.id}
                            className="glass-strong p-6 rounded-2xl hover-lift animate-fade-in-up"
                            style={{ animationDelay: `${index * 0.1}s` }}
                        >
                            <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-6">
                                <div className="flex-1">
                                    <div className="flex items-start justify-between mb-3">
                                        <h3 className="text-2xl font-bold" style={{ color: 'var(--color-text)' }}>
                                            {report.title}
                                        </h3>
                                        <StatusBadge status={report.status} size="md" />
                                    </div>

                                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm mb-4">
                                        {report.student_name && (
                                            <div>
                                                <span className="font-semibold" style={{ color: 'var(--color-text)' }}>
                                                    Student:
                                                </span>
                                                <span style={{ color: 'var(--color-text-secondary)' }}>
                                                    {' '}{report.student_name}
                                                </span>
                                            </div>
                                        )}
                                        {report.roll_no && (
                                            <div>
                                                <span className="font-semibold" style={{ color: 'var(--color-text)' }}>
                                                    Roll No:
                                                </span>
                                                <span style={{ color: 'var(--color-text-secondary)' }}>
                                                    {' '}{report.roll_no}
                                                </span>
                                            </div>
                                        )}
                                        {report.department && (
                                            <div>
                                                <span className="font-semibold" style={{ color: 'var(--color-text)' }}>
                                                    Department:
                                                </span>
                                                <span style={{ color: 'var(--color-text-secondary)' }}>
                                                    {' '}{report.department}
                                                </span>
                                            </div>
                                        )}
                                        <div>
                                            <span className="font-semibold" style={{ color: 'var(--color-text)' }}>
                                                Created:
                                            </span>
                                            <span style={{ color: 'var(--color-text-secondary)' }}>
                                                {' '}{new Date(report.created_at).toLocaleDateString()}
                                            </span>
                                        </div>
                                    </div>

                                    {report.error_message && (
                                        <div className="p-3 rounded-lg" style={{
                                            backgroundColor: 'rgba(239, 68, 68, 0.1)',
                                            border: '1px solid rgba(239, 68, 68, 0.3)',
                                            color: 'var(--color-error)'
                                        }}>
                                            <span className="font-semibold">Error: </span>
                                            {report.error_message}
                                        </div>
                                    )}
                                </div>

                                {report.status === 'completed' && (
                                    <div className="flex flex-col sm:flex-row gap-3">
                                        <button
                                            onClick={() => handleDownload(report.id, 'docx')}
                                            className="px-6 py-3 rounded-xl font-semibold text-white transition-all hover:scale-105 hover:shadow-lg flex items-center justify-center gap-2"
                                            style={{
                                                background: 'linear-gradient(135deg, var(--color-primary), var(--color-secondary))'
                                            }}
                                        >
                                            <span>📄</span>
                                            <span>DOCX</span>
                                        </button>
                                        {report.pdf_path && (
                                            <button
                                                onClick={() => handleDownload(report.id, 'pdf')}
                                                className="px-6 py-3 rounded-xl font-semibold text-white transition-all hover:scale-105 hover:shadow-lg flex items-center justify-center gap-2"
                                                style={{
                                                    background: 'linear-gradient(135deg, var(--color-secondary), var(--color-accent))'
                                                }}
                                            >
                                                <span>📕</span>
                                                <span>PDF</span>
                                            </button>
                                        )}
                                    </div>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {/* Results Count */}
            {filteredReports.length > 0 && (
                <div className="mt-6 text-center text-sm" style={{ color: 'var(--color-text-secondary)' }}>
                    Showing {filteredReports.length} of {reports.length} reports
                </div>
            )}
        </div>
    )
}
