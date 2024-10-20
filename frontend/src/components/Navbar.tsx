'use client'

import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useState, useEffect } from 'react'

export default function Navbar() {
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const router = useRouter()

  useEffect(() => {
    // Check if token exists in localStorage
    const token = localStorage.getItem('token')
    setIsLoggedIn(!!token)
  }, [])

  const handleLogout = () => {
    localStorage.removeItem('token')
    setIsLoggedIn(false)
    router.push('/login')
  }

  return (
    <nav className="bg-black bg-opacity-80 p-4 fixed top-0 left-0 right-0 z-50">
      <div className="container mx-auto flex justify-between items-center">
        <Link href="/" className="text-white font-bold">
          nebulink
        </Link>
        <div className="flex items-center">
          {isLoggedIn ? (
            <>
              <Link href="/settings" className="text-white mr-4">
                connect
              </Link>
              <button onClick={handleLogout} className="text-white">
                logout
              </button>
            </>
          ) : (
            <>
              <Link href="/login" className="text-white mr-4">
                login
              </Link>
              <Link href="/signup" className="text-white">
                sign up
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  )
}