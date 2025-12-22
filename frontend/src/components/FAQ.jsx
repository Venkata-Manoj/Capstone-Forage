import { useState } from 'react'
import { FiChevronDown } from 'react-icons/fi'
import GradientCard from './GradientCard'

const faqs = [
    {
        question: "How does CapstoneForge work?",
        answer: "Simply upload your reference materials (PDF, DOCX, PPTX, or images), provide your project title, and our AI analyzes the structure and content to generate a comprehensive, well-formatted capstone report following academic standards."
    },
    {
        question: "What file formats are supported?",
        answer: "We support PDF, DOCX, PPTX files, and images (PNG, JPG). For images, we use OCR technology to extract text content automatically."
    },
    {
        question: "How long does report generation take?",
        answer: "Generation typically takes 2-5 minutes depending on the complexity and length of your reference materials. You'll see real-time progress updates during the process."
    },
    {
        question: "Can I edit the generated report?",
        answer: "Absolutely! Download your report in DOCX or PDF format and edit it using Microsoft Word, Google Docs, or any compatible editor. The report is fully editable."
    },
    {
        question: "Is my data secure?",
        answer: "Yes! Your files are processed securely and are not stored permanently on our servers. We prioritize your privacy and data security."
    },
    {
        question: "What makes a good reference file?",
        answer: "The best reference files are well-structured with clear sections, detailed content, proper headings, and comprehensive information. Academic papers, thesis documents, and detailed project reports work excellently."
    }
]

function FAQItem({ question, answer, isOpen, onClick }) {
    return (
        <div
            className="border-b last:border-b-0"
            style={{ borderColor: 'var(--color-border)' }}
        >
            <button
                onClick={onClick}
                className="w-full py-4 px-6 flex justify-between items-center text-left hover:bg-opacity-50 transition-all"
                style={{ color: 'var(--color-text)' }}
            >
                <span className="font-medium text-lg">{question}</span>
                <FiChevronDown
                    className="transition-transform duration-300 flex-shrink-0 ml-4"
                    style={{
                        transform: isOpen ? 'rotate(180deg)' : 'rotate(0deg)',
                        color: 'var(--color-primary)'
                    }}
                    size={24}
                />
            </button>
            <div
                className="overflow-hidden transition-all duration-300"
                style={{
                    maxHeight: isOpen ? '500px' : '0',
                    opacity: isOpen ? 1 : 0,
                }}
            >
                <div
                    className="px-6 pb-4"
                    style={{ color: 'var(--color-text-secondary)' }}
                >
                    {answer}
                </div>
            </div>
        </div>
    )
}

export default function FAQ() {
    const [openIndex, setOpenIndex] = useState(null)

    return (
        <section className="py-20 px-4" style={{ backgroundColor: 'var(--color-background)' }}>
            <div className="max-w-4xl mx-auto">
                <div className="text-center mb-12 animate-fade-in">
                    <h2 className="text-4xl font-bold mb-4 gradient-text">
                        Frequently Asked Questions
                    </h2>
                    <p style={{ color: 'var(--color-text-secondary)' }}>
                        Everything you need to know about CapstoneForge
                    </p>
                </div>

                <GradientCard className="overflow-hidden">
                    {faqs.map((faq, index) => (
                        <FAQItem
                            key={index}
                            question={faq.question}
                            answer={faq.answer}
                            isOpen={openIndex === index}
                            onClick={() => setOpenIndex(openIndex === index ? null : index)}
                        />
                    ))}
                </GradientCard>
            </div>
        </section>
    )
}
