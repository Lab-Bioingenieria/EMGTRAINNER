export interface Patient {
    id: string
    name: string
    age: number
    sessions: number
    lastSession: string
    progress: number
    status: 'active' | 'inactive' | 'completed'
}
