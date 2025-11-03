"use client"

import { useState } from "react"
import { X, Moon, Sun, LogOut } from "lucide-react"

interface SettingsModalProps {
  onClose: () => void
  onLogout: () => void
}

export default function SettingsModal({ onClose, onLogout }: SettingsModalProps) {
  const [darkMode, setDarkMode] = useState(false)
  const [apiKey, setApiKey] = useState("")
  const [apiEndpoint, setApiEndpoint] = useState("https://api.example.com/chat")

  const handleDarkModeToggle = () => {
    setDarkMode(!darkMode)
    if (!darkMode) {
      document.documentElement.classList.add("dark")
    } else {
      document.documentElement.classList.remove("dark")
    }
  }

  const handleSaveSettings = () => {
    localStorage.setItem(
      "chatbot-settings",
      JSON.stringify({
        darkMode,
        apiKey,
        apiEndpoint,
      }),
    )
    onClose()
  }

  const handleLogout = () => {
    onLogout()
    onClose()
  }

  return (
    <div
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 animate-in fade-in duration-200"
      onClick={onClose}
    >
      <div
        className="bg-white dark:bg-slate-900 rounded-lg shadow-lg max-w-md w-11/12 max-h-screen overflow-y-auto animate-in slide-in-from-bottom-4 duration-300"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200 dark:border-slate-700">
          <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100">Settings</h2>
          <button
            className="text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100 transition-colors p-1"
            onClick={onClose}
          >
            <X size={24} />
          </button>
        </div>

        <div className="px-6 py-4">
          <div className="mb-6">
            <h3 className="text-sm font-semibold text-slate-900 dark:text-slate-100 uppercase tracking-wider mb-4">
              Appearance
            </h3>
            <div className="flex items-center justify-between">
              <span className="text-slate-900 dark:text-slate-100">Dark Mode</span>
              <button
                className={`w-12 h-7 rounded-full transition-all flex items-center ${darkMode ? "bg-green-600 justify-end" : "bg-slate-300 justify-start"} p-0.5`}
                onClick={handleDarkModeToggle}
              >
                {darkMode ? <Moon size={18} className="text-white" /> : <Sun size={18} className="text-slate-600" />}
              </button>
            </div>
          </div>

          <div className="mb-6">
            <h3 className="text-sm font-semibold text-slate-900 dark:text-slate-100 uppercase tracking-wider mb-4">
              API Configuration
            </h3>
            <div className="mb-4">
              <label className="block text-sm font-medium text-slate-900 dark:text-slate-100 mb-2">API Endpoint</label>
              <input
                type="text"
                value={apiEndpoint}
                onChange={(e) => setApiEndpoint(e.target.value)}
                className="w-full px-3 py-2 bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-md text-slate-900 dark:text-slate-100 focus:outline-none focus:border-green-600 focus:shadow-sm"
                placeholder="https://api.example.com/chat"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-900 dark:text-slate-100 mb-2">API Key</label>
              <input
                type="password"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                className="w-full px-3 py-2 bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-md text-slate-900 dark:text-slate-100 focus:outline-none focus:border-green-600 focus:shadow-sm"
                placeholder="Enter your API key"
              />
            </div>
          </div>

          <div className="mb-6">
            <h3 className="text-sm font-semibold text-slate-900 dark:text-slate-100 uppercase tracking-wider mb-4">
              Account
            </h3>
            <button
              className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
              onClick={handleLogout}
            >
              <LogOut size={18} />
              Logout
            </button>
          </div>

          <div>
            <h3 className="text-sm font-semibold text-slate-900 dark:text-slate-100 uppercase tracking-wider mb-2">
              About
            </h3>
            <p className="text-sm text-slate-600 dark:text-slate-400">
              ChatBot v1.0.0 - A ChatGPT-like AI assistant interface
            </p>
          </div>
        </div>

        <div className="flex gap-3 px-6 py-4 border-t border-slate-200 dark:border-slate-700 justify-end">
          <button
            className="px-4 py-2 bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-slate-100 border border-slate-200 dark:border-slate-700 rounded-md hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors"
            onClick={onClose}
          >
            Cancel
          </button>
          <button
            className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
            onClick={handleSaveSettings}
          >
            Save Settings
          </button>
        </div>
      </div>
    </div>
  )
}