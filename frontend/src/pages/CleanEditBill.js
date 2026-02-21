import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate, Link } from 'react-router-dom';
import api from '../api';

export default function CleanEditBill() {
  const location = useLocation();
  const params = new URLSearchParams(location.search);
  const date = params.get('date');
  const time = params.get('time');
  const category = params.get('category');
  const value = params.get('value');

  const [image, setImage] = useState(null);
  const [newValue, setNewValue] = useState(parseFloat(value).toFixed(2));
  const [newCategory, setNewCategory] = useState(category);
  const [categories, setCategories] = useState([]);
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    api.get('/api/categories/').then(res => setCategories(res.data.categories));
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    if (!image) { setError('Please select an image'); return; }
    setSubmitting(true);
    const formData = new FormData();
    formData.append('image', image);
    formData.append('value', newValue);
    formData.append('category', newCategory);
    try {
      const res = await api.post(
        `/api/bill/clean-edit/?date=${date}&time=${time}&category=${category}&value=${value}`,
        formData,
        { headers: { 'Content-Type': 'multipart/form-data' } }
      );
      const newQuery = `?date=${date}&time=${time}&category=${newCategory}&value=${parseFloat(newValue).toFixed(2)}`;
      navigate(`/bill${newQuery}`);
    } catch (err) {
      setError(err.response?.data?.error || 'Something went wrong');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h2>Replace Receipt</h2>
        <Link to={`/bill?date=${date}&time=${time}&category=${category}&value=${value}`} style={styles.link}>← Back</Link>
      </div>
      <form onSubmit={handleSubmit} style={styles.form}>
        <label style={styles.label}>New image</label>
        <input type="file" accept="image/*" onChange={e => setImage(e.target.files[0])} required />

        <label style={styles.label}>Value (£)</label>
        <input
          style={styles.input}
          type="number"
          step="0.01"
          min="0"
          value={newValue}
          onChange={e => setNewValue(e.target.value)}
          required
        />

        <label style={styles.label}>Category</label>
        <select style={styles.input} value={newCategory} onChange={e => setNewCategory(e.target.value)}>
          {categories.map(cat => (
            <option key={cat.uuid} value={cat.name}>{cat.name}</option>
          ))}
        </select>

        {error && <p style={styles.error}>{error}</p>}
        <button type="submit" style={styles.button} disabled={submitting}>
          {submitting ? 'Uploading…' : 'Save'}
        </button>
      </form>
    </div>
  );
}

const styles = {
  container: { maxWidth: 400, margin: '4rem auto', fontFamily: 'sans-serif', padding: '0 1rem' },
  header: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' },
  link: { color: '#4285F4', textDecoration: 'none' },
  form: { display: 'flex', flexDirection: 'column', gap: '0.75rem' },
  label: { fontWeight: 'bold' },
  input: { padding: '0.5rem', fontSize: '1rem', borderRadius: '4px', border: '1px solid #ccc' },
  button: { padding: '0.6rem', backgroundColor: '#4285F4', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer', fontSize: '1rem' },
  error: { color: 'red' },
};
