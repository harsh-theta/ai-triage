import type { Metadata } from 'next'
import './globals.css'
import { SiteHeader } from '@/components/site-header'

export const metadata: Metadata = {
  title: 'AI-Powered Intelligent Triage',
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
      <body>
        <SiteHeader />
        {children}
      </body>
    </html>
  )
}
