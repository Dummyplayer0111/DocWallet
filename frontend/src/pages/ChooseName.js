import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';
import { narrowPage, glassCard, headerRow, pageTitle, form, fieldLabel, Loader } from '../theme';

export default function ChooseName() {
  const [username, setUsername] = useState('');
  const [timezone, setTimezone] = useState('UTC');
  const [timezones, setTimezones] = useState([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    api.get('/api/auth/timezones/')
      .then(res => setTimezones(res.data.timezones))
      .finally(() => setLoading(false));
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      await api.post('/api/choose-name/', { username, timezone });
      navigate('/home');
    } catch (err) {
      setError(err.response?.data?.error || 'Something went wrong');
    }
  };

  if (loading) return <Loader />;

  return (
    <div style={narrowPage}>
      <div className="glass-card fade-up" style={{ ...glassCard, padding: '2.5rem' }}>
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <div style={{ fontSize: '2.5rem', marginBottom: '0.5rem' }}>👋</div>
          <h2 style={{ ...pageTitle, marginBottom: '0.4rem' }}>Set up your account</h2>
          <p style={{ color: '#5c6bc0', fontSize: '0.88rem' }}>Just a couple of details and you're in</p>
        </div>

        <form onSubmit={handleSubmit} style={form}>
          <div>
            <label style={fieldLabel}>Username</label>
            <input
              type="text"
              value={username}
              onChange={e => setUsername(e.target.value)}
              placeholder="Choose a username"
              required
            />
          </div>

          <div>
            <label style={fieldLabel}>Timezone</label>
            <select value={timezone} onChange={e => setTimezone(e.target.value)}>
              {timezones.map(tz => <option key={tz} value={tz}>{tz}</option>)}
            </select>
          </div>

          {error && <div className="form-error">⚠ {error}</div>}

          <button type="submit" className="btn btn-primary" style={{ width: '100%', padding: '0.8rem' }}>
            Continue →
          </button>
        </form>
      </div>
    </div>
  );
}
