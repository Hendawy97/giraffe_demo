import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Giraffe SDK Demo',
  description: 'Demo application showcasing Giraffe SDK integration with Next.js',
  keywords: ['Giraffe', 'SDK', 'BIM', '3D', '2D', 'CAD', 'Architecture'],
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <head>
        <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🦒</text></svg>" />
      </head>
      <body>{children}</body>
    </html>
  )
}