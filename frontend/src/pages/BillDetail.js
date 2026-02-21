import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import api from '../api';
import { page, Loader } from '../theme';

export default function BillDetail() {
  const location = useLocation();
  const params = new URLSearchParams(location.search);
  const date = params.get('date');
  const time = params.get('time');
  const category = params.get('category');
  const value = params.get('value');
  const navigate = useNavigate();

  const [fileId, setFileId] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get(`/api/bill/?date=${date}&time=${time}&category=${category}&value=${value}`)
      .then(res => setFileId(res.data.id))
      .finally(() => setLoading(false));
  }, [date, time, category, value]);

  const query = `?date=${date}&time=${time}&category=${category}&value=${value}`;

  if (loading) return <Loader />;

  return (
    <div style={{ ...page, maxWidth: 720 }}>
      {/* Header */}
      <div className="fade-up" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1.5rem' }}>
        <div>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: '0.3rem' }}>{category}</h2>
          <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
            <span style={badge}>{date}</span>
            <span style={badge}>{time}</span>
            <span style={{ ...badge, background: 'rgba(91,141,239,0.12)', border: '1px solid rgba(91,141,239,0.3)', color: '#2e7d32', fontWeight: 700 }}>
              £{parseFloat(value).toFixed(2)}
            </span>
          </div>
        </div>
        <button className="btn btn-ghost btn-sm" onClick={() => navigate('/home')}>← Home</button>
      </div>

      {/* Receipt preview */}
      <div className="glass-card fade-up" style={{ padding: 0, overflow: 'hidden', marginBottom: '1.25rem' }}>
        {fileId ? (
          <iframe
            title="receipt"
            src={`https://drive.google.com/file/d/${fileId}/preview`}
            style={{ width: '100%', height: 480, border: 'none', display: 'block' }}
            allow="autoplay"
          />
        ) : (
          <div style={{ padding: '3rem', textAlign: 'center', color: '#5c6bc0' }}>
            <div style={{ fontSize: '3rem', marginBottom: '0.5rem' }}>🖼️</div>
            Image not found in Drive.
          </div>
        )}
      </div>

      {/* Action */}
      <div className="fade-up" style={{ display: 'flex', justifyContent: 'flex-end' }}>
        <button
          className="btn btn-primary"
          onClick={() => navigate(`/bill/edit${query}`)}
          style={{ padding: '0.7rem 1.6rem' }}
        >
          ✏️ Edit Bill
        </button>
      </div>
    </div>
  );
}

const badge = {
  padding: '0.25rem 0.65rem',
  background: 'rgba(91,141,239,0.08)',
  border: '1px solid rgba(91,141,239,0.2)',
  borderRadius: 6,
  fontSize: '0.8rem',
  color: '#3949ab',
  fontWeight: 500,
};
