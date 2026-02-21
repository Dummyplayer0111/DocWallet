import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import api from '../api';
import { page, glassCard, form, fieldLabel, Loader } from '../theme';

export default function EditBill() {
  const location = useLocation();
  const params = new URLSearchParams(location.search);
  const date = params.get('date');
  const time = params.get('time');
  const origCategory = params.get('category');
  const origValue = params.get('value');
  const navigate = useNavigate();

  const [categories, setCategories] = useState([]);
  const [newCategory, setNewCategory] = useState(origCategory);
  const [newValue, setNewValue] = useState(parseFloat(origValue).toFixed(2));
  const [fileId, setFileId] = useState(null);
  const [replacePhoto, setReplacePhoto] = useState(false);
  const [image, setImage] = useState(null);
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [loading, setLoading] = useState(true);

  const backQuery = `?date=${date}&time=${time}&category=${origCategory}&value=${origValue}`;

  useEffect(() => {
    Promise.all([
      api.get('/api/categories/'),
      api.get(`/api/bill/?date=${date}&time=${time}&category=${origCategory}&value=${origValue}`),
    ]).then(([catRes, billRes]) => {
      setCategories(catRes.data.categories);
      setFileId(billRes.data.id);
    }).finally(() => setLoading(false));
  }, []);

  const handleReplaceToggle = (e) => {
    setReplacePhoto(e.target.checked);
    if (!e.target.checked) setImage(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    if (replacePhoto && !image) {
      setError('Please select a new photo, or uncheck "Replace photo".');
      return;
    }
    setSubmitting(true);
    const formData = new FormData();
    formData.append('value', newValue);
    formData.append('category', newCategory);
    if (replacePhoto && image) {
      formData.append('image', image);
    }
    try {
      await api.post(
        `/api/bill/clean-edit/?date=${date}&time=${time}&category=${origCategory}&value=${origValue}`,
        formData,
        { headers: { 'Content-Type': 'multipart/form-data' } }
      );
      navigate(`/bill?date=${date}&time=${time}&category=${newCategory}&value=${parseFloat(newValue).toFixed(2)}`);
    } catch (err) {
      setError(err.response?.data?.error || 'Something went wrong.');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <Loader />;

  return (
    <div style={{ ...page, maxWidth: 620 }}>
      {/* Header */}
      <div className="fade-up" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 700, margin: 0 }}>Edit Bill</h2>
        <button className="btn btn-ghost btn-sm" onClick={() => navigate(`/bill${backQuery}`)}>← Back</button>
      </div>

      {/* Current receipt preview */}
      {fileId && (
        <div className="glass-card fade-up" style={{ padding: 0, overflow: 'hidden', marginBottom: '1.25rem' }}>
          <div style={{ padding: '0.6rem 1rem', borderBottom: '1px solid rgba(91,141,239,0.12)', fontSize: '0.78rem', color: '#3949ab', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.06em' }}>
            Current receipt
          </div>
          <iframe
            title="receipt preview"
            src={`https://drive.google.com/file/d/${fileId}/preview`}
            style={{ width: '100%', height: 320, border: 'none', display: 'block' }}
            allow="autoplay"
          />
        </div>
      )}

      {/* Edit form */}
      <div className="glass-card fade-up" style={{ ...glassCard }}>
        <form onSubmit={handleSubmit} style={form}>
          <div>
            <label style={fieldLabel}>Category</label>
            <select value={newCategory} onChange={e => setNewCategory(e.target.value)}>
              {categories.map(cat => (
                <option key={cat.uuid} value={cat.name}>{cat.name}</option>
              ))}
            </select>
          </div>

          <div>
            <label style={fieldLabel}>Amount (£)</label>
            <input
              type="number"
              step="0.01"
              min="0"
              value={newValue}
              onChange={e => setNewValue(e.target.value)}
              required
            />
          </div>

          {/* Replace photo toggle */}
          <div style={{ padding: '1rem', background: 'rgba(91,141,239,0.05)', borderRadius: 12, border: '1px solid rgba(91,141,239,0.12)' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', cursor: 'pointer', marginBottom: replacePhoto ? '1rem' : 0 }}>
              <input type="checkbox" checked={replacePhoto} onChange={handleReplaceToggle} />
              <span style={{ fontWeight: 500, fontSize: '0.9rem' }}>Replace photo</span>
            </label>

            {replacePhoto && (
              <div>
                <label style={fieldLabel}>New photo</label>
                <input
                  type="file"
                  accept="image/*"
                  onChange={e => setImage(e.target.files[0])}
                />
              </div>
            )}
          </div>

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
                Saving…
              </span>
            ) : '💾 Save Changes'}
          </button>
        </form>
      </div>
    </div>
  );
}
