export interface Patient {
    id: number
    patient_code: string
    name: string
    age: number
    sessions_count: number
    last_session: string | null
    progress: number
    status: 'active' | 'inactive' | 'completed'
}
