import { Link } from 'react-router-dom'
import { FiGithub, FiTwitter, FiLinkedin, FiMail } from 'react-icons/fi'

export default function Footer() {
    const currentYear = new Date().getFullYear()

    return (
        <footer
            className="border-t py-12 px-4"
            style={{
                backgroundColor: 'var(--color-surface)',
                borderColor: 'var(--color-border)'
            }}
        >
            <div className="max-w-7xl mx-auto">
                <div className="grid md:grid-cols-4 gap-8 mb-8">
                    {/* Brand */}
                    <div>
                        <h3 className="text-2xl font-bold mb-4 gradient-text">
                            CapstoneForge
                        </h3>
                        <p className="text-sm mb-4" style={{ color: 'var(--color-text-secondary)' }}>
                            AI-powered capstone report generation for students and researchers.
                        </p>
                        <div className="flex gap-4">
                            <a
                                href="https://github.com"
                                target="_blank"
                                rel="noopener noreferrer"
                                className="hover:scale-110 transition-transform"
                                style={{ color: 'var(--color-text-secondary)' }}
                            >
                                <FiGithub size={24} />
                            </a>
                            <a
                                href="https://twitter.com"
                                target="_blank"
                                rel="noopener noreferrer"
                                className="hover:scale-110 transition-transform"
                                style={{ color: 'var(--color-text-secondary)' }}
                            >
                                <FiTwitter size={24} />
                            </a>
                            <a
                                href="https://linkedin.com"
                                target="_blank"
                                rel="noopener noreferrer"
                                className="hover:scale-110 transition-transform"
                                style={{ color: 'var(--color-text-secondary)' }}
                            >
                                <FiLinkedin size={24} />
                            </a>
                        </div>
                    </div>

                    {/* Quick Links */}
                    <div>
                        <h4 className="font-semibold mb-4" style={{ color: 'var(--color-text)' }}>
                            Quick Links
                        </h4>
                        <ul className="space-y-2">
                            <li>
                                <Link
                                    to="/"
                                    className="hover:underline"
                                    style={{ color: 'var(--color-text-secondary)' }}
                                >
                                    Home
                                </Link>
                            </li>
                            <li>
                                <Link
                                    to="/generate"
                                    className="hover:underline"
                                    style={{ color: 'var(--color-text-secondary)' }}
                                >
                                    Generate Report
                                </Link>
                            </li>
                            <li>
                                <Link
                                    to="/reports"
                                    className="hover:underline"
                                    style={{ color: 'var(--color-text-secondary)' }}
                                >
                                    My Reports
                                </Link>
                            </li>
                        </ul>
                    </div>

                    {/* Resources */}
                    <div>
                        <h4 className="font-semibold mb-4" style={{ color: 'var(--color-text)' }}>
                            Resources
                        </h4>
                        <ul className="space-y-2">
                            <li>
                                <a
                                    href="#faq"
                                    className="hover:underline"
                                    style={{ color: 'var(--color-text-secondary)' }}
                                >
                                    FAQ
                                </a>
                            </li>
                            <li>
                                <a
                                    href="#examples"
                                    className="hover:underline"
                                    style={{ color: 'var(--color-text-secondary)' }}
                                >
                                    Examples
                                </a>
                            </li>
                            <li>
                                <a
                                    href="#"
                                    className="hover:underline"
                                    style={{ color: 'var(--color-text-secondary)' }}
                                >
                                    Documentation
                                </a>
                            </li>
                        </ul>
                    </div>

                    {/* Contact */}
                    <div>
                        <h4 className="font-semibold mb-4" style={{ color: 'var(--color-text)' }}>
                            Contact
                        </h4>
                        <ul className="space-y-2">
                            <li className="flex items-center gap-2" style={{ color: 'var(--color-text-secondary)' }}>
                                <FiMail size={16} />
                                <a href="mailto:support@capstoneforge.com" className="hover:underline">
                                    support@capstoneforge.com
                                </a>
                            </li>
                            <li>
                                <a
                                    href="#"
                                    className="hover:underline"
                                    style={{ color: 'var(--color-text-secondary)' }}
                                >
                                    Privacy Policy
                                </a>
                            </li>
                            <li>
                                <a
                                    href="#"
                                    className="hover:underline"
                                    style={{ color: 'var(--color-text-secondary)' }}
                                >
                                    Terms of Service
                                </a>
                            </li>
                        </ul>
                    </div>
                </div>

                {/* Bottom Bar */}
                <div
                    className="pt-8 border-t text-center text-sm"
                    style={{
                        borderColor: 'var(--color-border)',
                        color: 'var(--color-text-secondary)'
                    }}
                >
                    <p>© {currentYear} CapstoneForge. All rights reserved. | Version 1.0.0</p>
                </div>
            </div>
        </footer>
    )
}
