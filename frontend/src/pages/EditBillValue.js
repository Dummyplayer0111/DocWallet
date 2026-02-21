import React, { useState } from 'react';
import { useLocation, useNavigate, Link } from 'react-router-dom';
import api from '../api';

export default function EditBillValue() {
  const location = useLocation();
  const params = new URLSearchParams(location.search);
  const date = params.get('date');
  const time = params.get('time');
  const category = params.get('category');
  const value = params.get('value');

  const [newValue, setNewValue] = useState(parseFloat(value).toFixed(2));
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      const res = await api.patch(
        `/api/bill/?date=${date}&time=${time}&category=${category}&value=${value}`,
        { value: parseFloat(newValue) }
      );
      const newQuery = `?date=${date}&time=${time}&category=${category}&value=${parseFloat(newValue).toFixed(2)}`;
      navigate(`/bill${newQuery}`);
    } catch (err) {
      setError(err.response?.data?.error || 'Something went wrong');
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h2>Edit Value</h2>
        <Link to={`/bill?date=${date}&time=${time}&category=${category}&value=${value}`} style={styles.link}>← Back</Link>
      </div>
      <form onSubmit={handleSubmit} style={styles.form}>
        <label style={styles.label}>New value (£)</label>
        <input
          style={styles.input}
          type="number"
          step="0.01"
          min="0"
          value={newValue}
          onChange={e => setNewValue(e.target.value)}
          required
        />
        {error && <p style={styles.error}>{error}</p>}
        <button type="submit" style={styles.button}>Save</button>
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
