import { FiLoader } from 'react-icons/fi'

export default function AnimatedButton({
    children,
    onClick,
    loading = false,
    variant = 'primary',
    className = '',
    ...props
}) {
    const baseStyles = 'px-6 py-3 rounded-lg font-medium transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 justify-center'

    const variants = {
        primary: 'text-white hover:scale-105 hover:shadow-lg',
        secondary: 'hover:scale-105',
        outline: 'border-2 hover:scale-105'
    }

    const getBackgroundStyle = () => {
        if (variant === 'primary') {
            return {
                background: `linear-gradient(135deg, var(--color-primary), var(--color-secondary))`,
            }
        } else if (variant === 'secondary') {
            return {
                backgroundColor: 'var(--color-surface)',
                color: 'var(--color-text)',
                border: '1px solid var(--color-border)'
            }
        } else {
            return {
                backgroundColor: 'transparent',
                color: 'var(--color-primary)',
                borderColor: 'var(--color-primary)'
            }
        }
    }

    return (
        <button
            onClick={onClick}
            disabled={loading}
            className={`${baseStyles} ${variants[variant]} ${className}`}
            style={getBackgroundStyle()}
            {...props}
        >
            {loading && <FiLoader className="animate-spin" size={20} />}
            {children}
        </button>
    )
}
