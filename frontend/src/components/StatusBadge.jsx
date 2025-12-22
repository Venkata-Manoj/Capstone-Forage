export default function StatusBadge({ status, size = 'md', showIcon = true }) {
    const statusConfig = {
        pending: {
            icon: '⏳',
            label: 'Pending',
            bgColor: 'bg-gray-100 dark:bg-gray-800',
            textColor: 'text-gray-700 dark:text-gray-300',
            borderColor: 'border-gray-300 dark:border-gray-600',
            animate: false
        },
        generating: {
            icon: '🤖',
            label: 'Generating',
            bgColor: 'bg-blue-50 dark:bg-blue-900/20',
            textColor: 'text-blue-700 dark:text-blue-400',
            borderColor: 'border-blue-300 dark:border-blue-600',
            animate: true
        },
        processing: {
            icon: '⚙️',
            label: 'Processing',
            bgColor: 'bg-yellow-50 dark:bg-yellow-900/20',
            textColor: 'text-yellow-700 dark:text-yellow-400',
            borderColor: 'border-yellow-300 dark:border-yellow-600',
            animate: true
        },
        completed: {
            icon: '✅',
            label: 'Completed',
            bgColor: 'bg-green-50 dark:bg-green-900/20',
            textColor: 'text-green-700 dark:text-green-400',
            borderColor: 'border-green-300 dark:border-green-600',
            animate: false
        },
        failed: {
            icon: '❌',
            label: 'Failed',
            bgColor: 'bg-red-50 dark:bg-red-900/20',
            textColor: 'text-red-700 dark:text-red-400',
            borderColor: 'border-red-300 dark:border-red-600',
            animate: false
        }
    }

    const config = statusConfig[status] || statusConfig.pending

    const sizes = {
        sm: 'px-2 py-0.5 text-xs',
        md: 'px-3 py-1 text-sm',
        lg: 'px-4 py-2 text-base'
    }

    return (
        <span
            className={`
                inline-flex items-center gap-1.5 rounded-full font-semibold border
                ${config.bgColor} ${config.textColor} ${config.borderColor} ${sizes[size]}
                ${config.animate ? 'animate-pulse' : ''}
                transition-all duration-300
            `}
        >
            {showIcon && <span>{config.icon}</span>}
            <span>{config.label}</span>
        </span>
    )
}
