import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import Home from './pages/Home'
import Generate from './pages/Generate'
import Reports from './pages/Reports'

function App() {
    return (
        <Router>
            <div className="min-h-screen bg-gray-50">
                <nav className="bg-white shadow-sm">
                    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                        <div className="flex justify-between h-16">
                            <div className="flex">
                                <Link to="/" className="flex items-center px-2 py-2 text-gray-900 font-semibold">
                                    CapstoneForge
                                </Link>
                                <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                                    <Link to="/" className="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-900">
                                        Home
                                    </Link>
                                    <Link to="/generate" className="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-500 hover:text-gray-900">
                                        Generate
                                    </Link>
                                    <Link to="/reports" className="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-500 hover:text-gray-900">
                                        Reports
                                    </Link>
                                </div>
                            </div>
                        </div>
                    </div>
                </nav>

                <Routes>
                    <Route path="/" element={<Home />} />
                    <Route path="/generate" element={<Generate />} />
                    <Route path="/reports" element={<Reports />} />
                </Routes>
            </div>
        </Router>
    )
}

export default App
