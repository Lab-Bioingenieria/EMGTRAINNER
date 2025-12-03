import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react'

type Theme = 'light' | 'dark' | 'system'
interface ThemeProviderProps {
  children: ReactNode
  defaultTheme?: Theme
  storageKey?: string
}

// Context to access theme and setter
const ThemeContext = createContext<{
  theme: Theme
  setTheme: (theme: Theme) => void
}>({
  theme: 'light',
  setTheme: () => {},
})

export function ThemeProvider({
  children,
  defaultTheme = 'light',
  storageKey = 'vite-theme',
}: ThemeProviderProps) {
  const [theme, setThemeState] = useState<Theme>(() => {
    const stored = localStorage.getItem(storageKey)
    if (stored === 'light' || stored === 'dark' || stored === 'system') return stored
    return defaultTheme
  })

  // Keep theme in sync with <html> class and localStorage
  useEffect(() => {
    if (theme === 'system') {
      const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      document.documentElement.classList.toggle('dark', isDark)
    } else {
      document.documentElement.classList.toggle('dark', theme === 'dark')
    }
    localStorage.setItem(storageKey, theme)
  }, [theme, storageKey])

  // Respond to system theme changes
  useEffect(() => {
    if (theme !== 'system') return
    const listener = (e: MediaQueryListEvent) => {
      document.documentElement.classList.toggle('dark', e.matches)
    }
    const query = window.matchMedia('(prefers-color-scheme: dark)')
    query.addEventListener('change', listener)
    return () => query.removeEventListener('change', listener)
  }, [theme])

  const setTheme = (newTheme: Theme) => setThemeState(newTheme)

  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  )
}


export function useTheme() {
  return useContext(ThemeContext)
}

// Así evitas el error de Vite y mantienes tu custom hook utilizable en otros componentes.

