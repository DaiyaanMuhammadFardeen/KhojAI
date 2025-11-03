"use client"

import type React from "react"
import { useState, useEffect } from "react"
import { Menu, Plus, Settings, Trash2, MessageSquare, X, Edit3, Check, XCircle } from "lucide-react"
import { ConversationAPI } from '@/app/api/chat/route'

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
  const [chats, setChats] = useState<ChatItem[]>([])
  const [hoveredChatId, setHoveredChatId] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [editingChatId, setEditingChatId] = useState<string | null>(null)
  const [editTitle, setEditTitle] = useState("")

  // Load conversations from backend
  useEffect(() => {
    const loadConversations = async () => {
      try {
        setLoading(true)
        const userId = localStorage.getItem('userId')
        if (!userId) {
          console.error("No user ID found")
          setLoading(false)
          return
        }

        const response = await ConversationAPI.getByUser(userId)
        const formattedChats = response.data.map(chat => ({
          id: chat.id,
          title: chat.title,
          timestamp: new Date(chat.createdAt)
        }))
        setChats(formattedChats)
        setLoading(false)
      } catch (error) {
        console.error("Failed to load conversations:", error)
        setLoading(false)
      }
    }

    loadConversations()
  }, [])

  // Listen for conversation creation events
  useEffect(() => {
    const handleConversationCreated = () => {
      refreshConversations()
    }

    window.addEventListener('conversationCreated', handleConversationCreated)
    return () => {
      window.removeEventListener('conversationCreated', handleConversationCreated)
    }
  }, [])

  // Function to refresh conversations
  const refreshConversations = async () => {
    try {
      const userId = localStorage.getItem('userId')
      if (!userId) {
        console.error("No user ID found")
        return
      }

      const response = await ConversationAPI.getByUser(userId)
      const formattedChats = response.data.map(chat => ({
        id: chat.id,
        title: chat.title,
        timestamp: new Date(chat.createdAt)
      }))
      setChats(formattedChats)
    } catch (error) {
      console.error("Failed to refresh conversations:", error)
    }
  }

  const handleNewChat = async () => {
    try {
      const userId = localStorage.getItem('userId')
      if (!userId) {
        console.error("No user ID found")
        return
      }

      const response = await ConversationAPI.create({
        userId: userId,
        title: "New Chat"
      })

      const newChat: ChatItem = {
        id: response.data.id,
        title: response.data.title,
        timestamp: new Date(response.data.createdAt)
      }

      setChats(prev => [newChat, ...prev])
      onChatSelect(newChat.id)
    } catch (error) {
      console.error("Error creating new conversation:", error)
    }
  }

  const handleDeleteChat = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation()
    try {
      await ConversationAPI.delete(id)
      setChats(chats.filter((chat) => chat.id !== id))
    } catch (error) {
      console.error("Error deleting conversation:", error)
    }
  }

  const startEditing = (chatId: string, currentTitle: string, e: React.MouseEvent) => {
    e.stopPropagation()
    setEditingChatId(chatId)
    setEditTitle(currentTitle)
  }

  const cancelEditing = (e: React.MouseEvent) => {
    e.stopPropagation()
    setEditingChatId(null)
    setEditTitle("")
  }

  const saveEditing = async (chatId: string, e: React.MouseEvent) => {
    e.stopPropagation()
    if (!editTitle.trim()) return

    try {
      await ConversationAPI.updateTitle(chatId, editTitle.trim())
      setChats(chats.map(chat => 
        chat.id === chatId ? { ...chat, title: editTitle.trim() } : chat
      ))
      setEditingChatId(null)
      setEditTitle("")
    } catch (error) {
      console.error("Error updating conversation title:", error)
    }
  }

  const handleEditKeyDown = (chatId: string, e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      saveEditing(chatId, e as any)
    } else if (e.key === 'Escape') {
      cancelEditing(e as any)
    }
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

  // Group chats by date (Today, Yesterday, and Previous 3 days)
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  
  const yesterday = new Date(today)
  yesterday.setDate(yesterday.getDate() - 1)
  
  const threeDaysAgo = new Date(today)
  threeDaysAgo.setDate(threeDaysAgo.getDate() - 3)

  const todayChats = chats.filter(chat => {
    const chatDate = new Date(chat.timestamp)
    chatDate.setHours(0, 0, 0, 0)
    return chatDate.getTime() === today.getTime()
  })

  const yesterdayChats = chats.filter(chat => {
    const chatDate = new Date(chat.timestamp)
    chatDate.setHours(0, 0, 0, 0)
    return chatDate.getTime() === yesterday.getTime()
  })

  const previousChats = chats.filter(chat => {
    const chatDate = new Date(chat.timestamp)
    chatDate.setHours(0, 0, 0, 0)
    return chatDate < yesterday && chatDate >= threeDaysAgo
  })

  const olderChats = chats.filter(chat => {
    const chatDate = new Date(chat.timestamp)
    chatDate.setHours(0, 0, 0, 0)
    return chatDate < threeDaysAgo
  })

  return (
    <>
      <div
        className={`fixed md:relative w-60 h-screen bg-slate-50 dark:bg-slate-900 border-r border-slate-200 dark:border-slate-700 flex flex-col transition-transform duration-200 z-40 ${isOpen ? "translate-x-0" : "-translate-x-full"} md:translate-x-0`}
      >
        <div className="p-4 border-b border-slate-200 dark:border-slate-700 flex items-center justify-between">
          <button
            className="flex md:hidden items-center justify-center text-slate-900 dark:text-slate-100 cursor-pointer p-2 hover:text-green-600 transition-colors"
            onClick={onToggle}
          >
            <X size={20} />
          </button>
          <button
            className="hidden md:flex items-center justify-center text-slate-900 dark:text-slate-100 cursor-pointer p-2 hover:text-green-600 transition-colors"
            onClick={onToggle}
          >
            <X size={20} />
          </button>
          <button
            className="flex items-center gap-3 px-3 py-2 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-md text-slate-900 dark:text-slate-100 hover:bg-slate-100 dark:hover:bg-slate-700 hover:border-green-500 transition-all text-sm font-medium"
            onClick={handleNewChat}
            disabled={loading}
          >
            <Plus size={16} />
            <span>New chat</span>
          </button>
        </div>

        <div className="flex-1 overflow-y-auto py-4">
          {todayChats.length > 0 && (
            <div className="px-3 pb-4">
              <h3 className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-3 px-3">
                Today
              </h3>
              {todayChats.map((chat) => (
                <div
                  key={chat.id}
                  className="flex items-center gap-3 px-3 py-2 mb-1 bg-transparent rounded-md text-slate-900 dark:text-slate-100 cursor-pointer hover:bg-white dark:hover:bg-slate-800 transition-all relative group"
                  onMouseEnter={() => setHoveredChatId(chat.id)}
                  onMouseLeave={() => setHoveredChatId(null)}
                  onClick={() => onChatSelect(chat.id)}
                >
                  {editingChatId === chat.id ? (
                    <div className="flex items-center gap-2 flex-1" onClick={(e) => e.stopPropagation()}>
                      <MessageSquare size={16} className="flex-shrink-0 text-slate-500 dark:text-slate-400" />
                      <input
                        type="text"
                        value={editTitle}
                        onChange={(e) => setEditTitle(e.target.value)}
                        onKeyDown={(e) => handleEditKeyDown(chat.id, e)}
                        className="flex-1 bg-white dark:bg-slate-700 border border-slate-300 dark:border-slate-600 rounded px-2 py-1 text-sm"
                        autoFocus
                      />
                      <button 
                        className="text-green-600 hover:text-green-700"
                        onClick={(e) => saveEditing(chat.id, e)}
                      >
                        <Check size={16} />
                      </button>
                      <button 
                        className="text-red-600 hover:text-red-700"
                        onClick={cancelEditing}
                      >
                        <XCircle size={16} />
                      </button>
                    </div>
                  ) : (
                    <>
                      <MessageSquare size={16} className="flex-shrink-0 text-slate-500 dark:text-slate-400" />
                      <span className="flex-1 whitespace-nowrap overflow-hidden text-ellipsis text-sm">{chat.title}</span>
                      {hoveredChatId === chat.id && (
                        <div className="flex gap-1">
                          <button
                            className="text-slate-500 dark:text-slate-400 hover:text-blue-500 transition-colors"
                            onClick={(e) => startEditing(chat.id, chat.title, e)}
                          >
                            <Edit3 size={16} />
                          </button>
                          <button
                            className="text-slate-500 dark:text-slate-400 hover:text-red-500 transition-colors"
                            onClick={(e) => handleDeleteChat(chat.id, e)}
                          >
                            <Trash2 size={16} />
                          </button>
                        </div>
                      )}
                    </>
                  )}
                </div>
              ))}
            </div>
          )}

          {yesterdayChats.length > 0 && (
            <div className="px-3 pb-4">
              <h3 className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-3 px-3">
                Yesterday
              </h3>
              {yesterdayChats.map((chat) => (
                <div
                  key={chat.id}
                  className="flex items-center gap-3 px-3 py-2 mb-1 bg-transparent rounded-md text-slate-900 dark:text-slate-100 cursor-pointer hover:bg-white dark:hover:bg-slate-800 transition-all relative group"
                  onMouseEnter={() => setHoveredChatId(chat.id)}
                  onMouseLeave={() => setHoveredChatId(null)}
                  onClick={() => onChatSelect(chat.id)}
                >
                  {editingChatId === chat.id ? (
                    <div className="flex items-center gap-2 flex-1" onClick={(e) => e.stopPropagation()}>
                      <MessageSquare size={16} className="flex-shrink-0 text-slate-500 dark:text-slate-400" />
                      <input
                        type="text"
                        value={editTitle}
                        onChange={(e) => setEditTitle(e.target.value)}
                        onKeyDown={(e) => handleEditKeyDown(chat.id, e)}
                        className="flex-1 bg-white dark:bg-slate-700 border border-slate-300 dark:border-slate-600 rounded px-2 py-1 text-sm"
                        autoFocus
                      />
                      <button 
                        className="text-green-600 hover:text-green-700"
                        onClick={(e) => saveEditing(chat.id, e)}
                      >
                        <Check size={16} />
                      </button>
                      <button 
                        className="text-red-600 hover:text-red-700"
                        onClick={cancelEditing}
                      >
                        <XCircle size={16} />
                      </button>
                    </div>
                  ) : (
                    <>
                      <MessageSquare size={16} className="flex-shrink-0 text-slate-500 dark:text-slate-400" />
                      <span className="flex-1 whitespace-nowrap overflow-hidden text-ellipsis text-sm">{chat.title}</span>
                      {hoveredChatId === chat.id && (
                        <div className="flex gap-1">
                          <button
                            className="text-slate-500 dark:text-slate-400 hover:text-blue-500 transition-colors"
                            onClick={(e) => startEditing(chat.id, chat.title, e)}
                          >
                            <Edit3 size={16} />
                          </button>
                          <button
                            className="text-slate-500 dark:text-slate-400 hover:text-red-500 transition-colors"
                            onClick={(e) => handleDeleteChat(chat.id, e)}
                          >
                            <Trash2 size={16} />
                          </button>
                        </div>
                      )}
                    </>
                  )}
                </div>
              ))}
            </div>
          )}

          {previousChats.length > 0 && (
            <div className="px-3 pb-4">
              <h3 className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-3 px-3">
                Previous 3 days
              </h3>
              {previousChats.map((chat) => (
                <div
                  key={chat.id}
                  className="flex items-center gap-3 px-3 py-2 mb-1 bg-transparent rounded-md text-slate-900 dark:text-slate-100 cursor-pointer hover:bg-white dark:hover:bg-slate-800 transition-all relative group"
                  onMouseEnter={() => setHoveredChatId(chat.id)}
                  onMouseLeave={() => setHoveredChatId(null)}
                  onClick={() => onChatSelect(chat.id)}
                >
                  {editingChatId === chat.id ? (
                    <div className="flex items-center gap-2 flex-1" onClick={(e) => e.stopPropagation()}>
                      <MessageSquare size={16} className="flex-shrink-0 text-slate-500 dark:text-slate-400" />
                      <input
                        type="text"
                        value={editTitle}
                        onChange={(e) => setEditTitle(e.target.value)}
                        onKeyDown={(e) => handleEditKeyDown(chat.id, e)}
                        className="flex-1 bg-white dark:bg-slate-700 border border-slate-300 dark:border-slate-600 rounded px-2 py-1 text-sm"
                        autoFocus
                      />
                      <button 
                        className="text-green-600 hover:text-green-700"
                        onClick={(e) => saveEditing(chat.id, e)}
                      >
                        <Check size={16} />
                      </button>
                      <button 
                        className="text-red-600 hover:text-red-700"
                        onClick={cancelEditing}
                      >
                        <XCircle size={16} />
                      </button>
                    </div>
                  ) : (
                    <>
                      <MessageSquare size={16} className="flex-shrink-0 text-slate-500 dark:text-slate-400" />
                      <span className="flex-1 whitespace-nowrap overflow-hidden text-ellipsis text-sm">{chat.title}</span>
                      {hoveredChatId === chat.id && (
                        <div className="flex gap-1">
                          <button
                            className="text-slate-500 dark:text-slate-400 hover:text-blue-500 transition-colors"
                            onClick={(e) => startEditing(chat.id, chat.title, e)}
                          >
                            <Edit3 size={16} />
                          </button>
                          <button
                            className="text-slate-500 dark:text-slate-400 hover:text-red-500 transition-colors"
                            onClick={(e) => handleDeleteChat(chat.id, e)}
                          >
                            <Trash2 size={16} />
                          </button>
                        </div>
                      )}
                    </>
                  )}
                </div>
              ))}
            </div>
          )}

          {olderChats.length > 0 && (
            <div className="px-3">
              <h3 className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-3 px-3">
                Older
              </h3>
              {olderChats.map((chat) => (
                <div
                  key={chat.id}
                  className="flex items-center gap-3 px-3 py-2 mb-1 bg-transparent rounded-md text-slate-900 dark:text-slate-100 cursor-pointer hover:bg-white dark:hover:bg-slate-800 transition-all relative group"
                  onMouseEnter={() => setHoveredChatId(chat.id)}
                  onMouseLeave={() => setHoveredChatId(null)}
                  onClick={() => onChatSelect(chat.id)}
                >
                  {editingChatId === chat.id ? (
                    <div className="flex items-center gap-2 flex-1" onClick={(e) => e.stopPropagation()}>
                      <MessageSquare size={16} className="flex-shrink-0 text-slate-500 dark:text-slate-400" />
                      <input
                        type="text"
                        value={editTitle}
                        onChange={(e) => setEditTitle(e.target.value)}
                        onKeyDown={(e) => handleEditKeyDown(chat.id, e)}
                        className="flex-1 bg-white dark:bg-slate-700 border border-slate-300 dark:border-slate-600 rounded px-2 py-1 text-sm"
                        autoFocus
                      />
                      <button 
                        className="text-green-600 hover:text-green-700"
                        onClick={(e) => saveEditing(chat.id, e)}
                      >
                        <Check size={16} />
                      </button>
                      <button 
                        className="text-red-600 hover:text-red-700"
                        onClick={cancelEditing}
                      >
                        <XCircle size={16} />
                      </button>
                    </div>
                  ) : (
                    <>
                      <MessageSquare size={16} className="flex-shrink-0 text-slate-500 dark:text-slate-400" />
                      <span className="flex-1 whitespace-nowrap overflow-hidden text-ellipsis text-sm">{chat.title}</span>
                      {hoveredChatId === chat.id && (
                        <div className="flex gap-1">
                          <button
                            className="text-slate-500 dark:text-slate-400 hover:text-blue-500 transition-colors"
                            onClick={(e) => startEditing(chat.id, chat.title, e)}
                          >
                            <Edit3 size={16} />
                          </button>
                          <button
                            className="text-slate-500 dark:text-slate-400 hover:text-red-500 transition-colors"
                            onClick={(e) => handleDeleteChat(chat.id, e)}
                          >
                            <Trash2 size={16} />
                          </button>
                        </div>
                      )}
                    </>
                  )}
                </div>
              ))}
            </div>
          )}
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
        className="md:hidden fixed bottom-4 left-4 w-12 h-12 bg-green-600 hover:bg-green-700 border-none rounded-md text-white cursor-pointer z-30 flex items-center justify-center transition-transform hover:scale-105"
        onClick={onToggle}
      >
        <Menu size={24} />
      </button>
    </>
  )
}