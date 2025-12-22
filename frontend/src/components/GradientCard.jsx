export default function GradientCard({ children, className = '', hover = true }) {
    return (
        <div
            className={`relative p-6 rounded-xl ${hover ? 'hover-lift' : ''} ${className}`}
            style={{
                background: 'var(--color-surface)',
                border: '1px solid var(--color-border)',
            }}
        >
            <div
                className="absolute inset-0 rounded-xl opacity-0 hover:opacity-100 transition-opacity duration-300 pointer-events-none"
                style={{
                    background: `linear-gradient(135deg, ${getComputedStyle(document.documentElement).getPropertyValue('--color-primary')}15, ${getComputedStyle(document.documentElement).getPropertyValue('--color-secondary')}15)`,
                }}
            />
            <div className="relative z-10">
                {children}
            </div>
        </div>
    )
}
