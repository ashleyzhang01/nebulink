'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import axios from 'axios'
import { FaQuestionCircle } from 'react-icons/fa'

export default function Settings() {
  const [isLoading, setIsLoading] = useState(true)
  const [githubUsername, setGithubUsername] = useState('')
  const [githubToken, setGithubToken] = useState('')
  const [linkedinEmail, setLinkedinEmail] = useState('')
  const [linkedinPassword, setLinkedinPassword] = useState('')
  const [linkedinUserId, setLinkedinUserId] = useState('')
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
        username: linkedinUserId,
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
    return <div className="flex justify-center items-center h-screen">Loading...</div>
  }

  return (
    <div className="container mx-auto mt-8 p-4">
      <h1 className="text-3xl font-bold mb-8 text-center text-white">Connect Your Accounts</h1>
      
      <div className="mb-12 bg-gray-800 bg-opacity-50 p-6 rounded-lg shadow-lg">
      <h2 className="text-2xl font-semibold mb-4 text-white">github</h2>
        <form onSubmit={handleGithubSubmit} className="space-y-4">
          <div>
            <label htmlFor="githubUsername" className="block mb-1 text-white">github username</label>
            <input
              type="text"
              id="githubUsername"
              value={githubUsername}
              onChange={(e) => setGithubUsername(e.target.value)}
              className="w-full p-2 rounded bg-gray-700 bg-opacity-50 text-white"
              required
            />
          </div>
          <div className="relative">
            <label htmlFor="githubToken" className="block mb-1 text-white">
              github token
              <span className="ml-2 inline-block">
                <FaQuestionCircle className="text-gray-400 hover:text-white cursor-pointer" title="Optional, encrypted" />
              </span>
            </label>
            <input
              type="password"
              id="githubToken"
              value={githubToken}
              onChange={(e) => setGithubToken(e.target.value)}
              className="w-full p-2 rounded bg-gray-700 bg-opacity-50 text-white"
            />
          </div>
          <button type="submit" className="bg-gray-700 opacity-30 text-white px-4 py-2 rounded hover:bg-gray-900">
            set github user
          </button>
        </form>
      </div>

      <div className="mb-12 bg-gray-800 bg-opacity-50 p-6 rounded-lg shadow-lg">
        <h2 className="text-2xl font-semibold mb-4 text-white">linkedin</h2>
        <form onSubmit={handleLinkedinSubmit} className="space-y-4">
          <div>
            <label htmlFor="linkedinEmail" className="block mb-1 text-white">linkedin email</label>
            <input
              type="email"
              id="linkedinEmail"
              value={linkedinEmail}
              onChange={(e) => setLinkedinEmail(e.target.value)}
              className="w-full p-2 rounded bg-gray-700 bg-opacity-50 text-white"
              required
            />
          </div>
          <div>
            <label htmlFor="linkedinUserId" className="block mb-1 text-white">linkedin user id</label>
            <input
              type="text"
              id="linkedinUserId"
              value={linkedinUserId}
              onChange={(e) => setLinkedinUserId(e.target.value)}
              className="w-full p-2 rounded bg-gray-700 bg-opacity-50 text-white"
              required
            />
          </div>
          <div className="relative">
            <label htmlFor="linkedinPassword" className="block mb-1 text-white">
              linkedin Password
              <span className="ml-2 inline-block">
                <FaQuestionCircle className="text-gray-400 hover:text-white cursor-pointer" title="Encrypted" />
              </span>
            </label>
            <input
              type="password"
              id="linkedinPassword"
              value={linkedinPassword}
              onChange={(e) => setLinkedinPassword(e.target.value)}
              className="w-full p-2 rounded bg-gray-700 bg-opacity-50 text-white"
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