import { useTheme } from '../contexts/ThemeContext'
import { FiSun, FiMoon } from 'react-icons/fi'

export default function ThemeToggle() {
    const { theme, toggleTheme } = useTheme()

    return (
        <button
            onClick={toggleTheme}
            className="relative p-2 rounded-lg bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 transition-all duration-200 hover:scale-110"
            aria-label="Toggle theme"
            style={{
                backgroundColor: theme === 'dark' ? 'var(--color-surface)' : 'var(--color-surface)',
                color: 'var(--color-text)'
            }}
        >
            <div className="relative w-6 h-6">
                <FiSun
                    className="absolute inset-0 transition-all duration-300"
                    style={{
                        opacity: theme === 'light' ? 1 : 0,
                        transform: theme === 'light' ? 'rotate(0deg) scale(1)' : 'rotate(180deg) scale(0)',
                    }}
                    size={24}
                />
                <FiMoon
                    className="absolute inset-0 transition-all duration-300"
                    style={{
                        opacity: theme === 'dark' ? 1 : 0,
                        transform: theme === 'dark' ? 'rotate(0deg) scale(1)' : 'rotate(-180deg) scale(0)',
                    }}
                    size={24}
                />
            </div>
        </button>
    )
}
