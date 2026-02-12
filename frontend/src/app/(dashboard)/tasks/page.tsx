// // 'use client'

// // import { useEffect, useState } from 'react'
// // import { useRouter } from 'next/navigation'
// // import apiClient, { clearAuthToken } from '@/lib/api'
// // import { getCurrentUser } from '@/lib/auth'
// // import TaskList from '@/components/tasks/TaskList'
// // import TaskForm from '@/components/tasks/TaskForm'
// // import type { Task } from '@/types/task'

// // export default function TasksPage() {
// //   const router = useRouter()
// //   const [tasks, setTasks] = useState<Task[]>([])
// //   const [isLoading, setIsLoading] = useState(true)
// //   const [error, setError] = useState<string>('')
// //   const [showForm, setShowForm] = useState(false)

// //   const currentUser = getCurrentUser()

// //   useEffect(() => {
// //     if (!currentUser) {
// //       router.push('/signin')
// //       return
// //     }

// //     fetchTasks()
// //   }, [currentUser, router])

// //   const fetchTasks = async () => {
// //     if (!currentUser) return

// //     setIsLoading(true)
// //     setError('')

// //     try {
// //       const response = await apiClient.get<Task[]>(`/api/users/${currentUser.id}/tasks`)
// //       setTasks(response.data)
// //     } catch (err: any) {
// //       const errorMessage = err.response?.data?.detail || 'Failed to load tasks'
// //       setError(errorMessage)
// //     } finally {
// //       setIsLoading(false)
// //     }
// //   }

// //   const handleSignOut = () => {
// //     clearAuthToken()
// //     router.push('/')
// //   }

// //   const handleTaskCreated = (newTask: Task) => {
// //     setTasks([newTask, ...tasks])
// //     setShowForm(false)
// //   }

// //   const handleTaskUpdated = (updatedTask: Task) => {
// //     setTasks(tasks.map(task => (task.id === updatedTask.id ? updatedTask : task)))
// //   }

// //   const handleTaskDeleted = (taskId: number) => {
// //     setTasks(tasks.filter(task => task.id !== taskId))
// //   }

// //   if (!currentUser) {
// //     return null
// //   }

// //   return (
// //     <div className="min-h-screen bg-gray-50">
// //       {/* Header */}
// //       <header className="bg-white shadow-sm">
// //         <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
// //           <h1 className="text-2xl font-bold text-gray-900">My Tasks</h1>
// //           <div className="flex items-center space-x-4">
// //             <span className="text-sm text-gray-600">{currentUser.email}</span>
// //             <button onClick={handleSignOut} className="btn-secondary text-sm">
// //               Sign Out
// //             </button>
// //           </div>
// //         </div>
// //       </header>

// //       {/* Main Content */}
// //       <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
// //         {/* Add Task Button */}
// //         <div className="mb-6">
// //           <button
// //             onClick={() => setShowForm(!showForm)}
// //             className="btn-primary"
// //           >
// //             {showForm ? 'Cancel' : '+ Add Task'}
// //           </button>
// //         </div>

// //         {/* Task Form */}
// //         {showForm && (
// //           <div className="mb-6">
// //             <TaskForm
// //               userId={currentUser.id}
// //               onSuccess={handleTaskCreated}
// //               onCancel={() => setShowForm(false)}
// //             />
// //           </div>
// //         )}

// //         {/* Error Message */}
// //         {error && (
// //           <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-6">
// //             {error}
// //           </div>
// //         )}

// //         {/* Loading State */}
// //         {isLoading && (
// //           <div className="text-center py-12">
// //             <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
// //             <p className="mt-2 text-gray-600">Loading tasks...</p>
// //           </div>
// //         )}

// //         {/* Task List */}
// //         {!isLoading && (
// //           <TaskList
// //             tasks={tasks}
// //             userId={currentUser.id}
// //             onTaskUpdated={handleTaskUpdated}
// //             onTaskDeleted={handleTaskDeleted}
// //           />
// //         )}
// //       </main>
// //     </div>
// //   )
// // }






// 'use client' // MUST be first line

// import { useEffect, useState } from 'react'
// import { useRouter } from 'next/navigation'
// import apiClient, { clearAuthToken } from '@/lib/api'
// import { getCurrentUser } from '@/lib/auth'
// import TaskList from '@/components/tasks/TaskList'
// import TaskForm from '@/components/tasks/TaskForm'
// import type { Task } from '@/types/task'

// export default function TasksPage() {
//   const router = useRouter()
//   const [tasks, setTasks] = useState<Task[]>([])
//   const [isLoading, setIsLoading] = useState(true)
//   const [error, setError] = useState<string>('')
//   const [showForm, setShowForm] = useState(false)

//   const currentUser = getCurrentUser()

//   // ✅ useEffect with empty dependency array to avoid infinite loop
//   useEffect(() => {
//     if (!currentUser) {
//       router.push('/signin')
//       return
//     }
//     fetchTasks()
//     // eslint-disable-next-line react-hooks/exhaustive-deps
//   }, [])

//   const fetchTasks = async () => {
//     if (!currentUser) return

//     setIsLoading(true)
//     setError('')

//     try {
//       const response = await apiClient.get<Task[]>(`/api/users/${currentUser.id}/tasks`)
//       setTasks(response.data)
//     } catch (err: any) {
//       const errorMessage = err.response?.data?.detail || 'Failed to load tasks'
//       setError(errorMessage)
//     } finally {
//       setIsLoading(false)
//     }
//   }

//   const handleSignOut = () => {
//     clearAuthToken()
//     router.push('/')
//   }

//   const handleTaskCreated = (newTask: Task) => {
//     setTasks(prev => [newTask, ...prev]) // ✅ use prev to prevent stale state
//     setShowForm(false)
//   }

