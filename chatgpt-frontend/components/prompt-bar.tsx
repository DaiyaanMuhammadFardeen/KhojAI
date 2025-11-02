"use client"

import type React from "react"
import { useState, useRef } from "react"
import { Send } from "lucide-react"

interface PromptBarProps {
  onSendMessage: (message: string) => void
  isLoading: boolean
}

export default function PromptBar({ onSendMessage, isLoading }: PromptBarProps) {
  const [input, setInput] = useState("")
  const [rows, setRows] = useState(1)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value
    setInput(value)

    const lineCount = value.split("\n").length
    setRows(Math.min(Math.max(lineCount, 1), 4))
  }

  const handleSend = () => {
    if (input.trim() && !isLoading) {
      onSendMessage(input)
      setInput("")
      setRows(1)
      if (textareaRef.current) {
        textareaRef.current.focus()
      }
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="px-6 md:px-4 py-4 border-t border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-950 transition-colors duration-200">
      <div className="flex gap-3 items-end bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg p-3 transition-all focus-within:border-green-600 focus-within:shadow-sm">
        <textarea
          ref={textareaRef}
          value={input}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          placeholder="Message ChatBot..."
          rows={rows}
          disabled={isLoading}
          className="flex-1 bg-transparent border-none outline-none resize-none font-sans text-sm text-slate-900 dark:text-slate-100 placeholder-slate-500 dark:placeholder-slate-400 max-h-32 leading-relaxed disabled:opacity-60 disabled:cursor-not-allowed"
        />
        <button
          onClick={handleSend}
          disabled={!input.trim() || isLoading}
          className="flex-shrink-0 w-8 h-8 bg-green-600 hover:bg-green-700 border-none rounded-md text-white cursor-pointer flex items-center justify-center transition-all hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed"
          title="Send message (Enter)"
        >
          <Send size={20} />
        </button>
      </div>
      <p className="text-xs text-slate-500 dark:text-slate-400 mt-2 px-3">Press Shift + Enter for new line</p>
    </div>
  )
}
