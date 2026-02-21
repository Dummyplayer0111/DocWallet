import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import api from '../api';
import { page, pageTitle, Loader } from '../theme';

function parseBillName(name) {
  const parts = name.split('_');
  if (parts.length < 4) return { date: '', time: '', category: name, value: '' };
  return {
    category: parts[0],
    date: parts[1],
    time: parts[2],
    value: parseFloat(parts[3]).toFixed(2),
    raw: name,
  };
}

export default function BillsPage() {
  const { uuid } = useParams();
  const [bills, setBills] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState(new Set());
  const [deleting, setDeleting] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const controller = new AbortController();
    api.get(`/api/bills/${uuid}/`, { signal: controller.signal })
      .then(res => { setBills(res.data.bills); setLoading(false); })
      .catch(err => { if (err.code !== 'ERR_CANCELED') setLoading(false); });
    return () => controller.abort();
  }, [uuid]);

  const allSelected = bills.length > 0 && selected.size === bills.length;
  const someSelected = selected.size > 0;

  const toggleAll = () => {
    if (allSelected) {
      setSelected(new Set());
    } else {
      setSelected(new Set(bills));
    }
  };

  const toggleOne = (name) => {
    setSelected(prev => {
      const next = new Set(prev);
      next.has(name) ? next.delete(name) : next.add(name);
      return next;
    });
  };

  const handleDelete = async () => {
    if (!window.confirm(`Delete ${selected.size} bill${selected.size > 1 ? 's' : ''}? This cannot be undone.`)) return;
    setDeleting(true);
    try {
      await api.delete(`/api/bills/${uuid}/`, { data: { names: [...selected] } });
      setBills(prev => prev.filter(b => !selected.has(b)));
      setSelected(new Set());
    } catch (err) {
      alert('Delete failed. Please try again.');
    } finally {
      setDeleting(false);
    }
  };

  if (loading) return <Loader />;

  const total = bills.reduce((s, n) => s + parseFloat(parseBillName(n).value || 0), 0);
  const selectedTotal = [...selected].reduce((s, n) => s + parseFloat(parseBillName(n).value || 0), 0);

  return (
    <div style={page}>
      {/* Header */}
      <div className="fade-up" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1.5rem' }}>
        <div>
          <h2 style={pageTitle}>Bills</h2>
          {bills.length > 0 && (
            <p style={{ color: '#5c6bc0', fontSize: '0.85rem', marginTop: '0.2rem' }}>
              {bills.length} {bills.length === 1 ? 'bill' : 'bills'} · Total £{total.toFixed(2)}
            </p>
          )}
        </div>
        <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
          <Link to={`/export/${uuid}`} className="nav-link">Export</Link>
          <Link to="/home" className="btn btn-ghost btn-sm">← Home</Link>
        </div>
      </div>

      {/* Selection action bar */}
      {someSelected && (
        <div className="fade-up" style={{
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          padding: '0.75rem 1.1rem', marginBottom: '0.75rem',
          background: 'rgba(239,83,80,0.08)',
          border: '1px solid rgba(239,83,80,0.25)',
          borderRadius: 12,
        }}>
          <span style={{ fontSize: '0.9rem', color: '#c62828' }}>
            {selected.size} selected · £{selectedTotal.toFixed(2)}
          </span>
          <div style={{ display: 'flex', gap: '0.6rem' }}>
            <button className="btn btn-ghost btn-sm" onClick={() => setSelected(new Set())}>
              Clear
            </button>
            <button className="btn btn-danger btn-sm" onClick={handleDelete} disabled={deleting}>
              {deleting ? 'Deleting…' : `🗑 Delete ${selected.size}`}
            </button>
          </div>
        </div>
      )}

      {bills.length === 0 ? (
        <div className="glass-card fade-up" style={{ padding: '3rem', textAlign: 'center' }}>
          <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🧾</div>
          <p style={{ color: '#5c6bc0', marginBottom: '1.5rem' }}>No bills yet in this category.</p>
          <Link to={`/category/${uuid}/add`} className="btn btn-primary">Add your first bill</Link>
        </div>
      ) : (
        <div className="glass-card fade-up" style={{ padding: 0, overflow: 'hidden' }}>
          <table className="dw-table">
            <thead>
              <tr>
                <th style={{ width: 44 }}>
                  <input
                    type="checkbox"
                    checked={allSelected}
                    ref={el => { if (el) el.indeterminate = someSelected && !allSelected; }}
                    onChange={toggleAll}
                    style={{ cursor: 'pointer' }}
                  />
                </th>
                <th>Date</th>
                <th>Time</th>
                <th>Category</th>
                <th>Value (£)</th>
              </tr>
            </thead>
            <tbody>
              {bills.map((name, i) => {
                const b = parseBillName(name);
                const query = `?date=${b.date}&time=${b.time}&category=${b.category}&value=${b.value}`;
                const isSelected = selected.has(name);
                return (
                  <tr
                    key={name}
                    style={{
                      animationDelay: `${i * 0.04}s`,
                      cursor: 'pointer',
                      background: isSelected ? 'rgba(239,83,80,0.06)' : undefined,
                    }}
                  >
                    <td onClick={e => { e.stopPropagation(); toggleOne(name); }} style={{ width: 44 }}>
                      <input
                        type="checkbox"
                        checked={isSelected}
                        readOnly
                        style={{ cursor: 'pointer', pointerEvents: 'none' }}
                      />
                    </td>
                    <td onClick={() => navigate(`/bill${query}`)}>{b.date}</td>
                    <td onClick={() => navigate(`/bill${query}`)} style={{ color: '#5c6bc0' }}>{b.time}</td>
                    <td onClick={() => navigate(`/bill${query}`)}>{b.category}</td>
                    <td onClick={() => navigate(`/bill${query}`)} style={{ fontWeight: 600, color: '#2e7d32' }}>£{b.value}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Floating add button */}
      <Link
        to={`/category/${uuid}/add`}
        className="btn btn-primary"
        style={{
          position: 'fixed', bottom: '2rem', right: '2rem',
          borderRadius: '50%', width: 56, height: 56,
          fontSize: '1.6rem',
          boxShadow: '0 8px 32px rgba(91,141,239,0.45)',
          zIndex: 50, padding: 0,
        }}
      >
        +
      </Link>
    </div>
  );
}
