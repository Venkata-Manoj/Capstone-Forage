import { Link } from 'react-router-dom'
import { FiZap, FiFileText, FiClock, FiShield, FiDownload, FiCheckCircle } from 'react-icons/fi'
import AnimatedButton from '../components/AnimatedButton'
import GradientCard from '../components/GradientCard'
import Examples from '../components/Examples'
import FAQ from '../components/FAQ'
import { useEffect, useState } from 'react'

function StatCounter({ end, duration = 2000, suffix = '' }) {
  const [count, setCount] = useState(0)

  useEffect(() => {
    let startTime
    const animate = (currentTime) => {
      if (!startTime) startTime = currentTime
      const progress = Math.min((currentTime - startTime) / duration, 1)
      setCount(Math.floor(progress * end))
      if (progress < 1) {
        requestAnimationFrame(animate)
      }
    }
    requestAnimationFrame(animate)
  }, [end, duration])

  return <span>{count}{suffix}</span>
}

export default function Home() {
  const features = [
    {
      icon: FiZap,
      title: "Lightning Fast",
      description: "Generate comprehensive reports in minutes, not hours. Our AI processes your references quickly and efficiently."
    },
    {
      icon: FiFileText,
      title: "Professional Format",
      description: "Get perfectly structured reports following academic standards with proper citations and formatting."
    },
    {
      icon: FiClock,
      title: "Save Time",
      description: "Focus on your research while we handle the formatting and structure of your capstone report."
    },
    {
      icon: FiShield,
      title: "Secure & Private",
      description: "Your data is encrypted and processed securely. We don't store your files permanently."
    },
    {
      icon: FiDownload,
      title: "Multiple Formats",
      description: "Download your report in DOCX or PDF format, ready for submission or further editing."
    },
    {
      icon: FiCheckCircle,
      title: "Quality Assured",
      description: "AI-powered quality checks ensure your report meets academic standards and requirements."
    }
  ]

  return (
    <div style={{ backgroundColor: 'var(--color-background)' }}>
      {/* Hero Section */}
      <section className="py-20 px-4">
        <div className="max-w-7xl mx-auto text-center">
          <div className="animate-fade-in">
            <h1 className="text-5xl md:text-6xl font-bold mb-6 gradient-text">
              Transform Your Research into
              <br />
              Professional Capstone Reports
            </h1>
            <p className="text-xl md:text-2xl mb-8 max-w-3xl mx-auto" style={{ color: 'var(--color-text-secondary)' }}>
              AI-powered report generation that understands your content and creates
              perfectly structured academic documents in minutes.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Link to="/generate">
                <AnimatedButton variant="primary" className="text-lg px-8 py-4">
                  <FiZap /> Start Generating
                </AnimatedButton>
              </Link>
              <Link to="/reports">
                <AnimatedButton variant="outline" className="text-lg px-8 py-4">
                  View Examples
                </AnimatedButton>
              </Link>
            </div>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mt-20">
            {[
              { value: 1000, suffix: '+', label: 'Reports Generated' },
              { value: 95, suffix: '%', label: 'Accuracy Rate' },
              { value: 5, suffix: ' min', label: 'Avg. Generation Time' },
              { value: 500, suffix: '+', label: 'Happy Students' }
            ].map((stat, index) => (
              <div
                key={index}
                className="animate-fade-in"
                style={{ animationDelay: `${index * 0.1}s` }}
              >
                <div className="text-4xl font-bold mb-2 gradient-text">
                  <StatCounter end={stat.value} suffix={stat.suffix} />
                </div>
                <div className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>
                  {stat.label}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-20 px-4" style={{ backgroundColor: 'var(--color-surface)' }}>
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold mb-4 gradient-text">
              Why Choose CapstoneForge?
            </h2>
            <p className="text-xl" style={{ color: 'var(--color-text-secondary)' }}>
              Everything you need to create outstanding capstone reports
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <div
                key={index}
                className="animate-fade-in"
                style={{ animationDelay: `${index * 0.1}s` }}
              >
                <GradientCard>
                  <div
                    className="w-12 h-12 rounded-lg flex items-center justify-center mb-4"
                    style={{
                      background: `linear-gradient(135deg, var(--color-primary), var(--color-secondary))`,
                    }}
                  >
                    <feature.icon size={24} color="white" />
                  </div>
                  <h3 className="text-xl font-bold mb-2" style={{ color: 'var(--color-text)' }}>
                    {feature.title}
                  </h3>
                  <p style={{ color: 'var(--color-text-secondary)' }}>
                    {feature.description}
                  </p>
                </GradientCard>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Examples Section */}
      <div id="examples">
        <Examples />
      </div>

      {/* FAQ Section */}
      <div id="faq">
        <FAQ />
      </div>

      {/* CTA Section */}
      <section className="py-20 px-4" style={{ backgroundColor: 'var(--color-surface)' }}>
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl font-bold mb-6 gradient-text">
            Ready to Create Your Report?
          </h2>
          <p className="text-xl mb-8" style={{ color: 'var(--color-text-secondary)' }}>
            Join hundreds of students who have already streamlined their capstone process
          </p>
          <Link to="/generate">
            <AnimatedButton variant="primary" className="text-lg px-8 py-4">
              <FiZap /> Get Started Now
            </AnimatedButton>
          </Link>
        </div>
      </section>
    </div>
  )
}
