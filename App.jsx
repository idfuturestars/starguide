
import React from 'react'
import { Routes, Route } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import MainLayout from './components/layout/MainLayout'
import AuthLayout from './components/layout/AuthLayout'
import Login from './views/auth/Login'
import Register from './views/auth/Register'
import DemoLogin from './views/auth/DemoLogin'
import MissionControl from './views/MissionControl'
import BattleArena from './views/BattleArena'

function App() {
  return (
    <>
      <Routes>
        <Route path="/auth/*" element={<AuthLayout />}>
          <Route path="login" element={<Login />} />
          <Route path="register" element={<Register />} />
          <Route path="demo" element={<DemoLogin />} />
        </Route>
        
        <Route path="/*" element={<MainLayout />}>
          <Route index element={<MissionControl />} />
          <Route path="battle" element={<BattleArena />} />
          {/* Add other protected routes here */}
        </Route>
      </Routes>
      
      <Toaster 
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#1a1a2e',
            color: '#fff',
          },
        }}
      />
    </>
  )
}

export default App
