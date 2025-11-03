"use client"
import ReactMarkdown from "react-markdown"
import { Copy, Check } from "lucide-react"
import { useState } from "react"

interface Message {
  id: string
  role: "user" | "assistant"
  content: string
  timestamp: Date
}

interface ChatMessageProps {
  message: Message
}

export default function ChatMessage({ message }: ChatMessageProps) {
  const [copied, setCopied] = useState(false)

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div
      className={`flex gap-4 ${message.role === "user" ? "justify-end" : "justify-start"} animate-in fade-in slide-in-from-bottom-2 duration-300 w-full`}
    >
      <div
        className={`flex-shrink-0 w-8 h-8 rounded-md flex items-center justify-center text-xs font-semibold text-white ${message.role === "user" ? "bg-green-600" : "bg-green-600"}`}
      >
        {message.role === "user" ? "You" : "AI"}
      </div>

      <div className="max-w-[80%] w-fit">
        {message.role === "assistant" ? (
          <div className="relative bg-slate-100 dark:bg-slate-800 rounded-lg p-4 text-slate-900 dark:text-slate-100">
            <ReactMarkdown
              components={{
                h1: ({ node, ...props }) => (
                  <h1 className="text-2xl font-bold my-4 text-slate-900 dark:text-slate-100 first:mt-0" {...props} />
                ),
                h2: ({ node, ...props }) => (
                  <h2 className="text-xl font-bold my-3 text-slate-900 dark:text-slate-100" {...props} />
                ),
                h3: ({ node, ...props }) => (
                  <h3 className="text-lg font-semibold my-2 text-slate-900 dark:text-slate-100" {...props} />
                ),
                p: ({ node, ...props }) => (
                  <p className="my-3 leading-relaxed text-slate-900 dark:text-slate-100" {...props} />
                ),
                ul: ({ node, ...props }) => <ul className="my-3 pl-6 text-slate-900 dark:text-slate-100" {...props} />,
                ol: ({ node, ...props }) => <ol className="my-3 pl-6 text-slate-900 dark:text-slate-100" {...props} />,
                li: ({ node, ...props }) => <li className="my-1 leading-relaxed" {...props} />,
                code: ({ node, inline, ...props }) =>
                  inline ? (
                    <code
                      className="bg-slate-200 dark:bg-slate-700 px-1.5 py-0.5 rounded text-sm font-mono text-red-600 dark:text-red-400"
                      {...props}
                    />
                  ) : (
                    <code
                      className="block bg-slate-200 dark:bg-slate-700 p-3 rounded-md font-mono text-sm overflow-x-auto text-slate-900 dark:text-slate-100"
                      {...props}
                    />
                  ),
                pre: ({ node, ...props }) => <pre className="my-3 overflow-x-auto" {...props} />,
                blockquote: ({ node, ...props }) => (
                  <blockquote
                    className="my-3 pl-4 border-l-4 border-slate-300 dark:border-slate-600 italic text-slate-600 dark:text-slate-400"
                    {...props}
                  />
                ),
                a: ({ node, ...props }) => <a className="text-green-600 hover:opacity-80 underline" {...props} />,
              }}
            >
              {message.content}
            </ReactMarkdown>
            <button
              className="absolute top-3 right-3 text-slate-500 dark:text-slate-400 hover:text-green-600 transition-colors p-1"
              onClick={handleCopy}
              title="Copy message"
            >
              {copied ? <Check size={16} /> : <Copy size={16} />}
            </button>
          </div>
        ) : (
          <p className="bg-green-600 text-white rounded-lg p-4 break-words">{message.content}</p>
        )}
      </div>
    </div>
  )
}