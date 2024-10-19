'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'

export default function Settings() {
  const [isLoading, setIsLoading] = useState(true)
  const router = useRouter()

  useEffect(() => {
    const token = localStorage.getItem('token')
    console.log(token)
    if (!token) {
      router.push('/login')
    } else {
      setIsLoading(false)
    }
  }, [router])

  if (isLoading) {
    return <div>Loading...</div>
  }

  return (
    <div className="container mx-auto mt-8">
      <h1 className="text-2xl font-bold mb-4">Settings</h1>
      <p>Welcome to your settings page!</p>
    </div>
  )
}