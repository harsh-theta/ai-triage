"use client"

import type React from "react"

import { useState, useRef, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Send } from "lucide-react"
import type { Message } from "@/app/page"
import { cn } from "@/lib/utils"

interface ChatInterfaceProps {
  messages: Message[]
  onSendMessage: (message: string) => void
  disabled?: boolean
  isLoading?: boolean
  voiceMode?: boolean
}

export function ChatInterface({ messages, onSendMessage, disabled = false, isLoading = false, voiceMode = false }: ChatInterfaceProps) {
  const [input, setInput] = useState("")
  const scrollAreaRef = useRef<HTMLDivElement>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)
  const [isListening, setIsListening] = useState(false)
  const recognitionRef = useRef<any>(null)

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  // Initial focus on mount
  useEffect(() => {
    if (!disabled && !isLoading) {
      inputRef.current?.focus()
    }
  }, [])

  // Auto-focus input after bot responds
  useEffect(() => {
    if (messages.length === 0) return
    const lastMsg = messages[messages.length - 1]
    if (lastMsg.role === "assistant" && !disabled && !isLoading) {
      // Small delay to ensure the message is rendered and loading is complete
      const timer = setTimeout(() => {
        inputRef.current?.focus()
      }, 100)
      return () => clearTimeout(timer)
    }
  }, [messages, disabled, isLoading])

  // TTS: Play assistant messages when they arrive and voiceMode is on
  useEffect(() => {
    if (!voiceMode) return
    if (messages.length === 0) return
    const lastMsg = messages[messages.length - 1]
    if (lastMsg.role === "assistant" && lastMsg.content) {
      // Cancel any ongoing speech
      window.speechSynthesis.cancel()
      
      // Use TTS microservice audio if available, otherwise fallback to browser TTS
      if (lastMsg.audio_url) {
        const audio = new Audio(lastMsg.audio_url)
        audio.play().catch(error => {
          console.error("Failed to play TTS audio:", error)
          // Fallback to browser TTS if audio fails
          const utter = new window.SpeechSynthesisUtterance(lastMsg.content)
          utter.rate = 1
          utter.pitch = 1
          window.speechSynthesis.speak(utter)
        })
      } else {
        // Fallback to browser TTS if no audio_url
        const utter = new window.SpeechSynthesisUtterance(lastMsg.content)
        utter.rate = 1
        utter.pitch = 1
        window.speechSynthesis.speak(utter)
      }
    }
  }, [messages, voiceMode])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (input.trim() && !disabled && !isLoading) {
      onSendMessage(input.trim())
      setInput("")
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  // STT: Start/stop speech recognition
  const handleMicClick = () => {
    if (!isListening) {
      // @ts-ignore
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
      if (!SpeechRecognition) {
        alert("Speech recognition is not supported in this browser.")
        return
      }
      const recognition = new SpeechRecognition()
      recognition.lang = "en-US"
      recognition.interimResults = false
      recognition.maxAlternatives = 1
      recognition.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript
        setInput(transcript)
        setIsListening(false)
        
        // In voice mode, automatically send the message after recognition
        if (voiceMode && transcript.trim()) {
          onSendMessage(transcript.trim())
          setInput("")
        }
      }
      recognition.onerror = () => {
        setIsListening(false)
      }
      recognition.onend = () => {
        setIsListening(false)
      }
      recognitionRef.current = recognition
      setIsListening(true)
      recognition.start()
    } else {
      recognitionRef.current?.stop()
      setIsListening(false)
      
      // In voice mode, if there's text in input, send it when stopping manually
      if (voiceMode && input.trim()) {
        onSendMessage(input.trim())
        setInput("")
      }
    }
  }

  return (
    <div className="flex flex-col h-full">
      {/* Messages */}
      <ScrollArea className="flex-1 p-4" ref={scrollAreaRef}>
        <div className="space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={cn("flex w-full", message.role === "user" ? "justify-end" : "justify-start")}
            >
              <div
                className={cn(
                  "max-w-[80%] rounded-lg px-4 py-2",
                  message.role === "user" ? "bg-blue-600 text-white" : "bg-gray-100 text-gray-900",
                )}
              >
                <p className="text-sm">{message.content}</p>
                <p className={cn("text-xs mt-1", message.role === "user" ? "text-blue-100" : "text-gray-500")}>
                  {message.timestamp.toLocaleTimeString()}
                </p>
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>
      </ScrollArea>

      {/* Input */}
      <div className="p-4 border-t">
        {voiceMode ? (
          // Voice Mode: Only show mic button with status
          <div className="flex flex-col items-center gap-3">
            {isListening && (
              <div className="text-sm text-blue-600 font-medium animate-pulse">
                🎤 Listening... Click to stop and send
              </div>
            )}
            {!isListening && input.trim() && (
              <div className="text-sm text-gray-600 bg-gray-100 rounded-lg px-3 py-2 max-w-full overflow-hidden">
                "{input}"
              </div>
            )}
            <Button
              type="button"
              onClick={handleMicClick}
              disabled={disabled || isLoading}
              variant={isListening ? "default" : "outline"}
              size="lg"
              className={cn(
                "w-20 h-20 rounded-full transition-all duration-200 shadow-lg",
                isListening 
                  ? "bg-red-500 hover:bg-red-600 animate-pulse shadow-red-200" 
                  : "hover:scale-105 shadow-blue-100 border-2 border-blue-200"
              )}
              aria-label={isListening ? "Stop listening and send" : "Start listening"}
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill={isListening ? "white" : "currentColor"}
                className="h-16 w-16"
              >
                <path d="M8.25 4.5a3.75 3.75 0 1 1 7.5 0v4.5a3.75 3.75 0 1 1-7.5 0V4.5Z" />
                <path d="M6 10.5a.75.75 0 0 1 .75.75v1.5a5.25 5.25 0 1 0 10.5 0v-1.5a.75.75 0 0 1 1.5 0v1.5A6.75 6.75 0 0 1 12.75 20v1.25h3a.75.75 0 0 1 0 1.5h-7.5a.75.75 0 0 1 0-1.5h3V20A6.75 6.75 0 0 1 5.25 12.75v-1.5A.75.75 0 0 1 6 10.5Z" />
              </svg>
            </Button>
            {!isListening && (
              <div className="text-xs text-gray-500 text-center">
                Click to start speaking
              </div>
            )}
          </div>
        ) : (
          // Text Mode: Show input field and send button
          <form onSubmit={handleSubmit} className="flex gap-2">
            <Input
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={disabled ? "Assessment complete" : "Describe your symptoms..."}
              disabled={disabled || isLoading}
              className="flex-1"
            />
            <Button type="submit" disabled={!input.trim() || disabled || isLoading} size="icon">
              <Send className="h-4 w-4" />
            </Button>
          </form>
        )}
      </div>
    </div>
  )
}
