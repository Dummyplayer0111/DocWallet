import React, { useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import api from '../api';
import { narrowPage, glassCard, headerRow, pageTitle, form, fieldLabel } from '../theme';

export default function NewBill() {
  const { uuid } = useParams();
  const [image, setImage] = useState(null);
  const [value, setValue] = useState('');
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    if (!image) { setError('Please select an image'); return; }
    setSubmitting(true);
    const formData = new FormData();
    formData.append('image', image);
    formData.append('value', value);
    try {
      await api.post(`/api/bills/${uuid}/`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      navigate('/home');
    } catch (err) {
      setError(err.response?.data?.error || 'Upload failed');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div style={narrowPage}>
      <div className="glass-card fade-up" style={glassCard}>
        <div style={headerRow}>
          <h2 style={pageTitle}>Add Bill</h2>
          <Link to={`/category/${uuid}`} className="btn btn-ghost btn-sm">← Back</Link>
        </div>

        <form onSubmit={handleSubmit} style={form}>
          <div>
            <label style={fieldLabel}>Receipt photo</label>
            <input
              type="file"
              accept="image/*"
              onChange={e => setImage(e.target.files[0])}
              required
            />
            {image && (
              <div style={{ marginTop: '0.75rem', position: 'relative' }}>
                <img
                  src={URL.createObjectURL(image)}
                  alt="preview"
                  style={{ width: '100%', maxHeight: 220, objectFit: 'cover', borderRadius: 10, opacity: 0.9 }}
                />
                <div style={{
                  position: 'absolute', top: 8, right: 8,
                  background: 'rgba(46,125,50,0.85)', borderRadius: 6,
                  padding: '2px 8px', fontSize: '0.75rem', color: '#fff',
                }}>
                  ✓ Selected
                </div>
              </div>
            )}
          </div>

          <div>
            <label style={fieldLabel}>Amount (£)</label>
            <input
              type="number"
              step="0.01"
              min="0"
              placeholder="0.00"
              value={value}
              onChange={e => setValue(e.target.value)}
              required
            />
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
                Uploading…
              </span>
            ) : '💾 Save Bill'}
          </button>
        </form>
      </div>
    </div>
  );
}
