import { useState } from 'react'
import {Routes,Route} from 'react-router-dom'
import Home from './pages/Home'
import Dashboard from './pages/dashboard/dashboard'
import './App.css'

function App() {
  //const [count, setCount] = useState(0)

  return (
    <Routes>
      <Route path='/' element={<Home />} />
      <Route path='/dashboard' element={<Dashboard />} />
      {/* <Route path='/about' element={<About />} /> */}
    </Routes>
  )
}

export default App
