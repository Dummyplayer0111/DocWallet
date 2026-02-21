import React, { useState, useEffect } from 'react';
import { useNavigate, useParams, Link } from 'react-router-dom';
import api from '../api';
import { narrowPage, glassCard, headerRow, pageTitle, form, fieldLabel, Loader } from '../theme';

export default function RenameCategory() {
  const { id } = useParams();
  const [name, setName] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    api.get('/api/categories/').then(res => {
      const cat = res.data.categories.find(c => String(c.id) === id);
      if (cat) setName(cat.name);
    }).finally(() => setLoading(false));
  }, [id]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSubmitting(true);
    try {
      await api.patch(`/api/categories/${id}/`, { name });
      navigate('/home/edit');
    } catch (err) {
      setError(err.response?.data?.error || 'Something went wrong');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <Loader />;

  return (
    <div style={narrowPage}>
      <div className="glass-card fade-up" style={glassCard}>
        <div style={headerRow}>
          <h2 style={pageTitle}>Rename Category</h2>
          <Link to="/home/edit" className="btn btn-ghost btn-sm">← Back</Link>
        </div>

        <form onSubmit={handleSubmit} style={form}>
          <div>
            <label style={fieldLabel}>New name</label>
            <input
              type="text"
              value={name}
              onChange={e => setName(e.target.value)}
              required
            />
          </div>
          {error && <div className="form-error">⚠ {error}</div>}
          <button type="submit" className="btn btn-primary" disabled={submitting} style={{ width: '100%', padding: '0.8rem' }}>
            {submitting ? 'Saving…' : 'Save Changes'}
          </button>
        </form>
      </div>
    </div>
  );
}
