"use client"

import { useState, useRef, useEffect } from "react"
import ChatMessage from "./chat-message"
import PromptBar from "./prompt-bar"
import { Menu } from "lucide-react"
import { ConversationAPI, MessageAPI } from '@/app/api/chat/route'

interface Message {
  id: string
  role: "USER" | "AI"
  content: string
  sentAt: string
}

interface Conversation {
  id: string
  title: string
  createdAt: string
  messages: Message[]
}

interface ChatInterfaceProps {
  onMenuClick: () => void
  chatId: string | null
}

export default function ChatInterface({ onMenuClick, chatId }: ChatInterfaceProps) {
  const [conversation, setConversation] = useState<Conversation | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [conversation?.messages])

  // Load conversation when chatId changes
  useEffect(() => {
    const loadConversation = async () => {
      if (!chatId) {
        // No chatId means we start with no conversation
        setConversation(null)
        return;
      } else {
        // Load existing conversation
        try {
          const response = await ConversationAPI.get(chatId)
          setConversation(response.data)
        } catch (error) {
          console.error("Error loading conversation:", error)
        }
      }
    }

    loadConversation()
  }, [chatId])

  // Update conversation title based on first message
  useEffect(() => {
    const updateConversationTitle = async () => {
      if (!conversation || conversation.messages.length === 0) return

      // If this is still titled "New Chat" and we have messages, update the title
      if (conversation.title === "New Chat" && conversation.messages.length > 0) {
        const firstUserMessage = conversation.messages.find(msg => msg.role === "USER")
        if (firstUserMessage) {
          // Get first 5 words of the first message
          const words = firstUserMessage.content.split(' ').slice(0, 5)
          const newTitle = words.join(' ')
          
          try {
            const response = await ConversationAPI.updateTitle(conversation.id, newTitle)
            setConversation(response.data)
          } catch (error) {
            console.error("Error updating conversation title:", error)
          }
        }
      }
    }

    updateConversationTitle()
  }, [conversation?.messages.length, conversation?.id, conversation?.title])

  const handleSendMessage = async (content: string) => {
    if (!content.trim()) return

    setIsLoading(true)

    try {
      // If no conversation exists, create one
      let currentConversation = conversation;
      if (!currentConversation) {
        const userId = localStorage.getItem('userId')
        if (!userId) {
          console.error("No user ID found")
          setIsLoading(false)
          return
        }

        // Create new conversation with the first 5 words of the message as title
        const words = content.split(' ').slice(0, 5)
        const title = words.join(' ')
        
        const convResponse = await ConversationAPI.create({
          userId: userId,
          title: title || "New Chat"
        })

        currentConversation = convResponse.data
        setConversation(currentConversation)
        
        // Dispatch a custom event to notify the sidebar about the new conversation
        window.dispatchEvent(new CustomEvent('conversationCreated', { detail: currentConversation.id }))
      }

      // Send message to the conversation
      const response = await MessageAPI.create({
        convId: currentConversation.id,
        role: "USER",
        content: content
      })

      // Update the conversation with the full response
      setConversation(response.data)
    } catch (error) {
      console.error("Error sending message:", error)
      
      // Add error message to the conversation
      const errorMessage: Message = {
        id: Date.now().toString(),
        role: "AI",
        content: "Sorry, I encountered an error processing your request. Please try again.",
        sentAt: new Date().toISOString()
      }
      
      setConversation(prev => {
        if (!prev) return null
        return {
          ...prev,
          messages: [...prev.messages, errorMessage]
        }
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex-1 flex flex-col h-screen bg-white dark:bg-slate-950 transition-colors duration-200">
      <div className="flex items-center justify-between px-6 py-4 md:px-4 border-b border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-950">
        <button
          className="flex md:hidden items-center justify-center text-slate-900 dark:text-slate-100 cursor-pointer p-2 hover:text-green-600 transition-colors"
          onClick={onMenuClick}
        >
          <Menu size={24} />
        </button>
        <div className="hidden md:flex w-10"></div>
        <h1 className="text-lg md:text-base font-semibold text-slate-900 dark:text-slate-100">
          {conversation?.title || "ChatBot"}
        </h1>
        <div className="w-10" />
      </div>

      <div className="flex-1 overflow-y-auto px-6 md:px-4 py-6 md:py-4 flex flex-col gap-6">
        {conversation?.messages.map((message) => (
          <ChatMessage 
            key={message.id} 
            message={{
              id: message.id,
              role: message.role === "USER" ? "user" : "assistant",
              content: message.content,
              timestamp: new Date(message.sentAt)
            }} 
          />
        ))}
        {isLoading && (
          <div className="flex items-center gap-4 px-6 py-4 bg-slate-100 dark:bg-slate-800 rounded-lg w-fit">
            <div className="w-2 h-2 rounded-full bg-green-600 animate-pulse" />
            <div className="w-2 h-2 rounded-full bg-green-600 animate-pulse" style={{ animationDelay: "0.2s" }} />
            <div className="w-2 h-2 rounded-full bg-green-600 animate-pulse" style={{ animationDelay: "0.4s" }} />
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <PromptBar onSendMessage={handleSendMessage} isLoading={isLoading} />
    </div>
  )
}