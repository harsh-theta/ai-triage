'use client'

import React from 'react'
import { Button } from '@/components/ui/button'
import { Switch } from '@/components/ui/switch'
import { Mic, RotateCcw } from 'lucide-react'
import { ThetaLogo } from './theta-logo'

export function SiteHeader(): JSX.Element {
  const [voiceMode, setVoiceMode] = React.useState(false)

  const handleVoiceModeChange = (checked: boolean) => {
    setVoiceMode(checked)
    window.dispatchEvent(new CustomEvent('ui:voice-mode', { detail: { checked } }))
  }

  const handleNewSession = () => {
    window.dispatchEvent(new CustomEvent('ui:new-session'))
  }

  return (
    <header className="sticky top-0 z-50 bg-white border-b border-gray-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          {/* Logo and Title */}
          <div className="flex items-center gap-4">
            <div className="flex items-center">
              <img 
                src="/assets/theta-logo.png" 
                alt="Theta Technolabs" 
                className="h-10 w-auto object-contain"
                onError={(e) => {
                  // Hide the image and show fallback
                  e.currentTarget.style.display = 'none'
                  const fallback = e.currentTarget.nextElementSibling as HTMLElement
                  if (fallback) fallback.style.display = 'flex'
                }}
              />
              <div className="hidden">
                <ThetaLogo />
              </div>
            </div>
            <div className="hidden md:block">
              <h1 className="text-xl font-semibold text-gray-900">AI-Powered Intelligent Triage</h1>
              <p className="text-sm text-gray-600">Real-time medical assessment and EMR generation</p>
            </div>
          </div>



          {/* Controls */}
          <div className="flex items-center gap-4">
            {/* Voice Mode Toggle */}
            <div className="flex items-center gap-3 bg-gray-50 rounded-lg px-4 py-2 border">
              <Mic className="h-4 w-4 text-gray-600" />
              <span className="text-sm font-medium text-gray-700">Voice Mode</span>
              <Switch
                checked={voiceMode}
                onCheckedChange={handleVoiceModeChange}
                className="data-[state=checked]:bg-[hsl(var(--theta-teal))]"
              />
            </div>

            {/* New Session Button */}
            <Button
              onClick={handleNewSession}
              variant="outline"
              className="flex items-center gap-2 border-[hsl(var(--theta-teal))] text-[hsl(var(--theta-teal))] hover:bg-[hsl(var(--theta-teal))] hover:text-white transition-colors"
            >
              <RotateCcw className="h-4 w-4" />
              New Session
            </Button>

            {/* Contact Us Button */}
            <Button className="bg-gray-900 hover:bg-gray-800 text-white px-6">
              Contact Us
            </Button>
          </div>
        </div>
      </div>
    </header>
  )
}


