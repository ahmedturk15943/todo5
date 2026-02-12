'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { getCurrentUser } from '@/lib/auth'
import { getUserActivities } from '@/lib/api'
import Navigation from '@/components/Navigation'
import ActivityLog from '@/components/ActivityLog'

interface Activity {
  id: number
  action: string
  entity_type: string
  entity_id?: number
  task_id?: number
  changes?: Record<string, any>
  metadata?: Record<string, any>
  created_at: string
}

export default function ActivityPage() {
  const router = useRouter()
  const [activities, setActivities] = useState<Activity[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string>('')
  const [filter, setFilter] = useState<string>('all')

  const currentUser = getCurrentUser()

  useEffect(() => {
    if (!currentUser) {
      router.push('/signin')
      return
    }
    fetchActivities()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filter])

  const fetchActivities = async () => {
    setIsLoading(true)
    setError('')

    try {
      const params: any = { limit: 100 }
      if (filter !== 'all') {
        params.action = filter
      }

      const data = await getUserActivities(params)
      setActivities(data)
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to load activity history'
      setError(errorMessage)
    } finally {
      setIsLoading(false)
    }
  }

  if (!currentUser) return null

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900">Activity History</h1>
          <p className="mt-2 text-gray-600">
            View all your task operations and changes
          </p>
        </div>

        {/* Filter Buttons */}
        <div className="mb-6 flex flex-wrap gap-2">
          <button
            onClick={() => setFilter('all')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              filter === 'all'
                ? 'bg-blue-600 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-300'
            }`}
          >
            All Activities
          </button>
          <button
            onClick={() => setFilter('created')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              filter === 'created'
                ? 'bg-green-600 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-300'
            }`}
          >
            Created
          </button>
          <button
            onClick={() => setFilter('updated')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              filter === 'updated'
                ? 'bg-blue-600 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-300'
            }`}
          >
            Updated
          </button>
          <button
            onClick={() => setFilter('completed')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              filter === 'completed'
                ? 'bg-purple-600 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-300'
            }`}
          >
            Completed
          </button>
          <button
            onClick={() => setFilter('deleted')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              filter === 'deleted'
                ? 'bg-red-600 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-300'
            }`}
          >
            Deleted
          </button>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-6">
            {error}
          </div>
        )}

        {/* Activity Log */}
        <ActivityLog activities={activities} isLoading={isLoading} />

        {/* Load More Button */}
        {!isLoading && activities.length >= 100 && (
          <div className="mt-6 text-center">
            <button
              onClick={() => {
                // Implement pagination
                console.log('Load more activities')
              }}
              className="btn-secondary"
            >
              Load More
            </button>
          </div>
        )}
      </main>
    </div>
  )
}
