import React from "react";
import "./App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./contexts/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";
import Layout from "./components/Layout";

// Pages
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Books from "./pages/Books";
import MyLoans from "./pages/MyLoans";
import Users from "./pages/Users";
import Statistics from "./pages/Statistics";
import Admin from "./pages/Admin";

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <AuthProvider>
          <Routes>
            {/* Public routes */}
            <Route path="/login" element={<Login />} />
            
            {/* Protected routes with layout */}
            <Route path="/" element={
              <ProtectedRoute>
                <Layout />
              </ProtectedRoute>
            }>
              <Route index element={<Navigate to="/dashboard" replace />} />
              <Route path="dashboard" element={<Dashboard />} />
              <Route path="books" element={<Books />} />
              <Route path="my-loans" element={<MyLoans />} />
              
              {/* Admin/Librarian only routes */}
              <Route path="loans" element={
                <ProtectedRoute requireRole="librarian">
                  <div className="text-center py-12">
                    <h2 className="text-2xl font-bold mb-4">Gestion des Prêts</h2>
                    <p className="text-muted-foreground">Page en développement</p>
                  </div>
                </ProtectedRoute>
              } />
              
              <Route path="users" element={
                <ProtectedRoute requireRole="librarian">
                  <div className="text-center py-12">
                    <h2 className="text-2xl font-bold mb-4">Gestion des Utilisateurs</h2>
                    <p className="text-muted-foreground">Page en développement</p>
                  </div>
                </ProtectedRoute>
              } />
              
              <Route path="statistics" element={
                <ProtectedRoute requireRole="librarian">
                  <div className="text-center py-12">
                    <h2 className="text-2xl font-bold mb-4">Statistiques</h2>
                    <p className="text-muted-foreground">Page en développement</p>
                  </div>
                </ProtectedRoute>
              } />
              
              <Route path="admin" element={
                <ProtectedRoute requireRole="admin">
                  <div className="text-center py-12">
                    <h2 className="text-2xl font-bold mb-4">Administration</h2>
                    <p className="text-muted-foreground">Page en développement</p>
                  </div>
                </ProtectedRoute>
              } />
            </Route>
            
            {/* Catch all - redirect to dashboard */}
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </AuthProvider>
      </BrowserRouter>
    </div>
  );
}

export default App;