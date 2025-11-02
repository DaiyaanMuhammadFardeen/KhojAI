"use client"

import type React from "react"
import { useState } from "react"
import { Menu, Plus, Settings, Trash2, MessageSquare } from "lucide-react"

interface SidebarProps {
  isOpen: boolean
  onToggle: () => void
  onChatSelect: (chatId: string) => void
  onSettingsClick: () => void
}

interface ChatItem {
  id: string
  title: string
  timestamp: Date
}

export default function Sidebar({ isOpen, onToggle, onChatSelect, onSettingsClick }: SidebarProps) {
  const [chats, setChats] = useState<ChatItem[]>([
    { id: "1", title: "How to learn React", timestamp: new Date(Date.now() - 86400000) },
    { id: "2", title: "Python best practices", timestamp: new Date(Date.now() - 172800000) },
    { id: "3", title: "Web design tips", timestamp: new Date(Date.now() - 259200000) },
  ])
  const [hoveredChatId, setHoveredChatId] = useState<string | null>(null)

  const handleNewChat = () => {
    onChatSelect("")
  }

  const handleDeleteChat = (id: string, e: React.MouseEvent) => {
    e.stopPropagation()
    setChats(chats.filter((chat) => chat.id !== id))
  }

  const formatTime = (date: Date) => {
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMs / 3600000)
    const diffDays = Math.floor(diffMs / 86400000)

    if (diffMins < 60) return `${diffMins}m ago`
    if (diffHours < 24) return `${diffHours}h ago`
    if (diffDays < 7) return `${diffDays}d ago`
    return date.toLocaleDateString()
  }

  return (
    <>
      <div
        className={`fixed md:relative w-60 h-screen bg-slate-50 dark:bg-slate-900 border-r border-slate-200 dark:border-slate-700 flex flex-col transition-transform duration-200 z-40 ${isOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0"}`}
      >
        <div className="p-4 border-b border-slate-200 dark:border-slate-700">
          <button
            className="w-full flex items-center gap-3 px-4 py-2 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-md text-slate-900 dark:text-slate-100 hover:bg-slate-100 dark:hover:bg-slate-700 hover:border-green-500 transition-all text-sm font-medium"
            onClick={handleNewChat}
          >
            <Plus size={20} />
            <span>New chat</span>
          </button>
        </div>

        <div className="flex-1 overflow-y-auto py-4">
          <div className="px-3 pb-4">
            <h3 className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-3 px-3">
              Today
            </h3>
            {chats.slice(0, 1).map((chat) => (
              <div
                key={chat.id}
                className="flex items-center gap-3 px-3 py-2 mb-1 bg-transparent rounded-md text-slate-900 dark:text-slate-100 cursor-pointer hover:bg-white dark:hover:bg-slate-800 transition-all relative group"
                onMouseEnter={() => setHoveredChatId(chat.id)}
                onMouseLeave={() => setHoveredChatId(null)}
                onClick={() => onChatSelect(chat.id)}
              >
                <MessageSquare size={16} className="flex-shrink-0 text-slate-500 dark:text-slate-400" />
                <span className="flex-1 whitespace-nowrap overflow-hidden text-ellipsis text-sm">{chat.title}</span>
                {hoveredChatId === chat.id && (
                  <button
                    className="text-slate-500 dark:text-slate-400 hover:text-red-500 transition-colors"
                    onClick={(e) => handleDeleteChat(chat.id, e)}
                  >
                    <Trash2 size={16} />
                  </button>
                )}
              </div>
            ))}
          </div>

          <div className="px-3">
            <h3 className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-3 px-3">
              Previous 7 days
            </h3>
            {chats.slice(1).map((chat) => (
              <div
                key={chat.id}
                className="flex items-center gap-3 px-3 py-2 mb-1 bg-transparent rounded-md text-slate-900 dark:text-slate-100 cursor-pointer hover:bg-white dark:hover:bg-slate-800 transition-all relative group"
                onMouseEnter={() => setHoveredChatId(chat.id)}
                onMouseLeave={() => setHoveredChatId(null)}
                onClick={() => onChatSelect(chat.id)}
              >
                <MessageSquare size={16} className="flex-shrink-0 text-slate-500 dark:text-slate-400" />
                <span className="flex-1 whitespace-nowrap overflow-hidden text-ellipsis text-sm">{chat.title}</span>
                {hoveredChatId === chat.id && (
                  <button
                    className="text-slate-500 dark:text-slate-400 hover:text-red-500 transition-colors"
                    onClick={(e) => handleDeleteChat(chat.id, e)}
                  >
                    <Trash2 size={16} />
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>

        <div className="p-4 border-t border-slate-200 dark:border-slate-700">
          <button
            className="w-full flex items-center gap-3 px-4 py-2 bg-transparent border border-slate-200 dark:border-slate-700 rounded-md text-slate-900 dark:text-slate-100 hover:bg-white dark:hover:bg-slate-800 hover:border-green-500 transition-all text-sm font-medium"
            onClick={onSettingsClick}
          >
            <Settings size={20} />
            <span>Settings</span>
          </button>
        </div>
      </div>

      <button
        className="hidden md:hidden fixed bottom-4 left-4 w-12 h-12 bg-green-600 hover:bg-green-700 border-none rounded-md text-white cursor-pointer z-30 flex items-center justify-center transition-transform hover:scale-105"
        onClick={onToggle}
      >
        <Menu size={24} />
      </button>
    </>
  )
}
