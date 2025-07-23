import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'AI Triage System',
  description: 'AI-powered medical triage and EMR capture',
  generator: 'ai-triage',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
