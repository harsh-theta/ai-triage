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
  const [isListening, setIsListening] = useState(false)
  const recognitionRef = useRef<any>(null)

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  // TTS: Speak assistant messages when they arrive and voiceMode is on
  useEffect(() => {
    if (!voiceMode) return
    if (messages.length === 0) return
    const lastMsg = messages[messages.length - 1]
    if (lastMsg.role === "assistant" && lastMsg.content) {
      // Cancel any ongoing speech
      window.speechSynthesis.cancel()
      const utter = new window.SpeechSynthesisUtterance(lastMsg.content)
      utter.rate = 1
      utter.pitch = 1
      window.speechSynthesis.speak(utter)
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
        <form onSubmit={handleSubmit} className="flex gap-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={disabled ? "Chat disabled" : "Describe your symptoms..."}
            disabled={disabled || isLoading}
            className="flex-1"
          />
         {voiceMode && (
           <Button
             type="button"
             onClick={handleMicClick}
             disabled={disabled || isLoading}
             variant={isListening ? "secondary" : "outline"}
             size="icon"
             aria-label={isListening ? "Stop listening" : "Start listening"}
           >
             <svg
               xmlns="http://www.w3.org/2000/svg"
               fill={isListening ? "#2563eb" : "none"}
               viewBox="0 0 24 24"
               strokeWidth={1.5}
               stroke="currentColor"
               className="h-5 w-5"
             >
               <path
                 strokeLinecap="round"
                 strokeLinejoin="round"
                 d="M12 18.75v1.5m0 0h3.75m-3.75 0H8.25m7.5-7.5a3.75 3.75 0 10-7.5 0v2.25a3.75 3.75 0 007.5 0V12z"
               />
             </svg>
           </Button>
         )}
          <Button type="submit" disabled={!input.trim() || disabled || isLoading} size="icon">
            <Send className="h-4 w-4" />
          </Button>
        </form>
      </div>
    </div>
  )
}
