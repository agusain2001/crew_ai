import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Progress } from '@/components/ui/progress.jsx'
import { Textarea } from '@/components/ui/textarea.jsx'
import { Alert, AlertDescription } from '@/components/ui/alert.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { Search, Globe, BarChart3, FileText, CheckCircle, AlertCircle, Loader2 } from 'lucide-react'
import './App.css'

function App() {
  const [url, setUrl] = useState('')
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [progress, setProgress] = useState(0)
  const [currentStep, setCurrentStep] = useState('')
  const [analysisResult, setAnalysisResult] = useState(null)
  const [error, setError] = useState('')
  const [report, setReport] = useState('')

  const handleAnalyze = async () => {
    if (!url.trim()) {
      setError('Please enter a valid URL')
      return
    }

    setIsAnalyzing(true)
    setProgress(0)
    setCurrentStep('')
    setError('')
    setAnalysisResult(null)
    setReport('')

    try {
      // Connect to the AG-UI compatible chat endpoint
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: `Please analyze this website for SEO: ${url}`,
          session_id: 'seo-frontend'
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value)
        const lines = chunk.split('\n')

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const eventData = JSON.parse(line.slice(6))
              handleStreamEvent(eventData)
            } catch (e) {
              console.error('Error parsing event:', e)
            }
          }
        }
      }
    } catch (err) {
      setError(`Analysis failed: ${err.message}`)
      setIsAnalyzing(false)
    }
  }

  const handleStreamEvent = (event) => {
    switch (event.type) {
      case 'analysis_start':
        setCurrentStep('Starting analysis...')
        setProgress(10)
        break
      case 'analysis_progress':
        setCurrentStep(event.data.message)
        setProgress(event.data.progress)
        break
      case 'analysis_complete':
        setCurrentStep('Analysis completed!')
        setProgress(100)
        setAnalysisResult({
          url: event.data.url,
          timestamp: event.data.timestamp,
          status: 'success'
        })
        setIsAnalyzing(false)
        break
      case 'report':
        setReport(event.data.content)
        break
      case 'analysis_error':
      case 'error':
        setError(event.data.message || event.data.error)
        setIsAnalyzing(false)
        break
      default:
        console.log('Unknown event type:', event.type)
    }
  }

  const formatUrl = (inputUrl) => {
    if (!inputUrl.startsWith('http://') && !inputUrl.startsWith('https://')) {
      return `https://${inputUrl}`
    }
    return inputUrl
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center mb-4">
            <BarChart3 className="h-12 w-12 text-blue-600 mr-3" />
            <h1 className="text-4xl font-bold text-gray-900 dark:text-white">
              CrewAI SEO Analyzer
            </h1>
          </div>
          <p className="text-xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
            Comprehensive SEO analysis powered by AI agents. Get detailed insights and actionable recommendations for your website.
          </p>
        </div>

        {/* URL Input Section */}
        <Card className="mb-8 max-w-2xl mx-auto">
          <CardHeader>
            <CardTitle className="flex items-center">
              <Globe className="h-5 w-5 mr-2" />
              Website Analysis
            </CardTitle>
            <CardDescription>
              Enter a website URL to get a comprehensive SEO analysis
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex gap-4">
              <Input
                type="url"
                placeholder="https://example.com"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                className="flex-1"
                disabled={isAnalyzing}
              />
              <Button 
                onClick={handleAnalyze}
                disabled={isAnalyzing || !url.trim()}
                className="min-w-[120px]"
              >
                {isAnalyzing ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Analyzing
                  </>
                ) : (
                  <>
                    <Search className="h-4 w-4 mr-2" />
                    Analyze
                  </>
                )}
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Error Display */}
        {error && (
          <Alert className="mb-8 max-w-2xl mx-auto border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-900/20">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription className="text-red-800 dark:text-red-200">
              {error}
            </AlertDescription>
          </Alert>
        )}

        {/* Progress Section */}
        {isAnalyzing && (
          <Card className="mb-8 max-w-2xl mx-auto">
            <CardHeader>
              <CardTitle className="flex items-center">
                <Loader2 className="h-5 w-5 mr-2 animate-spin" />
                Analysis in Progress
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <Progress value={progress} className="w-full" />
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {currentStep}
                </p>
                <div className="flex items-center text-sm text-blue-600 dark:text-blue-400">
                  <span>{Math.round(progress)}% complete</span>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Results Section */}
        {analysisResult && (
          <div className="space-y-6">
            {/* Analysis Summary */}
            <Card className="max-w-4xl mx-auto">
              <CardHeader>
                <CardTitle className="flex items-center">
                  <CheckCircle className="h-5 w-5 mr-2 text-green-600" />
                  Analysis Complete
                </CardTitle>
                <CardDescription>
                  SEO analysis for {analysisResult.url}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="text-center p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                    <CheckCircle className="h-8 w-8 text-green-600 mx-auto mb-2" />
                    <p className="font-semibold text-green-800 dark:text-green-200">Analysis Complete</p>
                    <p className="text-sm text-green-600 dark:text-green-400">
                      {new Date(analysisResult.timestamp).toLocaleString()}
                    </p>
                  </div>
                  <div className="text-center p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                    <BarChart3 className="h-8 w-8 text-blue-600 mx-auto mb-2" />
                    <p className="font-semibold text-blue-800 dark:text-blue-200">Comprehensive Report</p>
                    <p className="text-sm text-blue-600 dark:text-blue-400">
                      Technical & Content Analysis
                    </p>
                  </div>
                  <div className="text-center p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                    <FileText className="h-8 w-8 text-purple-600 mx-auto mb-2" />
                    <p className="font-semibold text-purple-800 dark:text-purple-200">Actionable Insights</p>
                    <p className="text-sm text-purple-600 dark:text-purple-400">
                      Priority Recommendations
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Report Display */}
            {report && (
              <Card className="max-w-4xl mx-auto">
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <FileText className="h-5 w-5 mr-2" />
                    SEO Analysis Report
                  </CardTitle>
                  <CardDescription>
                    Detailed findings and recommendations
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <Tabs defaultValue="report" className="w-full">
                    <TabsList className="grid w-full grid-cols-2">
                      <TabsTrigger value="report">Full Report</TabsTrigger>
                      <TabsTrigger value="summary">Executive Summary</TabsTrigger>
                    </TabsList>
                    <TabsContent value="report" className="mt-4">
                      <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4 max-h-96 overflow-y-auto">
                        <pre className="whitespace-pre-wrap text-sm text-gray-800 dark:text-gray-200">
                          {report}
                        </pre>
                      </div>
                    </TabsContent>
                    <TabsContent value="summary" className="mt-4">
                      <div className="space-y-4">
                        <Alert>
                          <AlertCircle className="h-4 w-4" />
                          <AlertDescription>
                            This is a summary view. The full report contains detailed technical analysis and specific recommendations.
                          </AlertDescription>
                        </Alert>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <Card>
                            <CardHeader className="pb-3">
                              <CardTitle className="text-lg">Key Findings</CardTitle>
                            </CardHeader>
                            <CardContent>
                              <ul className="space-y-2 text-sm">
                                <li className="flex items-center">
                                  <Badge variant="outline" className="mr-2">SEO</Badge>
                                  Technical analysis completed
                                </li>
                                <li className="flex items-center">
                                  <Badge variant="outline" className="mr-2">Content</Badge>
                                  Content strategy evaluated
                                </li>
                                <li className="flex items-center">
                                  <Badge variant="outline" className="mr-2">Performance</Badge>
                                  Performance metrics analyzed
                                </li>
                              </ul>
                            </CardContent>
                          </Card>
                          <Card>
                            <CardHeader className="pb-3">
                              <CardTitle className="text-lg">Next Steps</CardTitle>
                            </CardHeader>
                            <CardContent>
                              <ul className="space-y-2 text-sm">
                                <li className="flex items-center">
                                  <Badge variant="secondary" className="mr-2">1</Badge>
                                  Review full report details
                                </li>
                                <li className="flex items-center">
                                  <Badge variant="secondary" className="mr-2">2</Badge>
                                  Implement priority recommendations
                                </li>
                                <li className="flex items-center">
                                  <Badge variant="secondary" className="mr-2">3</Badge>
                                  Monitor performance improvements
                                </li>
                              </ul>
                            </CardContent>
                          </Card>
                        </div>
                      </div>
                    </TabsContent>
                  </Tabs>
                </CardContent>
              </Card>
            )}
          </div>
        )}

        {/* Features Section */}
        {!isAnalyzing && !analysisResult && (
          <div className="max-w-4xl mx-auto mt-12">
            <h2 className="text-2xl font-bold text-center mb-8 text-gray-900 dark:text-white">
              What Our SEO Analysis Includes
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <Card>
                <CardHeader>
                  <Search className="h-8 w-8 text-blue-600 mb-2" />
                  <CardTitle>Technical SEO</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-600 dark:text-gray-400">
                    Page speed, mobile-friendliness, crawlability, and technical optimization analysis.
                  </p>
                </CardContent>
              </Card>
              <Card>
                <CardHeader>
                  <FileText className="h-8 w-8 text-green-600 mb-2" />
                  <CardTitle>Content Analysis</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-600 dark:text-gray-400">
                    Keyword optimization, content quality, structure, and search intent alignment.
                  </p>
                </CardContent>
              </Card>
              <Card>
                <CardHeader>
                  <BarChart3 className="h-8 w-8 text-purple-600 mb-2" />
                  <CardTitle>Performance Metrics</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-600 dark:text-gray-400">
                    Core Web Vitals, user experience metrics, and performance optimization recommendations.
                  </p>
                </CardContent>
              </Card>
            </div>
          </div>
        )}

        {/* Footer */}
        <footer className="text-center mt-16 py-8 border-t border-gray-200 dark:border-gray-700">
          <p className="text-gray-600 dark:text-gray-400">
            Powered by CrewAI, Google Gemini, and BrightData
          </p>
        </footer>
      </div>
    </div>
  )
}

export default App

