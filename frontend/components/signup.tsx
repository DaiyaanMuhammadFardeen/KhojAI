"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import styles from '@/styles/components/signup.module.scss'
import { UserAPI, CreateUserRequest } from '@/app/api/chat/route'

interface SignupProps {
  onLoginSuccess?: () => void
}

export default function Signup({ onLoginSuccess }: SignupProps) {
  const [username, setUsername] = useState("")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  const router = useRouter()

  const handleLoginComplete = (userId: string, username: string) => {
    // Store user info in localStorage
    localStorage.setItem('userId', userId)
    localStorage.setItem('username', username)
    
    // Notify parent component of successful login
    if (onLoginSuccess) {
      onLoginSuccess()
    } else {
      // Fallback redirect
      router.push('/chat')
    }
  }

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault()
    
    // Validate passwords match
    if (password !== confirmPassword) {
      setError("Passwords do not match")
      return
    }
    
    setIsLoading(true)
    setError(null)
    setSuccess(null)

    try {
      // Create a user
      const userData: CreateUserRequest = {
        username,
        email,
        password
      }

      console.log("Sending signup request with data:", userData);
      
      const response = await UserAPI.create(userData)
      
      console.log("Signup response:", response);
      
      if (response.data) {
        setSuccess("Account created successfully!")
        // Complete login process
        handleLoginComplete(response.data.id, response.data.username)
      }
    } catch (err: any) {
      console.error("Signup error:", err);
      
      // Handle different error types
      if (err.code === 'ERR_NETWORK') {
        setError("Network error or CORS issue. Please check your connection and try again.");
      } else if (err.response?.status === 403 || err.response?.status === 401) {
        setError("Authentication error. Please refresh the page and try again.");
      } else if (err.response?.status === 0) {
        setError("Network error or CORS issue. Please check your connection and try again.");
      } else if (err.message?.includes('Network Error')) {
        setError("Network error. Please check your internet connection.");
      } else {
        setError(`Failed to create account: ${err.message || err.toString()}. Please try again.`);
      }
    } finally {
      setIsLoading(false)
    }
  }

  const handleGuestAccess = async () => {
    setIsLoading(true)
    setError(null)
    setSuccess(null)
    
    try {
      // Create a guest user with default values
      const userData: CreateUserRequest = {
        username: `guest_${Date.now()}`,
        email: `guest_${Date.now()}@khojai.local`,
        password: "guest_password"
      }

      console.log("Sending guest access request with data:", userData);
      
      const response = await UserAPI.create(userData)
      
      console.log("Guest access response:", response);
      
      if (response.data) {
        setSuccess("Guest access granted!")
        // Complete login process
        handleLoginComplete(response.data.id, response.data.username)
      }
    } catch (err: any) {
      console.error("Guest access error:", err);
      
      // Handle different error types with more specific messages
      if (err.code === 'ERR_NETWORK' || !err.response || err.code === 'ECONNABORTED') {
        setError("Network connection error. Please check your internet connection and try again. If you're accessing this from a mobile device, make sure the backend server is accessible.");
      } else if (err.response?.status === 403 || err.response?.status === 401) {
        setError("Authentication error. Please refresh the page and try again.");
      } else if (err.response?.status === 0) {
        setError("Unable to connect to the server. This might be a CORS or network connectivity issue.");
      } else if (err.message?.includes('Network Error')) {
        setError("Network error. Please check your internet connection. If accessing from mobile, ensure the backend server is reachable.");
      } else {
        setError(`Failed to create guest account: ${err.message || err.toString()}. Please try again.`);
      }
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className={styles.signupContainer}>
      <div className={styles.signupCard}>
        <h1 className={styles.title}>Welcome to KhojAI</h1>
        <p className={styles.description}>
          Create an account or continue as a guest to start chatting with our AI assistant
        </p>
        
        <form onSubmit={handleSignup}>
          <div className={styles.formGroup}>
            <label htmlFor="username" className={styles.label}>
              Username
            </label>
            <input
              id="username"
              type="text"
              className={styles.input}
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Enter your username"
              disabled={isLoading}
              required
            />
          </div>
          
          <div className={styles.formGroup}>
            <label htmlFor="email" className={styles.label}>
              Email
            </label>
            <input
              id="email"
              type="email"
              className={styles.input}
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Enter your email"
              disabled={isLoading}
              required
            />
          </div>
          
          <div className={styles.formGroup}>
            <label htmlFor="password" className={styles.label}>
              Password
            </label>
            <input
              id="password"
              type="password"
              className={styles.input}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your password"
              disabled={isLoading}
              required
            />
          </div>
          
          <div className={styles.formGroup}>
            <label htmlFor="confirmPassword" className={styles.label}>
              Confirm Password
            </label>
            <input
              id="confirmPassword"
              type="password"
              className={styles.input}
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="Confirm your password"
              disabled={isLoading}
              required
            />
          </div>
          
          <button
            type="submit"
            className={styles.submitBtn}
            disabled={isLoading}
          >
            {isLoading ? "Creating Account..." : "Create Account"}
          </button>
        </form>
        
        <button
          type="button"
          className={styles.guestBtn}
          onClick={handleGuestAccess}
          disabled={isLoading}
        >
          {isLoading ? "Setting up..." : "Continue as Guest"}
        </button>
        
        <div className={styles.footer}>
          <p>
            Already have an account?{' '}
            <Link href="/login" className={styles.link}>
              Sign in
            </Link>
          </p>
        </div>
        
        {error && <div className={styles.error}>{error}</div>}
        {success && <div className={styles.success}>{success}</div>}
      </div>
    </div>
  )
}