import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import api from '../api';
import { page, glassCard, headerRow, pageTitle, fieldLabel, Loader } from '../theme';

export default function EditCategories() {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const controller = new AbortController();
    api.get('/api/categories/', { signal: controller.signal })
      .then(res => { setCategories(res.data.categories); setLoading(false); })
      .catch(err => { if (err.code !== 'ERR_CANCELED') setLoading(false); });
    return () => controller.abort();
  }, []);

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this category and its Drive folder?')) return;
    const res = await api.delete(`/api/categories/${id}/`);
    setCategories(res.data.categories);
  };
  // Note: delete returns the updated list directly, no refetch needed

  if (loading) return <Loader />;

  return (
    <div style={{ ...page, maxWidth: 620 }}>
      <div className="glass-card fade-up" style={{ ...glassCard }}>
        <div style={headerRow}>
          <h2 style={pageTitle}>Edit Categories</h2>
          <Link to="/home" className="btn btn-ghost btn-sm">← Back</Link>
        </div>

        <Link to="/home/edit/add" className="btn btn-primary" style={{ marginBottom: '1.5rem', display: 'inline-flex' }}>
          + Add category
        </Link>

        {categories.length === 0 ? (
          <p style={{ color: '#5c6bc0', textAlign: 'center', padding: '2rem 0' }}>No categories yet.</p>
        ) : (
          <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
            {categories.map((cat, i) => (
              <li
                key={cat.uuid}
                className="fade-up"
                style={{
                  animationDelay: `${i * 0.05}s`,
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '0.9rem 1.1rem',
                  background: 'rgba(91,141,239,0.06)',
                  border: '1px solid rgba(91,141,239,0.14)',
                  borderRadius: 12,
                  transition: 'background 0.2s',
                }}
              >
                <span style={{ fontWeight: 500, fontSize: '0.95rem' }}>{cat.name}</span>
                <div style={{ display: 'flex', gap: '0.5rem' }}>
                  <button
                    className="btn btn-outline btn-sm"
                    onClick={() => navigate(`/home/edit/rename/${cat.id}`)}
                  >
                    Rename
                  </button>
                  <button
                    className="btn btn-danger btn-sm"
                    onClick={() => handleDelete(cat.id)}
                  >
                    Delete
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
