import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import api from './api';

import SignIn from './pages/SignIn';
import ChooseName from './pages/ChooseName';
import Home from './pages/Home';
import EditCategories from './pages/EditCategories';
import AddCategory from './pages/AddCategory';
import RenameCategory from './pages/RenameCategory';
import BillsPage from './pages/BillsPage';
import NewBill from './pages/NewBill';
import BillDetail from './pages/BillDetail';
import EditBill from './pages/EditBill';
import SelectTimeframe from './pages/SelectTimeframe';
import ChosenBills from './pages/ChosenBills';

function AuthGuard({ children }) {
  const [status, setStatus] = useState(null); // null = loading
  const navigate = useNavigate();

  useEffect(() => {
    api.get('/api/auth/status/')
      .then(res => setStatus(res.data))
      .catch(() => setStatus({ authenticated: false }));
  }, []);

  if (status === null) return <div style={{ textAlign: 'center', marginTop: '4rem' }}>Loading…</div>;
  if (!status.authenticated) return <Navigate to="/" replace />;
  if (status.needs_setup) return <Navigate to="/choose-name" replace />;
  return children;
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<SignIn />} />
        <Route path="/choose-name" element={<ChooseName />} />

        <Route path="/home" element={<AuthGuard><Home /></AuthGuard>} />
        <Route path="/home/edit" element={<AuthGuard><EditCategories /></AuthGuard>} />
        <Route path="/home/edit/add" element={<AuthGuard><AddCategory /></AuthGuard>} />
        <Route path="/home/edit/rename/:id" element={<AuthGuard><RenameCategory /></AuthGuard>} />

        <Route path="/category/:uuid" element={<AuthGuard><BillsPage /></AuthGuard>} />
        <Route path="/category/:uuid/add" element={<AuthGuard><NewBill /></AuthGuard>} />

        <Route path="/bill" element={<AuthGuard><BillDetail /></AuthGuard>} />
        <Route path="/bill/edit" element={<AuthGuard><EditBill /></AuthGuard>} />

        <Route path="/export" element={<AuthGuard><SelectTimeframe /></AuthGuard>} />
        <Route path="/export/results" element={<AuthGuard><ChosenBills /></AuthGuard>} />
        <Route path="/export/:uuid" element={<AuthGuard><SelectTimeframe /></AuthGuard>} />
      </Routes>
    </BrowserRouter>
  );
}
