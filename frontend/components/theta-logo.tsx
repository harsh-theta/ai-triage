import React from 'react'

interface ThetaLogoProps {
  className?: string
}

export function ThetaLogo({ className = "h-10 w-auto" }: ThetaLogoProps) {
  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <svg
        viewBox="0 0 40 40"
        className="h-10 w-10"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <defs>
          <linearGradient id="thetaGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="hsl(174, 72%, 56%)" />
            <stop offset="50%" stopColor="hsl(186, 100%, 50%)" />
            <stop offset="100%" stopColor="hsl(195, 100%, 50%)" />
          </linearGradient>
        </defs>
        <circle cx="20" cy="20" r="18" fill="url(#thetaGradient)" />
        <text
          x="20"
          y="28"
          textAnchor="middle"
          className="fill-white font-bold text-xl"
          style={{ fontFamily: 'serif' }}
        >
          Θ
        </text>
      </svg>
      <div className="flex flex-col">
        <span className="text-lg font-bold text-gray-900">Theta</span>
        <span className="text-sm text-gray-600 -mt-1">Technolabs</span>
      </div>
    </div>
  )
}