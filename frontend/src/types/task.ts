// Task type definitions

export interface Task {
  id: number
  userId: string // UUID
  title: string
  description: string | null
  completed: boolean
  createdAt: string // ISO 8601 timestamp
  updatedAt: string // ISO 8601 timestamp
}

export interface CreateTaskRequest {
  title: string
  description?: string
}

export interface UpdateTaskRequest {
  title?: string
  description?: string
}

export interface TaskListResponse {
  tasks: Task[]
  total: number
}
