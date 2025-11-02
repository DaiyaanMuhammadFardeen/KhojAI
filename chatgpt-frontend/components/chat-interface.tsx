"use client"

import { useState, useRef, useEffect } from "react"
import ChatMessage from "./chat-message"
import PromptBar from "./prompt-bar"
import { Menu } from "lucide-react"

interface Message {
  id: string
  role: "user" | "assistant"
  content: string
  timestamp: Date
}

interface ChatInterfaceProps {
  onMenuClick: () => void
  chatId: string | null
}

export default function ChatInterface({ onMenuClick, chatId }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      role: "assistant",
      content: `# Welcome to ChatBot

I'm your AI assistant. I can help you with:
- **Answering questions** on a wide range of topics
- **Writing and editing** content
- **Coding assistance** and debugging
- **Creative brainstorming** and ideation
- **Learning and explanations** of complex concepts

Feel free to ask me anything! Start by typing your question or prompt below.`,
      timestamp: new Date(),
    },
  ])
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = async (content: string) => {
    if (!content.trim()) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setIsLoading(true)

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: content }),
      })

      if (!response.ok) {
        throw new Error("Failed to get response")
      }

      const data = await response.json()

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: data.response,
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, assistantMessage])
    } catch (error) {
      console.error("Error sending message:", error)
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: "Sorry, I encountered an error processing your request. Please try again.",
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex-1 flex flex-col h-screen bg-white dark:bg-slate-950 transition-colors duration-200">
      <div className="flex items-center justify-between px-6 py-4 md:px-4 border-b border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-950">
        <button
          className="hidden md:flex items-center justify-center text-slate-900 dark:text-slate-100 cursor-pointer p-2 hover:text-green-600 transition-colors"
          onClick={onMenuClick}
        >
          <Menu size={24} />
        </button>
        <h1 className="text-lg md:text-base font-semibold text-slate-900 dark:text-slate-100">ChatBot</h1>
        <div className="w-10" />
      </div>

      <div className="flex-1 overflow-y-auto px-6 md:px-4 py-6 md:py-4 flex flex-col gap-6">
        {messages.map((message) => (
          <ChatMessage key={message.id} message={message} />
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
