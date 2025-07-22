"use client"

import { Button } from "@/components/ui/button"
import { AlertTriangle, Phone } from "lucide-react"

interface EmergencyAlertProps {
  onReset: () => void
}

export function EmergencyAlert({ onReset }: EmergencyAlertProps) {
  return (
    <div className="fixed inset-0 bg-red-600 bg-opacity-95 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg p-8 max-w-md w-full text-center shadow-2xl">
        <div className="flex justify-center mb-4">
          <AlertTriangle className="h-16 w-16 text-red-600" />
        </div>

        <h1 className="text-2xl font-bold text-red-600 mb-4">EMERGENCY DETECTED</h1>

        <p className="text-gray-700 mb-6">
          Based on the symptoms described, this appears to be a medical emergency. Please seek immediate medical
          attention.
        </p>

        <div className="space-y-4">
          <Button
            className="w-full bg-red-600 hover:bg-red-700 text-white text-lg py-3"
            onClick={() => window.open("tel:911")}
          >
            <Phone className="h-5 w-5 mr-2" />
            Call 911 Now
          </Button>

          <div className="text-sm text-gray-600">
            <p className="font-semibold mb-2">Immediate Actions:</p>
            <ul className="text-left space-y-1">
              <li>• Call emergency services immediately</li>
              <li>• Stay calm and follow dispatcher instructions</li>
              <li>• Do not drive yourself to the hospital</li>
              <li>• Have someone stay with you if possible</li>
            </ul>
          </div>

          <Button variant="outline" onClick={onReset} className="w-full mt-4 bg-transparent">
            Start New Triage Session
          </Button>
        </div>
      </div>
    </div>
  )
}
