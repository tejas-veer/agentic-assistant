import { useState, useEffect, useRef, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Mic, MicOff, X, Send, Sparkles, ShoppingCart, Plus, ArrowRight, Volume2, VolumeX, Info, AlertCircle } from 'lucide-react'
import { useKioskStore } from '@/lib/store'
import { assistantApi, cartApi, menuApi, type MenuItem, type Category } from '@/lib/api'

interface SpeechRecognitionEvent {
  resultIndex: number
  results: {
    [key: number]: {
      [key: number]: {
        transcript: string
      }
      isFinal: boolean
    }
    length: number
  }
}

interface SpeechRecognitionErrorEvent {
  error: string
}

interface SpeechRecognitionInstance {
  continuous: boolean
  interimResults: boolean
  lang: string
  onstart: () => void
  onresult: (event: SpeechRecognitionEvent) => void
  onerror: (event: SpeechRecognitionErrorEvent) => void
  onend: () => void
  start: () => void
  stop: () => void
}

interface MessageContent {
  type: 'text' | 'menu-items' | 'cart-summary' | 'order-confirmed' | 'suggestions'
  text?: string
  items?: MenuItem[]
  cartTotal?: number
  orderNumber?: string
  suggestions?: string[]
  cartItems?: { name: string; quantity: number; price: number }[]
}

interface Message {
  role: 'user' | 'assistant'
  content: MessageContent[]
}

const categoryEmojis: Record<string, string> = {
  'Burgers': '🍔',
  'Pizzas': '🍕',
  'Sides': '🍟',
  'Drinks': '🥤',
  'Desserts': '🍰',
}

const formatPrice = (price: number) => `₹${price.toFixed(0)}`

const cleanResponseText = (text: string): string => {
  if (!text) return ''
  
  const jsonMatch = text.match(/\{[\s\S]*"response"[\s\S]*\}/)
  if (jsonMatch) {
    try {
      const parsed = JSON.parse(jsonMatch[0])
      if (parsed.response) {
        return parsed.response
      }
    } catch {
      const beforeJson = text.substring(0, text.indexOf('{')).trim()
      if (beforeJson) return beforeJson
    }
  }
  
  return text.replace(/\{[\s\S]*\}/g, '').trim() || text
}

interface VoiceStatus {
  sttSupported: boolean
  ttsSupported: boolean
  micPermission: 'granted' | 'denied' | 'prompt' | 'unknown'
  error: string | null
}

