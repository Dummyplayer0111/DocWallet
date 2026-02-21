import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import api from '../api';
import { narrowPage, glassCard, headerRow, pageTitle, form, fieldLabel } from '../theme';

export default function AddCategory() {
  const [name, setName] = useState('');
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSubmitting(true);
    try {
      await api.post('/api/categories/', { name });
      navigate('/home/edit');
    } catch (err) {
      setError(err.response?.data?.error || 'Something went wrong');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div style={narrowPage}>
      <div className="glass-card fade-up" style={glassCard}>
        <div style={headerRow}>
          <h2 style={pageTitle}>Add Category</h2>
          <Link to="/home/edit" className="btn btn-ghost btn-sm">← Back</Link>
        </div>

        <form onSubmit={handleSubmit} style={form}>
          <div>
            <label style={fieldLabel}>Category name</label>
            <input
              type="text"
              placeholder="e.g. Food, Travel, Bills…"
              value={name}
              onChange={e => setName(e.target.value)}
              required
            />
          </div>
          {error && <div className="form-error">⚠ {error}</div>}
          <button type="submit" className="btn btn-primary" disabled={submitting} style={{ width: '100%', padding: '0.8rem' }}>
            {submitting ? 'Creating…' : 'Create Category'}
          </button>
        </form>
      </div>
    </div>
  );
}
