'use client'

import React from 'react'
import { Button } from '@/components/ui/button'
import { Switch } from '@/components/ui/switch'
import { Mic, RotateCcw } from 'lucide-react'
import { ThetaLogo } from './theta-logo'
import { JSX } from 'react/jsx-runtime'

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
    <header className="fixed top-0 left-0 right-0 z-50 bg-gradient-to-r from-[hsl(var(--theta-teal))] to-[hsl(var(--theta-cyan))] shadow-sm">
      <div className="max-w-7xl mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          {/* Logo and Title */}
          <div className="flex items-center gap-4">
            <div className="flex items-center">
              <img
                src="https://demo.thetatechnolabs.com/assets/Theta%20Logo_1753431895879-M-ygvsIZ.png"
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
              <h1 className="text-xl font-semibold text-white">AI-Powered Intelligent Triage</h1>
              <p className="text-sm text-white/90">Real-time medical assessment and EMR generation</p>
            </div>
          </div>



          {/* Controls */}
          <div className="flex items-center gap-4">
            {/* Voice Mode Toggle */}
            <div className="flex items-center gap-3 bg-white/20 backdrop-blur-sm rounded-lg px-4 py-2 border border-white/30">
              <Mic className="h-4 w-4 text-white" />
              <span className="text-sm font-medium text-white">Voice Mode</span>
              <Switch
                checked={voiceMode}
                onCheckedChange={handleVoiceModeChange}
                className="data-[state=checked]:bg-white"
              />
            </div>

            {/* New Session Button */}
            <Button
              onClick={handleNewSession}
              variant="outline"
              className="flex items-center gap-2 border-white/30 text-white hover:bg-white/20 hover:text-white transition-colors bg-white/10"
            >
              <RotateCcw className="h-4 w-4" />
              New Session
            </Button>

            {/* Contact Us Button */}
            <Button className="bg-white/20 hover:bg-white/30 text-white px-6 border border-white/30">
              Contact Us
            </Button>
          </div>
        </div>
      </div>
    </header>
  )
}


