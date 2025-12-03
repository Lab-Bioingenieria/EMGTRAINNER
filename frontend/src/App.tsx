import { useState } from 'react'
import {Routes,Route} from 'react-router-dom'
import { DashboardLayout } from './layouts/dashboard-layout'
import { HomeLayout } from './layouts/home-layout'
import { LabLayout } from './layouts/lab-layout'
import { ConfigLayout } from './layouts/config-layout'
import { AnalyticsLayout } from './layouts/analytics-layout'
import { PatientsLayout } from './layouts/patients-layout'
import Home from './pages/Home'
import Dashboard from './pages/dashboard/dashboard'
import Lab from './pages/lab/lab'
import Config from './pages/dashboard/pages/config/config'
import Analytics from './pages/dashboard/pages/analytics/analytics'
import Patients from './pages/dashboard/pages/patients/patients'
import './App.css'

function App() {
  //const [count, setCount] = useState(0)

  return (
    <Routes>
      <Route path='/' 
      element={
      <HomeLayout>
        <Home />
      </HomeLayout>
      } />
      <Route 
      path='/dashboard' 
      element={
      <DashboardLayout>
        <Dashboard />
        
      </DashboardLayout>
      } />
      <Route 
      path='/lab' 
      element={
      <LabLayout>
        <Lab />
      </LabLayout>
      } 
      /> 
      <Route 
        path='/config' 
        element={
        <ConfigLayout>
          <Config />
        </ConfigLayout>
        } />
        <Route 
        path='/analytics' 
        element={
        <AnalyticsLayout>
          <Analytics />
        </AnalyticsLayout>
        } />
        <Route 
        path='/patients' 
        element={
        <PatientsLayout>
          <Patients />
        </PatientsLayout>
        } />
    </Routes>
  )
}

export default App
