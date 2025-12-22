import { FiCode, FiCpu, FiTrendingUp } from 'react-icons/fi'
import GradientCard from './GradientCard'

const examples = [
    {
        icon: FiCode,
        title: "Computer Science Project",
        description: "AI/ML Capstone",
        details: "Complete report with methodology, implementation, results, and analysis for a machine learning project with data visualization and performance metrics.",
        tags: ["Python", "TensorFlow", "Research"]
    },
    {
        icon: FiCpu,
        title: "Engineering Design",
        description: "Mechanical Design Project",
        details: "Comprehensive engineering report including CAD designs, stress analysis, material selection, and testing results with detailed technical specifications.",
        tags: ["CAD", "Analysis", "Testing"]
    },
    {
        icon: FiTrendingUp,
        title: "Business Analytics",
        description: "Market Research Study",
        details: "Professional business report with market analysis, data visualization, strategic recommendations, and executive summary following industry standards.",
        tags: ["Analytics", "Strategy", "Data"]
    }
]

export default function Examples() {
    return (
        <section className="py-20 px-4" style={{ backgroundColor: 'var(--color-surface)' }}>
            <div className="max-w-7xl mx-auto">
                <div className="text-center mb-12 animate-fade-in">
                    <h2 className="text-4xl font-bold mb-4 gradient-text">
                        Example Reports
                    </h2>
                    <p className="text-xl" style={{ color: 'var(--color-text-secondary)' }}>
                        See what CapstoneForge can create for different disciplines
                    </p>
                </div>

                <div className="grid md:grid-cols-3 gap-8">
                    {examples.map((example, index) => (
                        <div
                            key={index}
                            className="animate-fade-in"
                            style={{ animationDelay: `${index * 0.1}s` }}
                        >
                            <GradientCard className="h-full">
                                <div className="flex flex-col h-full">
                                    <div
                                        className="w-16 h-16 rounded-lg flex items-center justify-center mb-4"
                                        style={{
                                            background: `linear-gradient(135deg, var(--color-primary), var(--color-secondary))`,
                                        }}
                                    >
                                        <example.icon size={32} color="white" />
                                    </div>

                                    <h3 className="text-2xl font-bold mb-2" style={{ color: 'var(--color-text)' }}>
                                        {example.title}
                                    </h3>

                                    <p className="text-sm font-medium mb-3" style={{ color: 'var(--color-primary)' }}>
                                        {example.description}
                                    </p>

                                    <p className="mb-4 flex-grow" style={{ color: 'var(--color-text-secondary)' }}>
                                        {example.details}
                                    </p>

                                    <div className="flex flex-wrap gap-2">
                                        {example.tags.map((tag, tagIndex) => (
                                            <span
                                                key={tagIndex}
                                                className="px-3 py-1 rounded-full text-sm font-medium"
                                                style={{
                                                    backgroundColor: 'var(--color-surface)',
                                                    color: 'var(--color-primary)',
                                                    border: '1px solid var(--color-border)'
                                                }}
                                            >
                                                {tag}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            </GradientCard>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    )
}
