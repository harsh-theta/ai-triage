"use client"

import { useState } from "react"
import { ChatInterface } from "@/components/chat-interface"
import { EmrPreview } from "@/components/emr-preview"
import { SystemStatus } from "@/components/system-status"
import { EmergencyAlert } from "@/components/emergency-alert"
import { LoadingIndicator } from "@/components/loading-indicator"
import { ErrorDisplay } from "@/components/error-display"
import { Card } from "@/components/ui/card"
import { generateId } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Switch } from "@/components/ui/switch"

export interface Message {
  id: string
  role: "user" | "assistant"
  content: string
  timestamp: Date
  audio_url?: string
}

export interface EmrData {
  patient_info?: {
    age?: number
    gender?: string
    chief_complaint?: string
  }
  vital_signs?: {
    temperature?: string
    blood_pressure?: string
    heart_rate?: string
    respiratory_rate?: string
  }
  protocol_followed?: string
}

export interface TriageState {
  messages: Message[]
  emr_data: EmrData
  status: "active" | "emergency_detected" | "error" | "complete"
  current_protocol: string
  session_id: string
  is_loading: boolean
  error_message?: string
  medical_summary?: string
}

export default function TriagePage() {
  const [state, setState] = useState<TriageState>({
    messages: [
      {
        id: generateId(),
        role: "assistant",
        content:
          "Hello! I'm your AI triage assistant. Please describe your symptoms or medical concern, and I'll help assess your situation.",
        timestamp: new Date(),
      },
    ],
    emr_data: {},
    status: "active",
    current_protocol: "Initial Assessment",
    session_id: generateId(),
    is_loading: false,
  })
  const [voiceMode, setVoiceMode] = useState(false)

  const sendMessage = async (content: string) => {
    if (state.status === "emergency_detected" || state.status === "error" || state.status === "complete" || state.is_loading) {
      return
    }

    // Add user message
    const userMessage: Message = {
      id: generateId(),
      role: "user",
      content,
      timestamp: new Date(),
    }

    setState((prev) => ({
      ...prev,
      messages: [...prev.messages, userMessage],
      is_loading: true,
    }))

    try {
      // Direct call to backend API - use TTS endpoint if voice mode is enabled
      const basePath = process.env.NEXT_PUBLIC_API_BASE_PATH || "/intelligent-triage"
      const endpoint = voiceMode ? `${basePath}/chat/tts` : `${basePath}/chat`
      
      // Use relative URLs - nginx will proxy to backend
      const response = await fetch(endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: content,
          session_id: state.session_id,
        }),
      })

      if (!response.ok) {
        throw new Error("Failed to get response from triage system")
      }

      const data = await response.json()

      // Simplified EMR data (assessment removed)
      let emr_data = data.emr_data || state.emr_data

      // Add AI response
      const aiMessage: Message = {
        id: generateId(),
        role: "assistant",
        content: data.ai_message, // Backend returns ai_message, not message
        timestamp: new Date(),
        audio_url: data.audio_url, // Include audio URL from TTS microservice
      }

      setState((prev) => ({
        ...prev,
        messages: [...prev.messages, aiMessage],
        emr_data,
        status: data.status || prev.status,
        current_protocol: data.protocol || prev.current_protocol,
        is_loading: false,
        error_message: undefined,
        medical_summary: data.medical_summary || data.updated_report || prev.medical_summary,
      }))
    } catch (error) {
      setState((prev) => ({
        ...prev,
        status: "error",
        error_message: error instanceof Error ? error.message : "An unexpected error occurred",
        is_loading: false,
      }))
    }
  }

  const resetTriage = () => {
    setState({
      messages: [
        {
          id: generateId(),
          role: "assistant",
          content:
            "Hello! I'm your AI triage assistant. Please describe your symptoms or medical concern, and I'll help assess your situation.",
          timestamp: new Date(),
        },
      ],
      emr_data: {},
      status: "active",
      current_protocol: "Initial Assessment",
      session_id: generateId(),
      is_loading: false,
    })
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-7xl mx-auto">
        <header className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">AI Medical Triage System</h1>
            <p className="text-gray-600 mt-2">Intelligent patient assessment and emergency detection</p>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <Switch id="voice-mode" checked={voiceMode} onCheckedChange={setVoiceMode} />
              <label htmlFor="voice-mode" className="text-sm font-medium text-gray-700 select-none">
                Voice Mode
              </label>
            </div>
            <Button onClick={resetTriage} className="ml-4" variant="default">
              New Session
            </Button>
          </div>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Chat Interface */}
          <div className="lg:col-span-2">
            <Card className="h-[600px] flex flex-col">
              <div className="p-4 border-b">
                <SystemStatus protocol={state.current_protocol} status={state.status} />
              </div>

              <div className="flex-1 overflow-hidden">
                <ChatInterface
                  messages={state.messages}
                  onSendMessage={sendMessage}
                  disabled={state.status === "emergency_detected" || state.status === "error" || state.status === "complete"}
                  isLoading={state.is_loading}
                  voiceMode={voiceMode}
                />
              </div>

              {state.is_loading && <LoadingIndicator />}
            </Card>
          </div>

          {/* EMR Preview Panel */}
          <div className="lg:col-span-1">
            <EmrPreview data={state.emr_data} summary={state.medical_summary} />
          </div>
        </div>

        {/* Error Display */}
        {state.status === "error" && (
          <ErrorDisplay message={state.error_message || "An error occurred"} onRetry={resetTriage} />
        )}

        {/* Final EMR Dictionary (Raw) - Automatically shown when complete */}
        {state.status === "complete" && (
          <div className="max-w-3xl mx-auto mt-8">
            <Card className="p-4">
              <h2 className="text-xl font-bold mb-2">Final EMR Dictionary</h2>
              <pre className="bg-gray-100 rounded p-4 overflow-x-auto text-sm">
                {JSON.stringify(state.emr_data, null, 2)}
              </pre>
            </Card>
          </div>
        )}
      </div>

      {/* Emergency Alert Modal */}
      {state.status === "emergency_detected" && <EmergencyAlert onReset={resetTriage} />}
    </div>
  )
}
