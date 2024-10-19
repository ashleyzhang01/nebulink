'use client'

import { useState, useEffect } from 'react'
import axios from 'axios'

interface Item {
  id: number
  name: string
  description: string | null
}

export default function Home() {
  const [items, setItems] = useState<Item[]>([])
  const [newItem, setNewItem] = useState({ name: '', description: '' })

  useEffect(() => {
    fetchItems()
  }, [])

  const fetchItems = async () => {
    try {
      const response = await axios.get('http://localhost:8000/items/')
      setItems(response.data)
    } catch (error) {
      console.error('Error fetching items:', error)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await axios.post('http://localhost:8000/items/', newItem)
      setNewItem({ name: '', description: '' })
      fetchItems()
    } catch (error) {
      console.error('Error creating item:', error)
    }
  }

  return (
    <main className="p-8">
      <h1 className="text-3xl font-bold mb-4">Items</h1>
      <form onSubmit={handleSubmit} className="mb-4">
        <input
          type="text"
          placeholder="Name"
          value={newItem.name}
          onChange={(e) => setNewItem({ ...newItem, name: e.target.value })}
          className="border p-2 mr-2"
        />
        <input
          type="text"
          placeholder="Description"
          value={newItem.description}
          onChange={(e) => setNewItem({ ...newItem, description: e.target.value })}
          className="border p-2 mr-2"
        />
        <button type="submit" className="bg-blue-500 text-white p-2 rounded">
          Add Item
        </button>
      </form>
      <ul>
        {items.map((item) => (
          <li key={item.id} className="mb-2">
            <strong>{item.name}</strong>: {item.description}
          </li>
        ))}
      </ul>
    </main>
  )
}