// User type definitions

export interface User {
  id: string // UUID
  email: string
  createdAt: string // ISO 8601 timestamp
  updatedAt: string // ISO 8601 timestamp
}

export interface SignUpRequest {
  email: string
  password: string
}

export interface SignInRequest {
  email: string
  password: string
}

export interface AuthResponse {
  user: User
  token: string
}
