"use client"

import { useState, useEffect } from "react"
import { useRouter, useParams } from "next/navigation"
import Sidebar from "@/components/sidebar"
import ChatInterface from "@/components/chat-interface"
import SettingsModal from "@/components/settings-modal"
import { handleLogout } from '@/app/api/chat/route'

export default function ChatPage() {
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [settingsOpen, setSettingsOpen] = useState(false)
  const router = useRouter()
  const params = useParams()
  
  // Access the id directly from params
  const chatId = params.id as string

  useEffect(() => {
    // Check if user is logged in
    const userId = localStorage.getItem('userId')
    if (!userId) {
      router.push('/')
    }
  }, [router])

  const handleLogoutClick = () => {
    // Use the centralized logout function
    handleLogout()
    
    // Redirect to login page
    router.push('/')
  }

  return (
    <div className="flex h-screen w-full bg-white dark:bg-slate-950 transition-colors duration-200">
      <Sidebar
        isOpen={sidebarOpen}
        onToggle={() => setSidebarOpen(!sidebarOpen)}
        onChatSelect={() => {}} // Not needed in this context
        onSettingsClick={() => setSettingsOpen(true)}
        selectedChatId={chatId}
      />
      <ChatInterface onMenuClick={() => setSidebarOpen(!sidebarOpen)} chatId={chatId} />
      {settingsOpen && <SettingsModal onClose={() => setSettingsOpen(false)} onLogout={handleLogoutClick} />}
    </div>
  )
}