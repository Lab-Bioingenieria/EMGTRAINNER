import type { ReactNode } from 'react'

interface HomeLayoutProps {
  children: ReactNode
}

export function HomeLayout({ children }: HomeLayoutProps) {
  return (
    <div className="min-h-screen bg-background font-sans antialiased">
      {children}
    </div>
  )
}