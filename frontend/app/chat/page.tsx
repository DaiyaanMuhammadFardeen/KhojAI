"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import Sidebar from "@/components/sidebar"
import ChatInterface from "@/components/chat-interface"
import SettingsModal from "@/components/settings-modal"

export default function ChatPage() {
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [settingsOpen, setSettingsOpen] = useState(false)
  const [currentChatId, setCurrentChatId] = useState<string | null>(null)
  const router = useRouter()

  useEffect(() => {
    // Check if user is logged in
    const userId = localStorage.getItem('userId')
    if (!userId) {
      router.push('/')
    }
  }, [router])

  return (
    <div className="flex h-screen w-full bg-white dark:bg-slate-950 transition-colors duration-200">
      <Sidebar
        isOpen={sidebarOpen}
        onToggle={() => setSidebarOpen(!sidebarOpen)}
        onChatSelect={setCurrentChatId}
        onSettingsClick={() => setSettingsOpen(true)}
      />
      <ChatInterface onMenuClick={() => setSidebarOpen(!sidebarOpen)} chatId={currentChatId} />
      {settingsOpen && <SettingsModal onClose={() => setSettingsOpen(false)} />}
    </div>
  )
}