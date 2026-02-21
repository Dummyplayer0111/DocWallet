import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import api from '../api';
import { narrowPage, glassCard, headerRow, pageTitle, form, fieldLabel, Loader } from '../theme';

export default function SelectTimeframe() {
  const { uuid } = useParams();
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [allCategories, setAllCategories] = useState([]);
  const [selectedCategories, setSelectedCategories] = useState([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(!uuid);
  const [submitting, setSubmitting] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    if (!uuid) {
      api.get('/api/categories/')
        .then(res => setAllCategories(res.data.categories))
        .finally(() => setLoading(false));
    }
  }, [uuid]);

  const toggleCategory = (name) => {
    setSelectedCategories(prev =>
      prev.includes(name) ? prev.filter(c => c !== name) : [...prev, name]
    );
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    if (!uuid && selectedCategories.length === 0) {
      setError('Select at least one category');
      return;
    }
    setSubmitting(true);
    try {
      let res;
      if (uuid) {
        res = await api.post(`/api/export/${uuid}/`, { start_date: startDate, end_date: endDate });
      } else {
        res = await api.post('/api/export/', { start_date: startDate, end_date: endDate, categories: selectedCategories });
      }
      navigate('/export/results', { state: { bills: res.data.bills } });
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
          <h2 style={pageTitle}>Export Bills</h2>
          <Link to="/home" className="btn btn-ghost btn-sm">← Home</Link>
        </div>

        <form onSubmit={handleSubmit} style={form}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
            <div>
              <label style={fieldLabel}>From</label>
              <input type="date" value={startDate} onChange={e => setStartDate(e.target.value)} required />
            </div>
            <div>
              <label style={fieldLabel}>To</label>
              <input type="date" value={endDate} onChange={e => setEndDate(e.target.value)} required />
            </div>
          </div>

          {!uuid && (
            <div>
              <label style={fieldLabel}>Categories</label>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginTop: '0.3rem' }}>
                {allCategories.map(cat => {
                  const selected = selectedCategories.includes(cat.name);
                  return (
                    <button
                      key={cat.uuid}
                      type="button"
                      onClick={() => toggleCategory(cat.name)}
                      style={{
                        padding: '0.4rem 0.9rem',
                        borderRadius: 20,
                        border: `1px solid ${selected ? 'rgba(91,141,239,0.6)' : 'rgba(91,141,239,0.2)'}`,
                        background: selected ? 'rgba(91,141,239,0.18)' : 'rgba(255,255,255,0.7)',
                        color: selected ? '#1a237e' : '#5c6bc0',
                        fontWeight: selected ? 600 : 400,
                        fontSize: '0.85rem',
                        cursor: 'pointer',
                        fontFamily: 'inherit',
                        transition: 'all 0.2s',
                      }}
                    >
                      {selected ? '✓ ' : ''}{cat.name}
                    </button>
                  );
                })}
              </div>
            </div>
          )}

          {error && <div className="form-error">⚠ {error}</div>}

          <button
            type="submit"
            className="btn btn-primary"
            disabled={submitting}
            style={{ width: '100%', padding: '0.85rem' }}
          >
            {submitting ? (
              <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <span className="spinner" style={{ width: 18, height: 18, borderWidth: 2 }} />
                Searching…
              </span>
            ) : '🔍 View Bills'}
          </button>
        </form>
      </div>
    </div>
  );
}
