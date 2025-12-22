export default function ProgressBar({
    progress = 0,
    variant = 'primary',
    indeterminate = false,
    showPercentage = true,
    className = ''
}) {
    const variants = {
        primary: 'from-primary-500 to-primary-600',
        success: 'from-green-500 to-green-600',
        warning: 'from-yellow-500 to-yellow-600',
        error: 'from-red-500 to-red-600'
    }

    return (
        <div className={`w-full ${className}`}>
            <div className="relative w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                {indeterminate ? (
                    <div
                        className={`absolute h-full w-1/3 bg-gradient-to-r ${variants[variant]} animate-shimmer`}
                        style={{
                            animation: 'shimmer 1.5s infinite'
                        }}
                    />
                ) : (
                    <div
                        className={`h-full bg-gradient-to-r ${variants[variant]} transition-all duration-500 ease-out rounded-full`}
                        style={{ width: `${Math.min(100, Math.max(0, progress))}%` }}
                    />
                )}
            </div>
            {showPercentage && !indeterminate && (
                <div className="mt-1 text-right text-sm font-medium" style={{ color: 'var(--color-text-secondary)' }}>
                    {Math.round(progress)}%
                </div>
            )}
        </div>
    )
}
