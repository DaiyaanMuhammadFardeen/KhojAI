"use client"

import { useState, useEffect, useRef } from "react"
import Sidebar from "@/components/sidebar"
import ChatInterface from "@/components/chat-interface"
import SettingsModal from "@/components/settings-modal"
import Signup from "@/components/signup"

export default function Home() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [settingsOpen, setSettingsOpen] = useState(false)
  const [currentChatId, setCurrentChatId] = useState<string | null>(null)
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const sidebarRef = useRef<{ refreshConversations: () => void }>(null)

  useEffect(() => {
    // Check if user is already logged in
    const userId = localStorage.getItem('userId')
    if (userId) {
      setIsLoggedIn(true)
    }
  }, [])

  const handleLogout = () => {
    // Clear user data
    localStorage.removeItem('userId')
    localStorage.removeItem('username')
    localStorage.removeItem('conversations')
    setIsLoggedIn(false)
    setCurrentChatId(null)
  }

  if (!isLoggedIn) {
    return <Signup onLoginSuccess={() => setIsLoggedIn(true)} />
  }

  return (
    <div className="flex h-screen w-full bg-white dark:bg-slate-950 transition-colors duration-200">
      <Sidebar
        isOpen={sidebarOpen}
        onToggle={() => setSidebarOpen(!sidebarOpen)}
        onChatSelect={(chatId) => {
          setCurrentChatId(chatId)
          // Close sidebar on mobile after selecting a chat
          if (window.innerWidth < 768) {
            setSidebarOpen(false)
          }
        }}
        onSettingsClick={() => {
          setSettingsOpen(true)
          // Close sidebar on mobile when opening settings
          if (window.innerWidth < 768) {
            setSidebarOpen(false)
          }
        }}
      />
      <ChatInterface 
        onMenuClick={() => setSidebarOpen(!sidebarOpen)} 
        chatId={currentChatId} 
      />
      {settingsOpen && <SettingsModal onClose={() => setSettingsOpen(false)} onLogout={handleLogout} />}
    </div>
  )
}