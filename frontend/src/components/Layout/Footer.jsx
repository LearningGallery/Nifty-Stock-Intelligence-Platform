import { Github, Linkedin, Mail } from 'lucide-react'

function Footer() {
  return (
    <footer className="bg-white border-t border-gray-200 mt-auto">
      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-3">
              Nifty Stock Intelligence
            </h3>
            <p className="text-sm text-gray-600">
              AI-powered stock analysis platform for Indian equity markets.
              Portfolio project by Abu Talha.
            </p>
          </div>

          <div>
            <h4 className="text-sm font-semibold text-gray-900 mb-3">Links</h4>
            <ul className="space-y-2 text-sm text-gray-600">
              <li>
                <a href="/docs" className="hover:text-primary-600">Documentation</a>
              </li>
              <li>
                <a href="/api/docs" className="hover:text-primary-600">API Docs</a>
              </li>
              <li>
                <a href="https://github.com/LearningGallery/nifty-stock-intelligence" 
                   target="_blank" 
                   rel="noopener noreferrer"
                   className="hover:text-primary-600">
                  GitHub Repository
                </a>
              </li>
            </ul>
          </div>

          <div>
            <h4 className="text-sm font-semibold text-gray-900 mb-3">Connect</h4>
            <div className="flex gap-3">
              <a
                href="https://github.com/LearningGallery"
                target="_blank"
                rel="noopener noreferrer"
                className="p-2 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
              >
                <Github className="w-5 h-5 text-gray-700" />
              </a>
              <a
                href="https://www.linkedin.com/in/im-abutalha/"
                target="_blank"
                rel="noopener noreferrer"
                className="p-2 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
              >
                <Linkedin className="w-5 h-5 text-gray-700" />
              </a>
              <a
                href="mailto:contact@example.com"
                className="p-2 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
              >
                <Mail className="w-5 h-5 text-gray-700" />
              </a>
            </div>
          </div>
        </div>

        <div className="mt-8 pt-8 border-t border-gray-200">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <p className="text-sm text-gray-600">
              © 2024 Nifty Stock Intelligence. Portfolio Project.
            </p>
            <p className="text-xs text-gray-500">
              ⚠️ Disclaimer: This is for educational purposes only. Not financial advice.
              Consult a SEBI-registered advisor before investing.
            </p>
          </div>
        </div>
      </div>
    </footer>
  )
}

export default Footer
