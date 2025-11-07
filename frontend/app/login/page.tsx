"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { AuthAPI, LoginRequest } from '@/app/api/chat/route'
import styles from '@/styles/components/signup.module.scss'

export default function Login() {
  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const router = useRouter()

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError(null)

    try {
      const loginData: LoginRequest = {
        username,
        password
      }

      const response = await AuthAPI.login(loginData)
      
      if (response.data) {
        // Store token and user info in localStorage
        localStorage.setItem('token', response.data.token)
        localStorage.setItem('userId', response.data.userId)
        localStorage.setItem('username', response.data.username)
        
        // Redirect to chat page
        router.push('/chat')
      }
    } catch (err: any) {
      console.error("Login error:", err)
      
      if (err.response?.status === 401) {
        setError("Invalid username or password")
      } else {
        setError(`Login failed: ${err.message || err.toString()}`)
      }
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className={styles.signupContainer}>
      <div className={styles.signupCard}>
        <h1 className={styles.title}>Welcome Back</h1>
        <p className={styles.description}>
          Sign in to your account to continue
        </p>
        
        <form onSubmit={handleLogin}>
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
          
          <button
            type="submit"
            className={styles.submitBtn}
            disabled={isLoading}
          >
            {isLoading ? "Signing in..." : "Sign In"}
          </button>
        </form>
        
        {error && <div className={styles.error}>{error}</div>}
        
        <div className={styles.footer}>
          <p>
            Don&apos;t have an account?{' '}
            <Link href="/" className={styles.link}>
              Sign up
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}