export default function VoiceAssistant() {
  const { sessionId, deviceId, setVoiceActive, cart, setCart, assistantSessionId, setAssistantSession } = useKioskStore()
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isListening, setIsListening] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [isSpeaking, setIsSpeaking] = useState(false)
  const [voiceEnabled, setVoiceEnabled] = useState(true)
  const [transcript, setTranscript] = useState('')
  const [menuData, setMenuData] = useState<Category[]>([])
  const [showQuickActions, setShowQuickActions] = useState(true)
  const [voiceStatus, setVoiceStatus] = useState<VoiceStatus>({
    sttSupported: false,
    ttsSupported: false,
    micPermission: 'unknown',
    error: null
  })
  const [showStatus, setShowStatus] = useState(false)
  
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)
  const recognitionRef = useRef<SpeechRecognitionInstance | null>(null)
  const synthRef = useRef<SpeechSynthesis | null>(null)

  useEffect(() => {
    loadMenu()
    initSession()
    initSpeech()
    checkMicPermission()
    
    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop()
      }
      if (synthRef.current) {
        synthRef.current.cancel()
      }
    }
  }, [])
  
  const checkMicPermission = async () => {
    try {
      const result = await navigator.permissions.query({ name: 'microphone' as PermissionName })
      setVoiceStatus(prev => ({ ...prev, micPermission: result.state as 'granted' | 'denied' | 'prompt' }))
      
      result.onchange = () => {
        setVoiceStatus(prev => ({ ...prev, micPermission: result.state as 'granted' | 'denied' | 'prompt' }))
      }
    } catch {
      console.log('Permission API not supported')
    }
  }

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const initSpeech = () => {
    if (typeof window !== 'undefined') {
      const ttsSupported = 'speechSynthesis' in window
      synthRef.current = ttsSupported ? window.speechSynthesis : null
      
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const SpeechRecognitionAPI = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
      const sttSupported = !!SpeechRecognitionAPI
      
      setVoiceStatus(prev => ({
        ...prev,
        sttSupported,
        ttsSupported,
        error: !sttSupported ? 'Speech recognition not supported. Use Chrome browser.' : null
      }))
      
      console.log('🔊 TTS Supported:', ttsSupported)
      console.log('🎤 STT Supported:', sttSupported)
      
      if (SpeechRecognitionAPI) {
        const recognition = new SpeechRecognitionAPI() as SpeechRecognitionInstance
        recognition.continuous = false
        recognition.interimResults = true
        recognition.lang = 'en-US'
        
        recognition.onstart = () => {
          console.log('🎤 Voice recognition started')
          setIsListening(true)
          setTranscript('')
          setVoiceStatus(prev => ({ ...prev, error: null }))
        }
        
        recognition.onresult = (event: SpeechRecognitionEvent) => {
          let finalTranscript = ''
          let interimTranscript = ''
          
          for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcriptText = event.results[i][0].transcript
            if (event.results[i].isFinal) {
              finalTranscript += transcriptText
            } else {
              interimTranscript += transcriptText
            }
          }
          
          console.log('🎤 Transcript:', interimTranscript || finalTranscript)
          setTranscript(interimTranscript || finalTranscript)
          
          if (finalTranscript) {
            console.log('🎤 Final transcript:', finalTranscript)
            handleSend(finalTranscript)
          }
        }
        
        recognition.onerror = (event: SpeechRecognitionErrorEvent) => {
          console.error('🎤 Speech recognition error:', event.error)
          setIsListening(false)
          setTranscript('')
          
          let errorMsg = 'Voice error: ' + event.error
          if (event.error === 'not-allowed') {
            errorMsg = 'Microphone access denied. Please allow microphone permission.'
            setVoiceStatus(prev => ({ ...prev, micPermission: 'denied' }))
          } else if (event.error === 'no-speech') {
            errorMsg = 'No speech detected. Please try again.'
          } else if (event.error === 'network') {
            errorMsg = 'Network error. Check your internet connection.'
          }
          
          setVoiceStatus(prev => ({ ...prev, error: errorMsg }))
        }
        
        recognition.onend = () => {
          console.log('🎤 Voice recognition ended')
          setIsListening(false)
        }
        
        recognitionRef.current = recognition
      }
    }
  }

  const speak = useCallback((text: string) => {
    if (!voiceEnabled || !synthRef.current) return
    
    synthRef.current.cancel()
    
    const cleanText = cleanResponseText(text)
      .replace(/[*_`#]/g, '')
      .replace(/₹(\d+)/g, '$1 rupees')
      .replace(/\$(\d+\.?\d*)/g, '$1 rupees')
    
    const utterance = new SpeechSynthesisUtterance(cleanText)
    utterance.rate = 1.0
    utterance.pitch = 1.0
    utterance.volume = 1.0
    
    const voices = synthRef.current.getVoices()
    const preferredVoice = voices.find(v => 
      v.name.includes('Google') || 
      v.name.includes('Samantha') || 
      v.name.includes('Microsoft Zira')
    ) || voices.find(v => v.lang.startsWith('en'))
    
    if (preferredVoice) {
      utterance.voice = preferredVoice
    }
    
    utterance.onstart = () => {
      console.log('🔊 Speaking:', cleanText.substring(0, 50) + '...')
      setIsSpeaking(true)
    }
    
    utterance.onend = () => {
      console.log('🔊 Finished speaking')
      setIsSpeaking(false)
    }
    
    utterance.onerror = () => {
      setIsSpeaking(false)
    }
    
    synthRef.current.speak(utterance)
  }, [voiceEnabled])

  const toggleListening = async () => {
    if (!recognitionRef.current) {
      setVoiceStatus(prev => ({ ...prev, error: 'Speech recognition not supported. Use Chrome browser.' }))
      return
    }
    
    if (isListening) {
      recognitionRef.current.stop()
      return
    }
    
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      stream.getTracks().forEach(track => track.stop())
      
      setVoiceStatus(prev => ({ ...prev, micPermission: 'granted', error: null }))
      
      if (synthRef.current) {
        synthRef.current.cancel()
      }
      setIsSpeaking(false)
      
      console.log('🎤 Starting voice recognition...')
      recognitionRef.current.start()
    } catch (err) {
      console.error('🎤 Microphone access error:', err)
      setVoiceStatus(prev => ({ 
        ...prev, 
        micPermission: 'denied',
        error: 'Microphone access denied. Please allow microphone in browser settings.'
      }))
    }
  }

  const loadMenu = async () => {
    try {
      const menu = await menuApi.getMenu()
      setMenuData(menu)
    } catch (e) {
      console.error('Failed to load menu', e)
    }
  }

  const initSession = async () => {
    if (!assistantSessionId) {
      try {
        const session = await assistantApi.createSession({
          assistant_type: 'voice',
          device_id: deviceId,
        })
        setAssistantSession(session.session_id)
      } catch {
        console.error('Failed to create session')
      }
    }
  }

  const addToCart = async (item: MenuItem) => {
    try {
      const updatedCart = await cartApi.addItem(sessionId, deviceId, {
        menu_item_id: item.id,
        quantity: 1,
      })
      setCart(updatedCart)
      
      const message = `Added ${item.name} to your cart!`
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: [{ type: 'text', text: message }]
      }])
      speak(message)
    } catch (e) {
      console.error('Failed to add to cart', e)
    }
  }

  const generateFollowUpSuggestions = (text: string, items: MenuItem[]): string[] => {
    const suggestions: string[] = []
    const textLower = text.toLowerCase()
    
    if (items.length > 0) {
      suggestions.push(`Add ${items[0].name} to cart`)
      if (items.length > 1) {
        suggestions.push(`Tell me more about ${items[1].name}`)
      }
    }
    
    if (textLower.includes('burger')) {
      suggestions.push("What sides go well with burgers?")
      suggestions.push("Any drink recommendations?")
    } else if (textLower.includes('pizza')) {
      suggestions.push("What toppings are available?")
      suggestions.push("Do you have garlic bread?")
    } else if (textLower.includes('vegetarian') || textLower.includes('veggie')) {
      suggestions.push("Any vegan options?")
      suggestions.push("What about gluten-free?")
    } else if (textLower.includes('drink')) {
      suggestions.push("What desserts do you have?")
      suggestions.push("Any combo deals?")
    } else if (textLower.includes('dessert') || textLower.includes('sweet')) {
      suggestions.push("I'm ready to order")
      suggestions.push("Show my cart")
    }
    
    if (textLower.includes('cart') || textLower.includes('added')) {
      suggestions.push("What else do you recommend?")
      suggestions.push("I'm ready to checkout")
      suggestions.push("Remove last item")
    }
    
    if (textLower.includes('popular') || textLower.includes('recommend')) {
      suggestions.push("What's the cheapest option?")
      suggestions.push("Show me the full menu")
    }
    
    if (suggestions.length === 0) {
      suggestions.push("What's popular?")
      suggestions.push("Show my cart")
      suggestions.push("I need help ordering")
    }
    
    return suggestions.slice(0, 3)
  }

  const parseResponse = (text: string): MessageContent[] => {
    const contents: MessageContent[] = []
    const cleanedText = cleanResponseText(text)
    const mentionedItems = findMentionedItems(cleanedText)
    
    contents.push({ type: 'text', text: cleanedText })
    
    if (mentionedItems.length > 0) {
      contents.push({ type: 'menu-items', items: mentionedItems })
    }
    
    const suggestions = generateFollowUpSuggestions(cleanedText, mentionedItems)
    contents.push({ type: 'suggestions', suggestions })
    
    return contents
  }

  const findMentionedItems = (text: string): MenuItem[] => {
    const items: MenuItem[] = []
    const textLower = text.toLowerCase()
    
    menuData.forEach(category => {
      category.items.forEach(item => {
        if (textLower.includes(item.name.toLowerCase())) {
          if (!items.find(i => i.id === item.id)) {
            items.push(item)
          }
        }
      })
    })
    
    if (items.length === 0) {
      if (textLower.includes('burger')) {
        const burgers = menuData.find(c => c.name === 'Burgers')?.items || []
        items.push(...burgers.slice(0, 3))
      } else if (textLower.includes('pizza')) {
        const pizzas = menuData.find(c => c.name === 'Pizzas')?.items || []
        items.push(...pizzas.slice(0, 3))
      } else if (textLower.includes('vegetarian') || textLower.includes('veggie')) {
        menuData.forEach(category => {
          category.items.forEach(item => {
            if (item.tags?.includes('vegetarian') || item.name.toLowerCase().includes('veggie')) {
              if (!items.find(i => i.id === item.id)) {
                items.push(item)
              }
            }
          })
        })
      } else if (textLower.includes('popular') || textLower.includes('recommend')) {
        menuData.forEach(category => {
          if (category.items.length > 0) {
            items.push(category.items[0])
          }
        })
      }
    }
    
    return items.slice(0, 4)
  }

  const handleSend = async (customText?: string) => {
    const textToSend = customText || input.trim()
    if (!textToSend || isProcessing) return

    setInput('')
    setTranscript('')
    setShowQuickActions(false)
    setMessages(prev => [...prev, { 
      role: 'user', 
      content: [{ type: 'text', text: textToSend }] 
    }])
    setIsProcessing(true)

    const textLower = textToSend.toLowerCase()
    const isCartRequest = textLower.includes('cart') || textLower.includes('checkout') || textLower.includes('my order')
    
    let currentCart = cart
    if (isCartRequest) {
      try {
        const cartData = await cartApi.getCart(sessionId)
        setCart(cartData)
        currentCart = cartData
      } catch (e) {
        console.error('Failed to fetch cart', e)
      }
    }

    try {
      const response = await assistantApi.sendText({
        session_id: assistantSessionId || sessionId,
        text: textToSend,
        device_id: deviceId,
      })

      const contents = parseResponse(response.response)
      
      if (isCartRequest && currentCart && currentCart.items && currentCart.items.length > 0) {
        contents.push({
          type: 'cart-summary',
          cartItems: currentCart.items.map(item => ({
            name: item.menu_item_name,
            quantity: item.quantity,
            price: item.total_price
          })),
          cartTotal: currentCart.total
        })
      } else if (isCartRequest && (!currentCart || !currentCart.items || currentCart.items.length === 0)) {
        contents.push({
          type: 'text',
          text: "Your cart is empty. Would you like me to recommend something?"
        })
      }
      
      setMessages(prev => [...prev, { role: 'assistant', content: contents }])
      
      speak(response.response)

      if (response.action) {
        const cartData = await cartApi.getCart(sessionId)
        setCart(cartData)
      }
    } catch {
      const errorMsg = "I'm having trouble right now. Let me try again..."
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: [{ type: 'text', text: errorMsg }]
      }])
      speak(errorMsg)
    } finally {
      setIsProcessing(false)
    }
  }

  const quickActions = [
    { text: "What's popular?", icon: "🔥" },
    { text: "Show me burgers", icon: "🍔" },
    { text: "Any vegetarian options?", icon: "🥗" },
    { text: "What drinks do you have?", icon: "🥤" },
    { text: "I want something sweet", icon: "🍰" },
    { text: "Show my cart", icon: "🛒" },
  ]

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-[100] bg-surface-950"
    >
      <div 
        className="absolute inset-0 opacity-60 pointer-events-none"
        style={{ background: 'var(--gradient-mesh)' }}
      />

      <div className="relative h-full flex flex-col max-w-4xl mx-auto">
        <motion.header 
          initial={{ y: -50, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          className="flex items-center justify-between p-6"
        >
          <div className="flex items-center gap-4">
            <motion.div 
              animate={{ 
                rotate: isSpeaking ? [0, 5, -5, 0] : 0,
                scale: isSpeaking ? [1, 1.05, 1] : 1
              }}
              transition={{ repeat: isSpeaking ? Infinity : 0, duration: 0.5 }}
              className={`w-14 h-14 rounded-2xl flex items-center justify-center shadow-lg ${
                isSpeaking 
                  ? 'bg-gradient-to-br from-green-400 to-emerald-500 shadow-green-500/30' 
                  : 'bg-gradient-to-br from-brand-400 via-pink-500 to-purple-500 shadow-brand-500/30'
              }`}
            >
              {isSpeaking ? (
                <Volume2 className="w-7 h-7 text-white animate-pulse" />
              ) : (
                <Sparkles className="w-7 h-7 text-white" />
              )}
            </motion.div>
            <div>
              <h1 className="font-display text-2xl font-bold text-white">Voice Assistant</h1>
              <div className="flex items-center gap-2">
                <p className="text-white/50 text-sm">
                  {isListening ? '🎤 Listening...' : isSpeaking ? '🔊 Speaking...' : 'Tap mic to speak'}
                </p>
                {showStatus && (
                  <div className="flex items-center gap-1.5">
                    <span className={`w-2 h-2 rounded-full ${voiceStatus.sttSupported ? 'bg-green-400' : 'bg-red-400'}`} title="Speech Recognition" />
                    <span className={`w-2 h-2 rounded-full ${voiceStatus.ttsSupported ? 'bg-green-400' : 'bg-red-400'}`} title="Text to Speech" />
                    <span className={`w-2 h-2 rounded-full ${
                      voiceStatus.micPermission === 'granted' ? 'bg-green-400' : 
                      voiceStatus.micPermission === 'denied' ? 'bg-red-400' : 'bg-yellow-400'
                    }`} title="Microphone" />
                  </div>
                )}
              </div>
            </div>
          </div>
          
          <div className="flex items-center gap-3">
            <motion.button
              whileTap={{ scale: 0.9 }}
              onClick={() => setShowStatus(!showStatus)}
              className="p-2 rounded-lg bg-white/5 text-white/50 hover:bg-white/10"
              title="Toggle status"
            >
              <Info className="w-4 h-4" />
            </motion.button>
            <motion.button
              whileTap={{ scale: 0.9 }}
              onClick={() => setVoiceEnabled(!voiceEnabled)}
              className={`p-3 rounded-xl transition-colors ${
                voiceEnabled ? 'bg-green-500/20 text-green-400' : 'bg-white/10 text-white/50'
              }`}
              title={voiceEnabled ? 'Voice responses ON' : 'Voice responses OFF'}
            >
              {voiceEnabled ? <Volume2 className="w-5 h-5" /> : <VolumeX className="w-5 h-5" />}
            </motion.button>
            
            {cart && cart.items.length > 0 && (
              <motion.div 
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                className="flex items-center gap-2 bg-white/10 px-4 py-2 rounded-xl"
              >
                <ShoppingCart className="w-5 h-5 text-brand-400" />
                <span className="text-white font-semibold">{formatPrice(cart.total)}</span>
                <span className="bg-brand-500 text-white text-xs px-2 py-0.5 rounded-full">
                  {cart.items.length}
                </span>
              </motion.div>
            )}
            
            <motion.button
              whileTap={{ scale: 0.9 }}
              onClick={() => setVoiceActive(false)}
              className="p-3 rounded-xl bg-white/10 hover:bg-white/20 transition-colors"
            >
              <X className="w-6 h-6 text-white" />
            </motion.button>
          </div>
        </motion.header>

        <AnimatePresence>
          {voiceStatus.error && (
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="mx-6 mb-4 p-4 bg-red-500/20 border border-red-500/30 rounded-xl flex items-center gap-3"
            >
              <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0" />
              <p className="text-red-200 text-sm flex-1">{voiceStatus.error}</p>
              <button 
                onClick={() => setVoiceStatus(prev => ({ ...prev, error: null }))}
                className="text-red-300 hover:text-red-100"
              >
                <X className="w-4 h-4" />
              </button>
            </motion.div>
          )}
        </AnimatePresence>

        {showStatus && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            className="mx-6 mb-4 p-4 bg-white/5 border border-white/10 rounded-xl"
          >
            <h4 className="text-white/80 text-sm font-medium mb-3">Voice Status</h4>
            <div className="grid grid-cols-3 gap-4 text-sm">
              <div className="flex items-center gap-2">
                <span className={`w-3 h-3 rounded-full ${voiceStatus.sttSupported ? 'bg-green-400' : 'bg-red-400'}`} />
                <span className="text-white/60">Speech Recognition</span>
              </div>
              <div className="flex items-center gap-2">
                <span className={`w-3 h-3 rounded-full ${voiceStatus.ttsSupported ? 'bg-green-400' : 'bg-red-400'}`} />
                <span className="text-white/60">Text to Speech</span>
              </div>
              <div className="flex items-center gap-2">
                <span className={`w-3 h-3 rounded-full ${
                  voiceStatus.micPermission === 'granted' ? 'bg-green-400' : 
                  voiceStatus.micPermission === 'denied' ? 'bg-red-400' : 'bg-yellow-400'
                }`} />
                <span className="text-white/60">
                  Mic: {voiceStatus.micPermission === 'granted' ? 'Allowed' : 
                        voiceStatus.micPermission === 'denied' ? 'Blocked' : 'Prompt'}
                </span>
              </div>
            </div>
            {voiceStatus.micPermission === 'denied' && (
              <p className="mt-3 text-yellow-400/80 text-xs">
                ⚠️ Microphone is blocked. Click the lock/info icon in your browser's address bar to allow microphone access.
              </p>
            )}
            {!voiceStatus.sttSupported && (
              <p className="mt-3 text-yellow-400/80 text-xs">
                ⚠️ Speech Recognition requires Chrome browser. Firefox/Safari have limited support.
              </p>
            )}
          </motion.div>
        )}

        <div className="flex-1 overflow-y-auto px-6 pb-4 custom-scrollbar">
          {messages.length === 0 && showQuickActions && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex flex-col items-center justify-center h-full"
            >
              <motion.div
                animate={{ 
                  scale: isListening ? [1, 1.2, 1] : [1, 1.05, 1],
                  boxShadow: isListening 
                    ? ['0 0 0 0 rgba(239, 68, 68, 0.4)', '0 0 0 20px rgba(239, 68, 68, 0)', '0 0 0 0 rgba(239, 68, 68, 0.4)']
                    : undefined
                }}
                transition={{ repeat: Infinity, duration: isListening ? 1 : 2 }}
                className={`w-32 h-32 rounded-full flex items-center justify-center mb-8 shadow-2xl cursor-pointer ${
                  isListening 
                    ? 'bg-red-500 shadow-red-500/40' 
                    : 'bg-gradient-to-br from-brand-400 via-pink-500 to-purple-500 shadow-brand-500/40'
                }`}
                onClick={toggleListening}
              >
                {isListening ? (
                  <MicOff className="w-16 h-16 text-white" />
                ) : (
                  <Mic className="w-16 h-16 text-white" />
                )}
              </motion.div>
              
              {isListening && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="mb-4 px-6 py-4 bg-red-500/20 border border-red-500/30 rounded-2xl min-w-[200px]"
                >
                  {transcript ? (
                    <p className="text-white text-lg text-center">{transcript}</p>
                  ) : (
                    <div className="flex items-center justify-center gap-2">
                      <span className="w-2 h-2 bg-red-400 rounded-full animate-pulse" />
                      <span className="w-2 h-2 bg-red-400 rounded-full animate-pulse" style={{ animationDelay: '0.2s' }} />
                      <span className="w-2 h-2 bg-red-400 rounded-full animate-pulse" style={{ animationDelay: '0.4s' }} />
                      <span className="text-red-200 ml-2">Waiting for speech...</span>
                    </div>
                  )}
                </motion.div>
              )}
              
              <h2 className="font-display text-3xl font-bold text-white mb-3 text-center">
                {isListening ? (transcript ? "Hearing you..." : "I'm listening...") : "Tap to speak"}
              </h2>
              <p className="text-white/50 text-lg mb-10 text-center max-w-md">
                {isListening 
                  ? (transcript ? "Release or tap again to send" : "Speak clearly into your microphone")
                  : voiceStatus.sttSupported 
                    ? "Or tap a suggestion below" 
                    : "Speech not supported - use text input below"
                }
              </p>
              
              {!isListening && (
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3 w-full max-w-2xl">
                  {quickActions.map((action, i) => (
                    <motion.button
                      key={i}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: i * 0.1 }}
                      whileHover={{ scale: 1.03, y: -2 }}
                      whileTap={{ scale: 0.97 }}
                      onClick={() => handleSend(action.text)}
                      className="flex items-center gap-3 p-4 bg-white/5 hover:bg-white/10 border border-white/10 rounded-2xl transition-all group"
                    >
                      <span className="text-2xl">{action.icon}</span>
                      <span className="text-white/80 group-hover:text-white text-left text-sm font-medium">
                        {action.text}
                      </span>
                    </motion.button>
                  ))}
                </div>
              )}
            </motion.div>
          )}

          <AnimatePresence mode="popLayout">
            {messages.map((msg, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className={`mb-6 ${msg.role === 'user' ? 'flex justify-end' : ''}`}
              >
                {msg.role === 'user' ? (
                  <div className="max-w-md">
                    <div className="bg-gradient-to-r from-brand-500 to-pink-500 rounded-3xl rounded-br-lg px-6 py-4 shadow-lg shadow-brand-500/20">
                      <p className="text-white text-lg">{msg.content[0]?.text}</p>
                    </div>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {msg.content.map((content, j) => (
                      <div key={j}>
                        {content.type === 'text' && content.text && (
                          <motion.div 
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            className="flex gap-4"
                          >
                            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-brand-400 to-pink-500 flex items-center justify-center flex-shrink-0 shadow-lg">
                              <Sparkles className="w-5 h-5 text-white" />
                            </div>
                            <div className="bg-white/5 border border-white/10 rounded-3xl rounded-bl-lg px-6 py-4 max-w-2xl">
                              <p className="text-white/90 text-lg leading-relaxed">{content.text}</p>
                            </div>
                          </motion.div>
                        )}
                        
                        {content.type === 'menu-items' && content.items && content.items.length > 0 && (
                          <motion.div 
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.2 }}
                            className="ml-14 mt-4"
                          >
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                              {content.items.map((item, idx) => (
                                <motion.div
                                  key={item.id}
                                  initial={{ opacity: 0, scale: 0.9 }}
                                  animate={{ opacity: 1, scale: 1 }}
                                  transition={{ delay: idx * 0.1 }}
                                  className="group bg-white/5 hover:bg-white/10 border border-white/10 rounded-2xl p-4 transition-all cursor-pointer"
                                  onClick={() => addToCart(item)}
                                >
                                  <div className="flex gap-4">
                                    <div className="w-20 h-20 rounded-xl bg-gradient-to-br from-surface-700 to-surface-800 flex items-center justify-center text-3xl flex-shrink-0">
                                      {categoryEmojis[menuData.find(c => c.items.some(i => i.id === item.id))?.name || ''] || '🍽️'}
                                    </div>
                                    <div className="flex-1 min-w-0">
                                      <h4 className="font-semibold text-white truncate">{item.name}</h4>
                                      <p className="text-white/50 text-sm line-clamp-2 mb-2">{item.description}</p>
                                      <div className="flex items-center justify-between">
                                        <span className="text-brand-400 font-bold text-lg">{formatPrice(item.price)}</span>
                                        <motion.button
                                          whileHover={{ scale: 1.1 }}
                                          whileTap={{ scale: 0.9 }}
                                          className="p-2 bg-brand-500 hover:bg-brand-600 rounded-xl text-white transition-colors"
                                        >
                                          <Plus className="w-5 h-5" />
                                        </motion.button>
                                      </div>
                                    </div>
                                  </div>
                                  {item.tags && item.tags.length > 0 && (
                                    <div className="flex gap-2 mt-3 flex-wrap">
                                      {item.tags.slice(0, 3).map((tag, ti) => (
                                        <span key={ti} className="px-2 py-1 bg-white/10 rounded-full text-xs text-white/60">
                                          {tag}
                                        </span>
                                      ))}
                                    </div>
                                  )}
                                </motion.div>
                              ))}
                            </div>
                          </motion.div>
                        )}
                        
                        {content.type === 'cart-summary' && content.cartItems && content.cartItems.length > 0 && (
                          <motion.div 
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.2 }}
                            className="ml-14 mt-4"
                          >
                            <div className="bg-gradient-to-br from-white/5 to-white/10 border border-white/10 rounded-2xl p-5 max-w-md">
                              <div className="flex items-center gap-3 mb-4 pb-3 border-b border-white/10">
                                <ShoppingCart className="w-5 h-5 text-brand-400" />
                                <h4 className="font-semibold text-white">Your Cart</h4>
                              </div>
                              
                              <div className="space-y-3 mb-4">
                                {content.cartItems.map((item, ci) => (
                                  <motion.div 
                                    key={ci}
                                    initial={{ opacity: 0, x: -10 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    transition={{ delay: ci * 0.1 }}
                                    className="flex items-center justify-between"
                                  >
                                    <div className="flex items-center gap-3">
                                      <span className="w-7 h-7 bg-white/10 rounded-lg flex items-center justify-center text-sm text-white/80">
                                        {item.quantity}x
                                      </span>
                                      <span className="text-white">{item.name}</span>
                                    </div>
                                    <span className="text-white/70">{formatPrice(item.price)}</span>
                                  </motion.div>
                                ))}
                              </div>
                              
                              <div className="pt-3 border-t border-white/10 flex items-center justify-between">
                                <span className="text-white/70">Total</span>
                                <span className="text-xl font-bold text-brand-400">{formatPrice(content.cartTotal || 0)}</span>
                              </div>
                              
                              <motion.button
                                whileHover={{ scale: 1.02 }}
                                whileTap={{ scale: 0.98 }}
                                onClick={() => setVoiceActive(false)}
                                className="w-full mt-4 py-3 bg-gradient-to-r from-brand-500 to-pink-500 hover:from-brand-600 hover:to-pink-600 text-white font-semibold rounded-xl transition-all flex items-center justify-center gap-2"
                              >
                                <span>Proceed to Checkout</span>
                                <ArrowRight className="w-4 h-4" />
                              </motion.button>
                            </div>
                          </motion.div>
                        )}
                        
                        {content.type === 'suggestions' && content.suggestions && content.suggestions.length > 0 && i === messages.length - 1 && (
                          <motion.div 
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.4 }}
                            className="ml-14 mt-4"
                          >
                            <p className="text-white/40 text-sm mb-2">Try saying:</p>
                            <div className="flex flex-wrap gap-2">
                              {content.suggestions.map((suggestion, si) => (
                                <motion.button
                                  key={si}
                                  initial={{ opacity: 0, scale: 0.9 }}
                                  animate={{ opacity: 1, scale: 1 }}
                                  transition={{ delay: 0.5 + si * 0.1 }}
                                  whileHover={{ scale: 1.03 }}
                                  whileTap={{ scale: 0.97 }}
                                  onClick={() => handleSend(suggestion)}
                                  className="px-4 py-2 bg-gradient-to-r from-white/5 to-white/10 hover:from-white/10 hover:to-white/15 border border-white/10 hover:border-white/20 rounded-full text-white/80 hover:text-white text-sm transition-all flex items-center gap-2"
                                >
                                  <span>{suggestion}</span>
                                  <ArrowRight className="w-3 h-3 opacity-50" />
                                </motion.button>
                              ))}
                            </div>
                          </motion.div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </motion.div>
            ))}
          </AnimatePresence>

          {isProcessing && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex gap-4 mb-6"
            >
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-brand-400 to-pink-500 flex items-center justify-center flex-shrink-0">
                <Sparkles className="w-5 h-5 text-white animate-pulse" />
              </div>
              <div className="bg-white/5 border border-white/10 rounded-3xl rounded-bl-lg px-6 py-4">
                <div className="flex gap-2">
                  <motion.span 
                    animate={{ scale: [1, 1.3, 1] }}
                    transition={{ repeat: Infinity, duration: 0.6, delay: 0 }}
                    className="w-3 h-3 bg-brand-400 rounded-full"
                  />
                  <motion.span 
                    animate={{ scale: [1, 1.3, 1] }}
                    transition={{ repeat: Infinity, duration: 0.6, delay: 0.2 }}
                    className="w-3 h-3 bg-pink-400 rounded-full"
                  />
                  <motion.span 
                    animate={{ scale: [1, 1.3, 1] }}
                    transition={{ repeat: Infinity, duration: 0.6, delay: 0.4 }}
                    className="w-3 h-3 bg-purple-400 rounded-full"
                  />
                </div>
              </div>
            </motion.div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        <motion.div 
          initial={{ y: 50, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          className="p-6 bg-gradient-to-t from-surface-950 via-surface-950/90 to-transparent pt-12"
        >
          {isListening && transcript && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-4 max-w-2xl mx-auto"
            >
              <div className="bg-red-500/20 border border-red-500/30 rounded-2xl px-4 py-3">
                <p className="text-white/80 text-center">{transcript || 'Listening...'}</p>
              </div>
            </motion.div>
          )}
          
          <div className="flex items-center gap-4 max-w-2xl mx-auto">
            <motion.button
              whileTap={{ scale: 0.9 }}
              onClick={toggleListening}
              className={`relative p-5 rounded-2xl transition-all flex-shrink-0 ${
                isListening 
                  ? 'bg-red-500 shadow-lg shadow-red-500/40' 
                  : 'bg-gradient-to-br from-brand-400 via-pink-500 to-purple-500 shadow-lg shadow-brand-500/30'
              }`}
            >
              {isListening && (
                <>
                  <span className="absolute inset-0 rounded-2xl bg-red-500 animate-ping opacity-30" />
                  <span className="absolute inset-0 rounded-2xl bg-red-500 animate-pulse opacity-50" />
                </>
              )}
              {isListening ? (
                <MicOff className="w-7 h-7 text-white relative z-10" />
              ) : (
                <Mic className="w-7 h-7 text-white relative z-10" />
              )}
            </motion.button>
            
            <div className="flex-1 flex items-center gap-3 bg-white/5 border border-white/10 rounded-2xl p-2">
              <input
                ref={inputRef}
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                placeholder={isListening ? "Listening..." : "Or type your order..."}
                disabled={isListening}
                className="flex-1 bg-transparent px-4 py-3 text-white text-lg placeholder:text-white/30 focus:outline-none"
              />
              
              <motion.button
                whileTap={{ scale: 0.9 }}
                onClick={() => handleSend()}
                disabled={!input.trim() || isProcessing}
                className="p-3 rounded-xl bg-gradient-to-r from-brand-500 to-pink-500 text-white disabled:opacity-30 disabled:cursor-not-allowed hover:from-brand-600 hover:to-pink-600 transition-all"
              >
                <Send className="w-6 h-6" />
              </motion.button>
            </div>
          </div>
          
          {cart && cart.items.length > 0 && (
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-4 max-w-2xl mx-auto"
            >
              <button 
                onClick={() => setVoiceActive(false)}
                className="w-full flex items-center justify-between bg-brand-500 hover:bg-brand-600 text-white rounded-2xl p-4 transition-colors group"
              >
                <div className="flex items-center gap-3">
                  <ShoppingCart className="w-6 h-6" />
                  <span className="font-semibold">View Cart ({cart.items.length} items)</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="font-bold text-lg">{formatPrice(cart.total)}</span>
                  <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </div>
              </button>
            </motion.div>
          )}
          
          <div className="mt-3 max-w-2xl mx-auto flex items-center justify-center gap-4 text-xs text-white/40">
            <button 
              onClick={() => speak("Hello! I'm your voice assistant. How can I help you today?")}
              className="hover:text-white/60 underline"
            >
              Test Voice Output
            </button>
            <span>•</span>
            <span>
              {voiceStatus.sttSupported ? '✓ Voice input ready' : '✗ Voice input unavailable'}
            </span>
            <span>•</span>
            <span>
              {voiceStatus.ttsSupported ? '✓ Voice output ready' : '✗ Voice output unavailable'}
            </span>
          </div>
        </motion.div>
      </div>
    </motion.div>
  )
}
