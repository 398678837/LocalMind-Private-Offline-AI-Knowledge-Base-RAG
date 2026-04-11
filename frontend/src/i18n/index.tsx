
import { useState, useEffect, createContext, useContext } from 'react'
import zhCN from './zh-CN'
import enUS from './en-US'
import jaJP from './ja-JP'
import koKR from './ko-KR'

export type Locale = 'zh-CN' | 'en-US' | 'ja-JP' | 'ko-KR'

export const localeInfo: Record<Locale, { flag: string; name: string }> = {
  'zh-CN': { flag: '🇨🇳', name: '中文' },
  'en-US': { flag: '🇺🇸', name: 'English' },
  'ja-JP': { flag: '🇯🇵', name: '日本語' },
  'ko-KR': { flag: '🇰🇷', name: '한국어' }
}

const translations = {
  'zh-CN': zhCN,
  'en-US': enUS,
  'ja-JP': jaJP,
  'ko-KR': koKR
}

type TranslationKeys = typeof zhCN

interface I18nContextType {
  locale: Locale
  setLocale: (locale: Locale) => void
  t: (key: string) => string
}

const I18nContext = createContext<I18nContextType | undefined>(undefined)

export function I18nProvider({ children }: { children: React.ReactNode }) {
  const [locale, setLocale] = useState<Locale>(() => {
    const saved = localStorage.getItem('locale') as Locale
    return saved || 'zh-CN'
  })

  useEffect(() => {
    localStorage.setItem('locale', locale)
  }, [locale])

  const t = (key: string): string => {
    const keys = key.split('.')
    let value: any = translations[locale]
    
    for (const k of keys) {
      if (value && typeof value === 'object' && k in value) {
        value = value[k]
      } else {
        return key
      }
    }
    
    return typeof value === 'string' ? value : key
  }

  return (
    <I18nContext.Provider value={{ locale, setLocale, t }}>
      {children}
    </I18nContext.Provider>
  )
}

export function useI18n() {
  const context = useContext(I18nContext)
  if (!context) {
    throw new Error('useI18n must be used within an I18nProvider')
  }
  return context
}
