'use client'

import { useState, useRef, useEffect } from 'react'
import { Send, Bot, User, Settings, Sparkles, Brain, Target, Palette, Zap, Upload, FileText } from 'lucide-react'

interface Message {
  id: string
  content: string
  role: 'user' | 'assistant'
  timestamp: Date
}

interface ChatConfig {
  reasoningMode: 'none' | 'chain_of_thought' | 'step_by_step'
  styleTone: 'professional' | 'casual' | 'academic' | 'creative' | 'technical' | 'friendly'
  accuracyLevel: 'standard' | 'high' | 'maximum'
  temperature: number
  maxTokens: number
  includeCitations: boolean
  customInstructions: string
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([])
  const [inputMessage, setInputMessage] = useState('')
  const [developerMessage, setDeveloperMessage] = useState('You are a helpful AI assistant.')
  const [apiKey, setApiKey] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [showSettings, setShowSettings] = useState(false)
  const [showAdvancedSettings, setShowAdvancedSettings] = useState(false)
  const [pdfSessionId, setPdfSessionId] = useState<string | null>(null)
  const [isPdfMode, setIsPdfMode] = useState(false)
  const [apiBaseUrl, setApiBaseUrl] = useState('')
  const [config, setConfig] = useState<ChatConfig>({
    reasoningMode: 'none',
    styleTone: 'professional',
    accuracyLevel: 'standard',
    temperature: 0.7,
    maxTokens: 2000,
    includeCitations: false,
    customInstructions: ''
  })
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  // Auto-detect API URL
  useEffect(() => {
    const detectApiUrl = async () => {
      try {
        // Try production URL first
        const vercelUrl = window.location.origin
        const prodResponse = await fetch(`${vercelUrl}/api/config`)
        if (prodResponse.ok) {
          const config = await prodResponse.json()
          setApiBaseUrl(config.api_url)
          return
        }

        // Fallback to local development
        const devResponse = await fetch('http://localhost:8000/api/config')
        if (devResponse.ok) {
          const config = await devResponse.json()
          setApiBaseUrl(config.api_url)
          return
        }
      } catch (err) {
        console.error('Failed to detect API URL:', err)
        // Default to same origin
        setApiBaseUrl(window.location.origin)
      }
    }

    detectApiUrl()
  }, [])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handlePdfUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file || !apiKey || !apiBaseUrl) return

    setIsLoading(true)

    try {
      // Read the file as base64
      const reader = new FileReader()
      
      reader.onload = async (event) => {
        try {
          const base64Content = event.target?.result as string
          // Remove the data URL prefix (e.g., "data:application/pdf;base64,")
          const base64Data = base64Content.split(',')[1]
          
          const response = await fetch(`${apiBaseUrl}/api/upload-pdf`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              api_key: apiKey,
              filename: file.name,
              file_size: file.size,
              pdf_content: base64Data
            })
          })

          if (!response.ok) {
            const errorData = await response.json().catch(() => ({}))
            throw new Error(errorData.error || 'Failed to upload PDF')
          }

          const data = await response.json()
          console.log('PDF upload response:', data)
          
          setPdfSessionId(data.session_id)
          setIsPdfMode(true)
          setMessages([{
            id: Date.now().toString(),
            content: `PDF "${file.name}" uploaded successfully! You can now ask questions about the document.`,
            role: 'assistant',
            timestamp: new Date()
          }])
        } catch (err) {
          console.error('Error:', err)
          const error = err as Error
          setMessages([{
            id: Date.now().toString(),
            content: `Sorry, there was an error uploading your PDF: ${error.message}`,
            role: 'assistant',
            timestamp: new Date()
          }])
        } finally {
          setIsLoading(false)
          if (fileInputRef.current) {
            fileInputRef.current.value = ''
          }
        }
      }
      
      reader.onerror = () => {
        setMessages([{
          id: Date.now().toString(),
          content: 'Sorry, there was an error reading the PDF file.',
          role: 'assistant',
          timestamp: new Date()
        }])
        setIsLoading(false)
        if (fileInputRef.current) {
          fileInputRef.current.value = ''
        }
      }
      
      // Read the file as base64
      reader.readAsDataURL(file)
      
    } catch (err) {
      console.error('Error:', err)
      const error = err as Error
      setMessages([{
        id: Date.now().toString(),
        content: `Sorry, there was an error uploading your PDF: ${error.message}`,
        role: 'assistant',
        timestamp: new Date()
      }])
      setIsLoading(false)
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!inputMessage.trim() || !apiKey.trim() || !apiBaseUrl) return

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputMessage,
      role: 'user',
      timestamp: new Date()
    }

    setMessages((prev: Message[]) => [...prev, userMessage])
    setInputMessage('')
    setIsLoading(true)

    try {
      const endpoint = isPdfMode ? '/api/chat-pdf' : '/api/chat'
      const body = isPdfMode ? {
        message: inputMessage,
        session_id: pdfSessionId,
        api_key: apiKey,
        model: 'gpt-4.1-mini'
      } : {
        developer_message: developerMessage,
        user_message: inputMessage,
        model: 'gpt-4.1-mini',
        api_key: apiKey,
        reasoning_mode: config.reasoningMode,
        style_tone: config.styleTone,
        accuracy_level: config.accuracyLevel,
        temperature: config.temperature,
        max_tokens: config.maxTokens,
        include_citations: config.includeCitations,
        custom_instructions: config.customInstructions
      }

      // Debug logging
      console.log('Sending request:', {
        endpoint,
        isPdfMode,
        pdfSessionId,
        body: { ...body, api_key: body.api_key ? '***' : 'missing' }
      })

      // Additional debugging for PDF mode
      if (isPdfMode) {
        console.log('PDF Mode Debug:', {
          pdfSessionId,
          sessionIdType: typeof pdfSessionId,
          sessionIdLength: pdfSessionId ? pdfSessionId.length : 0,
          bodyKeys: Object.keys(body)
        })
      }

      const response = await fetch(`${apiBaseUrl}${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(body)
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || 'Failed to get response')
      }

      const reader = response.body?.getReader()
      if (!reader) throw new Error('No reader available')

      let assistantMessage = ''
      const assistantMessageId = (Date.now() + 1).toString()

      setMessages((prev: Message[]) => [...prev, {
        id: assistantMessageId,
        content: '',
        role: 'assistant',
        timestamp: new Date()
      }])

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = new TextDecoder().decode(value)
        assistantMessage += chunk

        setMessages((prev: Message[]) => prev.map((msg: Message) => 
          msg.id === assistantMessageId 
            ? { ...msg, content: assistantMessage }
            : msg
        ))
      }

    } catch (err) {
      console.error('Error:', err)
      const error = err as Error
      setMessages((prev: Message[]) => [...prev, {
        id: Date.now().toString(),
        content: `Sorry, there was an error: ${error.message}. Please check your API key and try again.`,
        role: 'assistant',
        timestamp: new Date()
      }])
    } finally {
      setIsLoading(false)
    }
  }

  const clearChat = () => {
    setMessages([])
    setPdfSessionId(null)
    setIsPdfMode(false)
  }

  const getReasoningModeIcon = (mode: string) => {
    switch (mode) {
      case 'chain_of_thought': return <Brain className="w-4 h-4" />
      case 'step_by_step': return <Target className="w-4 h-4" />
      default: return <Zap className="w-4 h-4" />
    }
  }

  const getStyleToneIcon = (tone: string) => {
    switch (tone) {
      case 'professional': return <User className="w-4 h-4" />
      case 'casual': return <Sparkles className="w-4 h-4" />
      case 'academic': return <Bot className="w-4 h-4" />
      case 'creative': return <Palette className="w-4 h-4" />
      case 'technical': return <Target className="w-4 h-4" />
      case 'friendly': return <Sparkles className="w-4 h-4" />
      default: return <User className="w-4 h-4" />
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-dark-50 to-dark-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-dark-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-white" />
              </div>
              <h1 className="text-xl font-bold text-dark-900">Enhanced AI Chat</h1>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setShowSettings(!showSettings)}
                className="btn-secondary flex items-center space-x-2"
              >
                <Settings className="w-4 h-4" />
                <span>Settings</span>
              </button>
              <button
                onClick={clearChat}
                className="btn-secondary"
              >
                Clear Chat
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Settings Panel */}
      {showSettings && (
        <div className="bg-white border-b border-dark-200 p-4">
          <div className="max-w-7xl mx-auto">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Basic Settings */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-dark-900">Basic Settings</h3>
                
                <div>
                  <label className="block text-sm font-medium text-dark-700 mb-2">
                    OpenAI API Key
                  </label>
                  <input
                    type="password"
                    value={apiKey}
                    onChange={(e) => setApiKey(e.target.value)}
                    className="input-field w-full"
                    placeholder="Enter your OpenAI API key"
                  />
                </div>

                {/* PDF Upload */}
                <div>
                  <label className="block text-sm font-medium text-dark-700 mb-2">
                    Upload PDF for Chat
                  </label>
                  <div className="flex items-center space-x-2">
                    <input
                      type="file"
                      ref={fileInputRef}
                      onChange={handlePdfUpload}
                      accept=".pdf"
                      className="hidden"
                    />
                    <button
                      onClick={() => fileInputRef.current?.click()}
                      className="btn-secondary flex items-center space-x-2"
                      disabled={!apiKey || isLoading}
                    >
                      <Upload className="w-4 h-4" />
                      <span>Upload PDF</span>
                    </button>
                    {pdfSessionId && (
                      <div className="flex items-center text-sm text-green-600">
                        <FileText className="w-4 h-4 mr-1" />
                        <span>PDF loaded</span>
                      </div>
                    )}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-dark-700 mb-2">
                    System Prompt
                  </label>
                  <textarea
                    value={developerMessage}
                    onChange={(e) => setDeveloperMessage(e.target.value)}
                    placeholder="You are a helpful AI assistant."
                    className="input-field resize-none"
                    rows={3}
                  />
                </div>

                <button
                  onClick={() => setShowAdvancedSettings(!showAdvancedSettings)}
                  className="btn-secondary flex items-center space-x-2"
                >
                  <Zap className="w-4 h-4" />
                  <span>{showAdvancedSettings ? 'Hide' : 'Show'} Advanced Settings</span>
                </button>
              </div>

              {/* Advanced Settings */}
              {showAdvancedSettings && (
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-dark-900">Advanced Settings</h3>
                  
                  <div>
                    <label className="block text-sm font-medium text-dark-700 mb-2">
                      Reasoning Mode
                    </label>
                    <select
                      value={config.reasoningMode}
                      onChange={(e) => setConfig(prev => ({ ...prev, reasoningMode: e.target.value as any }))}
                      className="input-field"
                    >
                      <option value="none">None</option>
                      <option value="chain_of_thought">Chain of Thought</option>
                      <option value="step_by_step">Step by Step</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-dark-700 mb-2">
                      Style Tone
                    </label>
                    <select
                      value={config.styleTone}
                      onChange={(e) => setConfig(prev => ({ ...prev, styleTone: e.target.value as any }))}
                      className="input-field"
                    >
                      <option value="professional">Professional</option>
                      <option value="casual">Casual</option>
                      <option value="academic">Academic</option>
                      <option value="creative">Creative</option>
                      <option value="technical">Technical</option>
                      <option value="friendly">Friendly</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-dark-700 mb-2">
                      Accuracy Level
                    </label>
                    <select
                      value={config.accuracyLevel}
                      onChange={(e) => setConfig(prev => ({ ...prev, accuracyLevel: e.target.value as any }))}
                      className="input-field"
                    >
                      <option value="standard">Standard</option>
                      <option value="high">High</option>
                      <option value="maximum">Maximum</option>
                    </select>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-dark-700 mb-2">
                        Temperature: {config.temperature}
                      </label>
                      <input
                        type="range"
                        min="0"
                        max="2"
                        step="0.1"
                        value={config.temperature}
                        onChange={(e) => setConfig(prev => ({ ...prev, temperature: parseFloat(e.target.value) }))}
                        className="w-full"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-dark-700 mb-2">
                        Max Tokens: {config.maxTokens}
                      </label>
                      <input
                        type="range"
                        min="100"
                        max="4000"
                        step="100"
                        value={config.maxTokens}
                        onChange={(e) => setConfig(prev => ({ ...prev, maxTokens: parseInt(e.target.value) }))}
                        className="w-full"
                      />
                    </div>
                  </div>

                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      id="citations"
                      checked={config.includeCitations}
                      onChange={(e) => setConfig(prev => ({ ...prev, includeCitations: e.target.checked }))}
                      className="rounded"
                    />
                    <label htmlFor="citations" className="text-sm font-medium text-dark-700">
                      Include Citations
                    </label>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-dark-700 mb-2">
                      Custom Instructions
                    </label>
                    <textarea
                      value={config.customInstructions}
                      onChange={(e) => setConfig(prev => ({ ...prev, customInstructions: e.target.value }))}
                      placeholder="Additional instructions for the AI..."
                      className="input-field resize-none"
                      rows={2}
                    />
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Current Configuration Display */}
      {showAdvancedSettings && (
        <div className="bg-primary-50 border-b border-primary-200 p-3">
          <div className="max-w-7xl mx-auto">
            <div className="flex items-center justify-center space-x-6 text-sm">
              <div className="flex items-center space-x-2">
                {getReasoningModeIcon(config.reasoningMode)}
                <span className="font-medium">Reasoning: {config.reasoningMode.replace('_', ' ')}</span>
              </div>
              <div className="flex items-center space-x-2">
                {getStyleToneIcon(config.styleTone)}
                <span className="font-medium">Style: {config.styleTone}</span>
              </div>
              <div className="flex items-center space-x-2">
                <Target className="w-4 h-4" />
                <span className="font-medium">Accuracy: {config.accuracyLevel}</span>
              </div>
              {config.includeCitations && (
                <div className="flex items-center space-x-2">
                  <Sparkles className="w-4 h-4" />
                  <span className="font-medium">Citations: On</span>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Main Chat Area */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-xl shadow-lg overflow-hidden">
          {/* Messages */}
          <div className="h-96 overflow-y-auto p-6">
            {messages.length === 0 ? (
              <div className="text-center py-12">
                <Bot className="w-12 h-12 text-primary-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-dark-900 mb-2">
                  Enhanced AI Chat
                </h3>
                <p className="text-dark-600 mb-4">
                  Start a conversation with advanced features like chain-of-thought reasoning, style guidance, and accuracy control.
                </p>
                <div className="flex justify-center space-x-4 text-sm text-dark-500">
                  <div className="flex items-center space-x-1">
                    <Brain className="w-4 h-4" />
                    <span>Chain of Thought</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <Palette className="w-4 h-4" />
                    <span>Style Control</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <Target className="w-4 h-4" />
                    <span>Accuracy Levels</span>
                  </div>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`chat-message ${
                      message.role === 'user' ? 'user-message' : 'assistant-message'
                    }`}
                  >
                    <div className="flex items-start space-x-3">
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                        message.role === 'user' ? 'bg-primary-400' : 'bg-dark-200'
                      }`}>
                        {message.role === 'user' ? (
                          <User className="w-4 h-4 text-white" />
                        ) : (
                          <Bot className="w-4 h-4 text-dark-600" />
                        )}
                      </div>
                      <div className="flex-1">
                        <div className="whitespace-pre-wrap">{message.content}</div>
                        <div className="text-xs text-dark-400 mt-2">
                          {message.timestamp.toLocaleTimeString()}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
                {isLoading && (
                  <div className="chat-message assistant-message">
                    <div className="flex items-start space-x-3">
                      <div className="w-8 h-8 rounded-full bg-dark-200 flex items-center justify-center">
                        <Bot className="w-4 h-4 text-dark-600" />
                      </div>
                      <div className="typing-indicator">
                        <div className="typing-dot"></div>
                        <div className="typing-dot" style={{ animationDelay: '0.2s' }}></div>
                        <div className="typing-dot" style={{ animationDelay: '0.4s' }}></div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Form */}
          <div className="border-t border-dark-200 p-4">
            <form onSubmit={handleSubmit} className="flex space-x-4">
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                placeholder="Type your message here..."
                className="input-field flex-1"
                disabled={isLoading || !apiKey.trim()}
              />
              <button
                type="submit"
                disabled={isLoading || !inputMessage.trim() || !apiKey.trim()}
                className="btn-primary flex items-center space-x-2"
              >
                <Send className="w-4 h-4" />
                <span>Send</span>
              </button>
            </form>
            {!apiKey.trim() && (
              <p className="text-sm text-red-600 mt-2">
                Please enter your OpenAI API key in the settings to start chatting.
              </p>
            )}
          </div>
        </div>
      </main>
    </div>
  )
} 