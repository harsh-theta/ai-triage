"use client"

import { Button } from "@/components/ui/button"
import { AlertTriangle, Phone, RotateCcw } from "lucide-react"

interface EmergencyAlertProps {
  onReset: () => void
}

export function EmergencyAlert({ onReset }: EmergencyAlertProps) {
  return (
    <div className="fixed inset-0 bg-red-600/95 backdrop-blur-sm flex items-center justify-center z-50 p-6">
      <div className="bg-white p-10 max-w-lg w-full text-center shadow-2xl border-4 border-red-200">
        <div className="flex justify-center mb-6">
          <div className="w-20 h-20 bg-red-100 rounded-full flex items-center justify-center animate-pulse">
            <AlertTriangle className="h-12 w-12 text-red-600" />
          </div>
        </div>

        <h1 className="text-3xl font-bold text-red-600 mb-2">EMERGENCY DETECTED</h1>
        <div className="w-16 h-1 bg-red-600 mx-auto mb-6 rounded-full"></div>

        <p className="text-gray-700 text-lg mb-8 leading-relaxed">
          Based on the symptoms described, this appears to be a medical emergency. 
          <strong className="text-red-600"> Please seek immediate medical attention.</strong>
        </p>

        <div className="space-y-6">
          <Button
            className="w-full bg-red-600 hover:bg-red-700 text-white text-xl py-4 shadow-lg hover:shadow-xl transition-all duration-200"
            onClick={() => window.open("tel:911")}
          >
            <Phone className="h-6 w-6 mr-3" />
            Call 911 Now
          </Button>

          <div className="bg-gray-50 p-6 text-left border border-gray-200">
            <p className="font-bold text-gray-900 mb-4 text-center">Immediate Actions Required:</p>
            <ul className="space-y-2 text-gray-700">
              <li className="flex items-start gap-3">
                <span className="w-2 h-2 bg-red-500 rounded-full mt-2 flex-shrink-0"></span>
                <span>Call emergency services immediately</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="w-2 h-2 bg-red-500 rounded-full mt-2 flex-shrink-0"></span>
                <span>Stay calm and follow dispatcher instructions</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="w-2 h-2 bg-red-500 rounded-full mt-2 flex-shrink-0"></span>
                <span>Do not drive yourself to the hospital</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="w-2 h-2 bg-red-500 rounded-full mt-2 flex-shrink-0"></span>
                <span>Have someone stay with you if possible</span>
              </li>
            </ul>
          </div>

          <Button 
            variant="outline" 
            onClick={onReset} 
            className="w-full border-gray-300 text-gray-700 hover:bg-gray-50 py-3 flex items-center gap-2"
          >
            <RotateCcw className="h-4 w-4" />
            Start New Triage Session
          </Button>
        </div>
      </div>
    </div>
  )
}
