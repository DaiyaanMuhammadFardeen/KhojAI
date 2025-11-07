"use client"

import { useState, useEffect, useRef } from "react"
import { Menu, Send, Plus } from "lucide-react"
import { MessageAPI, AIApi, CreateMessageRequest, ConversationAPI } from '@/app/api/chat/route'
import ChatMessage from "@/components/chat-message"
import styles from '@/styles/components/chat-interface.module.scss'

interface ChatInterfaceProps {
  onMenuClick: () => void
  chatId: string | null
}

interface Message {
  id: string
  role: 'USER' | 'AI'
  content: string
  sentAt: Date
}

export default function ChatInterface({ onMenuClick, chatId }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([])
  const [inputValue, setInputValue] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Load messages when chatId changes
  useEffect(() => {
    if (chatId) {
      loadMessages(chatId)
    } else {
      setMessages([])
    }
  }, [chatId])

  // Scroll to bottom of messages
  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const loadMessages = async (id: string) => {
    try {
      const response = await ConversationAPI.get(id)
      const loadedMessages = response.data.messages.map(msg => ({
        ...msg,
        sentAt: new Date(msg.sentAt)
      }))
      setMessages(loadedMessages)
    } catch (error) {
      console.error("Failed to load messages:", error)
    }
  }

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  const handleSend = async () => {
    if (!inputValue.trim() || !chatId || isLoading) return

    try {
      setIsLoading(true)
      
      // Add user message to UI immediately
      const userMessage: Message = {
        id: Date.now().toString(),
        role: 'USER',
        content: inputValue,
        sentAt: new Date()
      }
      
      setMessages(prev => [...prev, userMessage])
      setInputValue("")

      // Send user message to backend
      const userMessageRequest: CreateMessageRequest = {
        convId: chatId,
        role: 'USER',
        content: inputValue.trim()
      }
      
      const userResponse = await MessageAPI.create(userMessageRequest)
      
      // Update user message with real ID
      setMessages(prev => prev.map(msg => 
        msg.id === userMessage.id 
          ? { ...msg, id: userResponse.data.messages[userResponse.data.messages.length - 2].id } 
          : msg
      ))

      // Get AI response
      const aiResponse = await AIApi.generateResponse({ prompt: inputValue.trim() })
      
      // Add AI message to UI
      const aiMessage: Message = {
        id: Date.now().toString(),
        role: 'AI',
        content: aiResponse.data.message,
        sentAt: new Date()
      }
      
      setMessages(prev => [...prev, aiMessage])
      
      // Send AI message to backend
      const aiMessageRequest: CreateMessageRequest = {
        convId: chatId,
        role: 'AI',
        content: aiResponse.data.message
      }
      
      const aiResponseBackend = await MessageAPI.create(aiMessageRequest)
      
      // Update AI message with real ID
      setMessages(prev => prev.map(msg => 
        msg.id === aiMessage.id 
          ? { ...msg, id: aiResponseBackend.data.messages[aiResponseBackend.data.messages.length - 1].id } 
          : msg
      ))
    } catch (error) {
      console.error("Failed to send message:", error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  if (!chatId) {
    return (
      <div className={styles.emptyChatContainer}>
        <div className={styles.emptyChatContent}>
          <Plus size={48} className={styles.emptyChatIcon} />
          <h2 className={styles.emptyChatTitle}>No Chat Selected</h2>
          <p className={styles.emptyChatDescription}>
            Select an existing chat from the sidebar or create a new one to get started.
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <button 
          className={styles.menuButton}
          onClick={onMenuClick}
        >
          <Menu size={20} />
        </button>
        <h1 className={styles.title}>KhojAI Chat</h1>
      </div>

      <div className={styles.messagesContainer}>
        {messages.map((message) => (
          <ChatMessage
            key={message.id}
            role={message.role}
            content={message.content}
            timestamp={message.sentAt}
          />
        ))}
        {isLoading && (
          <ChatMessage
            role="AI"
            content=""
            timestamp={new Date()}
            isLoading={true}
          />
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className={styles.inputContainer}>
        <div className={styles.inputWrapper}>
          <textarea
            className={styles.input}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type your message..."
            disabled={isLoading}
            rows={1}
          />
          <button
            className={styles.sendButton}
            onClick={handleSend}
            disabled={!inputValue.trim() || isLoading}
          >
            <Send size={20} />
          </button>
        </div>
      </div>
    </div>
  )
}