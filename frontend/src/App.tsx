import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'

function App() {
  const [count, setCount] = useState(0)

  return (
    <>
      <div className="min-h-screen bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center p-4">
        <div className="bg-white rounded-xl shadow-2xl p-8 max-w-md w-full">
          <h1 className="text-4xl font-bold text-gray-800 mb-4">
            ✨ Stack Ready!
          </h1>
          <div className="space-y-2 text-gray-600">
            <p>✅ Vite</p>
            <p>✅ React 19</p>
            <p>✅ TypeScript</p>
            <p>✅ Tailwind CSS v3</p>
          </div>
          <button className="mt-6 w-full bg-blue-500 hover:bg-blue-600 text-white font-semibold py-3 px-4 rounded-lg transition duration-200">
            Get Started
          </button>
        </div>
      </div>
    </>
  )
}

export default App
