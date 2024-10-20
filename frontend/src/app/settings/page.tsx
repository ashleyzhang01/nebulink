'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import axios from 'axios'

export default function Settings() {
  const [isLoading, setIsLoading] = useState(true)
  const [githubUsername, setGithubUsername] = useState('')
  const [githubToken, setGithubToken] = useState('')
  const [linkedinEmail, setLinkedinEmail] = useState('')
  const [linkedinPassword, setLinkedinPassword] = useState('')
  const [message, setMessage] = useState('')
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

  const handleGithubSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setMessage('')
    try {
      const response = await axios.post('http://localhost:8000/api/github/create', {
        username: githubUsername,
        token: githubToken
      }, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      })
      setMessage('GitHub user created and scraping started')
    } catch (error) {
      setMessage('Error creating GitHub user')
    }
  }

  const handleLinkedinSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setMessage('')
    try {
      const response = await axios.post('http://localhost:8000/api/linkedin/create', {
        username: linkedinEmail,
        email: linkedinEmail,
        password: linkedinPassword
      }, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      })
      setMessage('LinkedIn user created and scraping started')
    } catch (error) {
      setMessage('Error creating LinkedIn user')
    }
  }

  if (isLoading) {
    return <div>Loading...</div>
  }

  return (
    <div className="container mx-auto mt-8 p-4">
      <h1 className="text-2xl font-bold mb-4 mt-10">connect your accounts</h1>
      
      <div className="mb-8">
        <h2 className="text-xl font-semibold mb-2">github</h2>
        <form onSubmit={handleGithubSubmit} className="space-y-4">
          <div>
            <label htmlFor="githubUsername" className="block mb-1">github username</label>
            <input
              type="text"
              id="githubUsername"
              value={githubUsername}
              onChange={(e) => setGithubUsername(e.target.value)}
              className="w-full p-2 rounded bg-opacity-20 bg-white"
              required
            />
          </div>
          <div>
            <label htmlFor="githubToken" className="block mb-1">github token (optional, encrypted)</label>
            <input
              type="password"
              id="githubToken"
              value={githubToken}
              onChange={(e) => setGithubToken(e.target.value)}
              className="w-full p-2 rounded bg-opacity-20 bg-white"
            />
          </div>
          <button type="submit" className="bg-gray-700 opacity-30 text-white px-4 py-2 rounded hover:bg-gray-900">
            set github user
          </button>
        </form>
      </div>

      <div className="mb-8">
        <h2 className="text-xl font-semibold mb-2">linkedin</h2>
        <form onSubmit={handleLinkedinSubmit} className="space-y-4">
          <div>
            <label htmlFor="linkedinEmail" className="block mb-1">linkedin email</label>
            <input
              type="email"
              id="linkedinEmail"
              value={linkedinEmail}
              onChange={(e) => setLinkedinEmail(e.target.value)}
              className="w-full p-2 rounded bg-opacity-20 bg-white"
              required
            />
          </div>
          <div>
            <label htmlFor="linkedinPassword" className="block mb-1">linkedin password (encrypted)</label>
            <input
              type="password"
              id="linkedinPassword"
              value={linkedinPassword}
              onChange={(e) => setLinkedinPassword(e.target.value)}
              className="w-full p-2 rounded bg-opacity-20 bg-white"
            />
          </div>
          <button type="submit" className="bg-gray-700 opacity-30 text-white px-4 py-2 rounded hover:bg-gray-900">
            set linkedin user
          </button>
        </form>
      </div>

      {message && (
        <div className="mt-4 p-2 bg-green-100 border border-green-400 text-green-700 rounded">
          {message}
        </div>
      )}
    </div>
  )
}