export default function FilePreview({ file, onRemove }) {
    const getFileIcon = (fileName) => {
        const ext = fileName.split('.').pop().toLowerCase()
        const icons = {
            pdf: '📕',
            docx: '📘',
            doc: '📘',
            pptx: '📊',
            ppt: '📊',
            png: '🖼️',
            jpg: '🖼️',
            jpeg: '🖼️'
        }
        return icons[ext] || '📄'
    }

    const formatFileSize = (bytes) => {
        if (bytes < 1024) return bytes + ' B'
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
        return (bytes / 1024 / 1024).toFixed(2) + ' MB'
    }

    return (
        <div
            className="glass p-4 rounded-xl flex items-center gap-4 animate-fade-in"
            style={{
                background: 'var(--color-surface)',
                border: '1px solid var(--color-border)'
            }}
        >
            <div className="text-5xl">
                {getFileIcon(file.name)}
            </div>
            <div className="flex-1 min-w-0">
                <p className="font-semibold truncate" style={{ color: 'var(--color-text)' }}>
                    {file.name}
                </p>
                <p className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>
                    {formatFileSize(file.size)}
                </p>
            </div>
            {onRemove && (
                <button
                    onClick={onRemove}
                    className="p-2 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
                    style={{ color: 'var(--color-error)' }}
                    title="Remove file"
                >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                </button>
            )}
        </div>
    )
}
