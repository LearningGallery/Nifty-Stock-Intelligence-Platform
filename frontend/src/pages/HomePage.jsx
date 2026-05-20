import { Link } from 'react-router-dom'
import { MessageSquare, BarChart3, TrendingUp, Shield, Zap, Brain } from 'lucide-react'

function HomePage() {
  const features = [
    {
      icon: Brain,
      title: 'AI-Powered Analysis',
      description: 'Advanced AI models analyze technical, fundamental, and sentiment data in real-time.',
    },
    {
      icon: Zap,
      title: 'Real-Time Insights',
      description: 'Get instant stock recommendations with live market data and news integration.',
    },
    {
      icon: BarChart3,
      title: 'Comprehensive Reports',
      description: 'Detailed analysis with pros, cons, risk factors, and price targets.',
    },
    {
      icon: Shield,
      title: 'Risk Assessment',
      description: 'Clear risk evaluation with stop-loss recommendations and confidence levels.',
    },
  ]

  return (
    <div className="space-y-12">
      {/* Hero Section */}
      <section className="text-center py-12">
        <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary-50 text-primary-700 rounded-full text-sm font-medium mb-6">
          <TrendingUp className="w-4 h-4" />
          Powered by Amazon Bedrock & AWS
        </div>
        
        <h1 className="text-5xl font-bold text-gray-900 mb-6">
          AI-Powered Stock Analysis
          <br />
          <span className="text-primary-600">for Indian Markets</span>
        </h1>
        
        <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
          Get comprehensive stock analysis for Nifty 100-250 stocks with AI-driven
          insights, real-time data, and actionable recommendations.
        </p>

        <div className="flex items-center justify-center gap-4">
          <Link to="/chat" className="btn btn-primary flex items-center gap-2">
            <MessageSquare className="w-5 h-5" />
            Start Chatting
          </Link>
          <Link to="/analysis" className="btn btn-secondary flex items-center gap-2">
            <BarChart3 className="w-5 h-5" />
            Analyze Stock
          </Link>
        </div>
      </section>

      {/* Features Grid */}
      <section className="py-12">
        <h2 className="text-3xl font-bold text-center mb-12">
          Intelligent Stock Analysis Features
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {features.map((feature, index) => (
            <div
              key={index}
              className="card hover:shadow-md transition-shadow"
            >
              <div className="flex items-start gap-4">
                <div className="p-3 bg-primary-50 rounded-lg">
                  <feature.icon className="w-6 h-6 text-primary-600" />
                </div>
                <div>
                  <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
                  <p className="text-gray-600">{feature.description}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Analysis Components */}
      <section className="py-12 bg-gradient-to-r from-primary-50 to-blue-50 -mx-6 px-6 rounded-xl">
        <h2 className="text-3xl font-bold text-center mb-12">
          Multi-Dimensional Analysis
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          <div className="text-center">
            <div className="w-16 h-16 bg-white rounded-full flex items-center justify-center mx-auto mb-4 shadow-md">
              <span className="text-2xl font-bold text-primary-600">📊</span>
            </div>
            <h3 className="text-lg font-semibold mb-2">Technical Analysis</h3>
            <p className="text-gray-600 text-sm">
              RSI, MACD, Moving Averages, Support/Resistance, Chart Patterns
            </p>
          </div>

          <div className="text-center">
            <div className="w-16 h-16 bg-white rounded-full flex items-center justify-center mx-auto mb-4 shadow-md">
              <span className="text-2xl font-bold text-primary-600">💼</span>
            </div>
            <h3 className="text-lg font-semibold mb-2">Fundamental Analysis</h3>
            <p className="text-gray-600 text-sm">
              P/E, ROE, Debt/Equity, Revenue Growth, Profit Margins
            </p>
          </div>

          <div className="text-center">
            <div className="w-16 h-16 bg-white rounded-full flex items-center justify-center mx-auto mb-4 shadow-md">
              <span className="text-2xl font-bold text-primary-600">📰</span>
            </div>
            <h3 className="text-lg font-semibold mb-2">Sentiment Analysis</h3>
            <p className="text-gray-600 text-sm">
              News Analysis, Market Sentiment, Social Media, Analyst Ratings
            </p>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="text-center py-12">
        <div className="card max-w-2xl mx-auto bg-gradient-to-r from-primary-600 to-blue-600 text-white">
          <h2 className="text-3xl font-bold mb-4">
            Ready to Make Informed Decisions?
          </h2>
          <p className="text-lg mb-6 opacity-90">
            Start analyzing stocks with AI-powered insights today.
          </p>
          <Link
            to="/chat"
            className="inline-flex items-center gap-2 px-6 py-3 bg-white text-primary-600 rounded-lg font-semibold hover:bg-gray-100 transition-colors"
          >
            <MessageSquare className="w-5 h-5" />
            Get Started Now
          </Link>
        </div>
      </section>

      {/* Disclaimer */}
      <section className="py-6">
        <div className="card bg-yellow-50 border-yellow-200">
          <p className="text-sm text-gray-700">
            <strong>⚠️ Disclaimer:</strong> This platform provides AI-generated analysis
            for informational purposes only. It is not financial advice. Always consult
            with a SEBI-registered financial advisor before making investment decisions.
            Past performance does not guarantee future results.
          </p>
        </div>
      </section>
    </div>
  )
}

export default HomePage
