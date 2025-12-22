import { useEffect, useState } from 'react'

export default function StatsCard({
    icon,
    label,
    value,
    trend = null,
    variant = 'primary',
    animate = true
}) {
    const [displayValue, setDisplayValue] = useState(0)

    useEffect(() => {
        if (!animate || typeof value !== 'number') {
            setDisplayValue(value)
            return
        }

        let start = 0
        const duration = 1000
        const increment = value / (duration / 16)

        const timer = setInterval(() => {
            start += increment
            if (start >= value) {
                setDisplayValue(value)
                clearInterval(timer)
            } else {
                setDisplayValue(Math.floor(start))
            }
        }, 16)

        return () => clearInterval(timer)
    }, [value, animate])

    const variants = {
        primary: 'from-primary-500 to-primary-600',
        secondary: 'from-secondary-500 to-secondary-600',
        success: 'from-green-500 to-green-600',
        warning: 'from-yellow-500 to-yellow-600',
        info: 'from-blue-500 to-blue-600'
    }

    return (
        <div
            className="glass p-6 rounded-xl hover-lift"
            style={{
                background: 'var(--color-surface)',
                border: '1px solid var(--color-border)'
            }}
        >
            <div className="flex items-center justify-between mb-2">
                <div
                    className={`p-3 rounded-lg bg-gradient-to-br ${variants[variant]} text-white text-2xl`}
                >
                    {icon}
                </div>
                {trend !== null && (
                    <div className={`text-sm font-semibold ${trend >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {trend >= 0 ? '↗' : '↘'} {Math.abs(trend)}%
                    </div>
                )}
            </div>
            <div className="mt-4">
                <p className="text-3xl font-bold" style={{ color: 'var(--color-text)' }}>
                    {displayValue}
                </p>
                <p className="text-sm mt-1" style={{ color: 'var(--color-text-secondary)' }}>
                    {label}
                </p>
            </div>
        </div>
    )
}
