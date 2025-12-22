import { Link, useLocation } from 'react-router-dom'

export default function Header() {
    const location = useLocation()

    const isActive = (path) => location.pathname === path

    return (
        <header className="glass border-b border-white/20 sticky top-0 z-50 backdrop-blur-xl">
            <div className="container mx-auto px-4 py-4">
                <div className="flex items-center justify-between">
                    {/* Logo */}
                    <Link to="/" className="flex items-center space-x-3 group">
                        <div className="w-12 h-12 bg-gradient-to-br from-primary-500 via-secondary-500 to-primary-600 rounded-xl flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform duration-300">
                            <span className="text-white font-bold text-2xl">CF</span>
                        </div>
                        <div>
                            <h1 className="text-2xl font-bold bg-gradient-to-r from-primary-600 to-secondary-600 bg-clip-text text-transparent">
                                CapstoneForge
                            </h1>
                            <p className="text-xs text-gray-600 font-medium">AI-Powered Reports</p>
                        </div>
                    </Link>

                    {/* Navigation */}
                    <nav className="flex items-center space-x-2">
                        <Link
                            to="/"
                            className={`px-5 py-2.5 rounded-lg font-semibold transition-all duration-200 ${isActive('/')
                                    ? 'bg-gradient-to-r from-primary-600 to-primary-700 text-white shadow-lg'
                                    : 'text-gray-700 hover:bg-primary-50 hover:text-primary-600'
                                }`}
                        >
                            Home
                        </Link>
                        <Link
                            to="/generate"
                            className={`px-5 py-2.5 rounded-lg font-semibold transition-all duration-200 ${isActive('/generate')
                                    ? 'bg-gradient-to-r from-primary-600 to-primary-700 text-white shadow-lg'
                                    : 'text-gray-700 hover:bg-primary-50 hover:text-primary-600'
                                }`}
                        >
                            Generate
                        </Link>
                        <Link
                            to="/reports"
                            className={`px-5 py-2.5 rounded-lg font-semibold transition-all duration-200 ${isActive('/reports')
                                    ? 'bg-gradient-to-r from-primary-600 to-primary-700 text-white shadow-lg'
                                    : 'text-gray-700 hover:bg-primary-50 hover:text-primary-600'
                                }`}
                        >
                            My Reports
                        </Link>
                    </nav>
                </div>
            </div>
        </header>
    )
}