//   const handleTaskUpdated = (updatedTask: Task) => {
//     setTasks(prev => prev.map(task => (task.id === updatedTask.id ? updatedTask : task)))
//   }

//   const handleTaskDeleted = (taskId: number) => {
//     setTasks(prev => prev.filter(task => task.id !== taskId))
//   }

//   if (!currentUser) return null

//   return (
//     <div className="min-h-screen bg-gray-50">
//       {/* Header */}
//       <header className="bg-white shadow-sm">
//         <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
//           <h1 className="text-2xl font-bold text-gray-900">My Tasks</h1>
//           <div className="flex items-center space-x-4">
//             <span className="text-sm text-gray-600">{currentUser.email}</span>
//             <button onClick={handleSignOut} className="btn-secondary text-sm">
//               Sign Out
//             </button>
//           </div>
//         </div>
//       </header>

//       {/* Main Content */}
//       <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
//         {/* Add Task Button */}
//         <div className="mb-6">
//           <button onClick={() => setShowForm(!showForm)} className="btn-primary">
//             {showForm ? 'Cancel' : '+ Add Task'}
//           </button>
//         </div>

//         {/* Task Form */}
//         {showForm && (
//           <div className="mb-6">
//             <TaskForm userId={currentUser.id} onSuccess={handleTaskCreated} onCancel={() => setShowForm(false)} />
//           </div>
//         )}

//         {/* Error Message */}
//         {error && <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-6">{error}</div>}

//         {/* Loading State */}
//         {isLoading && (
//           <div className="text-center py-12">
//             <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
//             <p className="mt-2 text-gray-600">Loading tasks...</p>
//           </div>
//         )}

//         {/* Task List */}
//         {!isLoading && <TaskList tasks={tasks} userId={currentUser.id} onTaskUpdated={handleTaskUpdated} onTaskDeleted={handleTaskDeleted} />}
//       </main>
//     </div>
//   )
// }










'use client' // MUST be first line

import { useEffect, useState, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import apiClient from '@/lib/api'
import { getCurrentUser } from '@/lib/auth'
import Navigation from '@/components/Navigation'
import TaskList from '@/components/tasks/TaskList'
import TaskForm from '@/components/tasks/TaskForm'
import { useRealTimeSync } from '@/hooks/useRealTimeSync'
import type { Task } from '@/types/task'

// Generate a unique device ID for this browser session
const getDeviceId = () => {
  if (typeof window === 'undefined') return 'server'

  let deviceId = sessionStorage.getItem('device_id')
  if (!deviceId) {
    deviceId = `device-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
    sessionStorage.setItem('device_id', deviceId)
  }
  return deviceId
}

export default function TasksPage() {
  const router = useRouter()
  const [tasks, setTasks] = useState<Task[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string>('')
  const [showForm, setShowForm] = useState(false)

  const currentUser = getCurrentUser()

  // Real-time sync callbacks
  const handleRealtimeTaskUpdate = useCallback((task: Task) => {
    setTasks(prev => {
      const existingIndex = prev.findIndex(t => t.id === task.id)
      if (existingIndex >= 0) {
        // Update existing task
        const updated = [...prev]
        updated[existingIndex] = task
        return updated
      } else {
        // Add new task
        return [task, ...prev]
      }
    })
  }, [])

  const handleRealtimeTaskDelete = useCallback((taskId: number) => {
    setTasks(prev => prev.filter(task => task.id !== taskId))
  }, [])

  // Initialize real-time sync
  const { connected } = useRealTimeSync(
    currentUser?.id,
    handleRealtimeTaskUpdate,
    handleRealtimeTaskDelete
  )

  useEffect(() => {
    if (!currentUser) {
      router.push('/signin')
      return
    }
    fetchTasks()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const fetchTasks = async () => {
    if (!currentUser) return

    setIsLoading(true)
    setError('')

    try {
      const response = await apiClient.get<Task[]>(`/api/users/${currentUser.id}/tasks`)
      setTasks(response.data)
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to load tasks'
      setError(errorMessage)
    } finally {
      setIsLoading(false)
    }
  }

  const handleTaskCreated = (newTask: Task) => {
    setTasks(prev => [newTask, ...prev])
    setShowForm(false)
  }

  const handleTaskUpdated = (updatedTask: Task) => {
    setTasks(prev => prev.map(task => (task.id === updatedTask.id ? updatedTask : task)))
  }

  const handleTaskDeleted = (taskId: number) => {
    setTasks(prev => prev.filter(task => task.id !== taskId))
  }

  if (!currentUser) return null

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Connection Status Indicator */}
        <div className="mb-4 flex items-center justify-end">
          <div className="flex items-center space-x-2 text-sm">
            <div className={`w-2 h-2 rounded-full ${connected ? 'bg-green-500' : 'bg-gray-400'}`}></div>
            <span className="text-gray-600">
              {connected ? 'Real-time sync active' : 'Connecting...'}
            </span>
          </div>
        </div>

        <div className="mb-6">
          <button onClick={() => setShowForm(!showForm)} className="btn-primary">
            {showForm ? 'Cancel' : '+ Add Task'}
          </button>
        </div>

        {showForm && (
          <div className="mb-6">
            <TaskForm userId={currentUser.id} onSuccess={handleTaskCreated} onCancel={() => setShowForm(false)} />
          </div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-6">
            {error}
          </div>
        )}

        {isLoading && (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
            <p className="mt-2 text-gray-600">Loading tasks...</p>
          </div>
        )}

        {!isLoading && (
          <TaskList
            tasks={tasks}
            userId={currentUser.id}
            onTaskUpdated={handleTaskUpdated}
            onTaskDeleted={handleTaskDeleted}
          />
        )}
      </main>
    </div>
  )
}
