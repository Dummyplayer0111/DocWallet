import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import api from '../api';
import { Loader } from '../theme';

/* ── Category emoji mapping ── */
function getEmoji(name) {
  const n = name.toLowerCase();
  if (n.includes('food') || n.includes('eat') || n.includes('restaurant') || n.includes('dining')) return '🍕';
  if (n.includes('game') || n.includes('gaming') || n.includes('play'))  return '🎮';
  if (n.includes('cinema') || n.includes('movie') || n.includes('film')) return '🎬';
  if (n.includes('petrol') || n.includes('fuel') || n.includes('gas'))   return '⛽';
  if (n.includes('travel') || n.includes('flight') || n.includes('trip') || n.includes('hotel')) return '✈️';
  if (n.includes('shop') || n.includes('cloth') || n.includes('fashion')) return '🛍️';
  if (n.includes('health') || n.includes('medical') || n.includes('medicine') || n.includes('pharmacy')) return '💊';
  if (n.includes('bill') || n.includes('electric') || n.includes('utility') || n.includes('wifi')) return '💡';
  if (n.includes('rent') || n.includes('home') || n.includes('house') || n.includes('flat')) return '🏠';
  if (n.includes('gym') || n.includes('sport') || n.includes('fitness')) return '💪';
  if (n.includes('book') || n.includes('educat') || n.includes('school') || n.includes('college')) return '📚';
  if (n.includes('car') || n.includes('vehicle') || n.includes('taxi') || n.includes('uber')) return '🚗';
  if (n.includes('subscri') || n.includes('netflix') || n.includes('spotify')) return '📱';
  if (n.includes('coffee') || n.includes('cafe'))  return '☕';
  if (n.includes('grocery') || n.includes('supermarket')) return '🛒';
  return '💼';
}

/* ── 3-D tilt card ── */
function TiltCard({ cat, onClick, delay }) {
  const ref = useRef();
  const [tilt, setTilt] = useState({ x: 0, y: 0 });
  const [hov, setHov] = useState(false);

  const onMove = e => {
    const r = ref.current.getBoundingClientRect();
    const x = ((e.clientY - r.top)  / r.height - 0.5) * -22;
    const y = ((e.clientX - r.left) / r.width  - 0.5) *  22;
    setTilt({ x, y });
  };

  return (
    <div
      ref={ref}
      className="fade-up"
      onClick={onClick}
      onMouseMove={onMove}
      onMouseEnter={() => setHov(true)}
      onMouseLeave={() => { setTilt({ x: 0, y: 0 }); setHov(false); }}
      style={{
        animationDelay: delay,
        background: hov
          ? 'linear-gradient(135deg, rgba(91,141,239,0.18), rgba(155,116,247,0.18))'
          : 'rgba(255,255,255,0.82)',
        backdropFilter: 'blur(24px)',
        WebkitBackdropFilter: 'blur(24px)',
        border: `1px solid ${hov ? 'rgba(91,141,239,0.5)' : 'rgba(180,200,255,0.35)'}`,
        borderRadius: 20,
        padding: '2.5rem 1rem',
        cursor: 'pointer',
        textAlign: 'center',
        transform: `perspective(800px) rotateX(${tilt.x}deg) rotateY(${tilt.y}deg) translateZ(${hov ? '10px' : '0'})`,
        transition: hov
          ? 'background 0.2s, border-color 0.2s, box-shadow 0.2s'
          : 'all 0.5s cubic-bezier(0.22,1,0.36,1)',
        boxShadow: hov
          ? '0 24px 48px rgba(91,141,239,0.28), inset 0 1px 0 rgba(255,255,255,0.9)'
          : '0 4px 20px rgba(91,141,239,0.12), inset 0 1px 0 rgba(255,255,255,0.9)',
        willChange: 'transform',
      }}
    >
      <div style={{
        fontSize: '2.6rem',
        marginBottom: '0.8rem',
        filter: hov ? 'drop-shadow(0 0 12px rgba(91,141,239,0.6))' : 'none',
        transition: 'filter 0.3s',
      }}>
        {getEmoji(cat.name)}
      </div>
      <div style={{
        fontWeight: 600,
        fontSize: '0.95rem',
        color: hov ? '#1a237e' : '#3949ab',
        transition: 'color 0.2s',
        letterSpacing: '0.01em',
      }}>
        {cat.name}
      </div>
    </div>
  );
}

export default function Home() {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const controller = new AbortController();
    api.get('/api/categories/', { signal: controller.signal })
      .then(res => { setCategories(res.data.categories); setLoading(false); })
      .catch(err => { if (err.code !== 'ERR_CANCELED') { navigate('/'); } });
    return () => controller.abort();
  }, [navigate]);

  if (loading) return <Loader />;

  return (
    <div style={{ position: 'relative', zIndex: 1, minHeight: '100vh' }}>
      {/* ── Navbar ── */}
      <nav style={nav.bar}>
        <div style={nav.inner}>
          <span style={nav.logo}>💳 Doc<span className="grad-text">Wallet</span></span>
          <div style={nav.links}>
            <Link to="/home/edit" className="nav-link">Edit categories</Link>
            <Link to="/export" className="nav-link">Export</Link>
            <button className="btn btn-ghost btn-sm" onClick={async () => {
              await api.post('/api/auth/logout/');
              navigate('/');
            }}>
              Logout
            </button>
          </div>
        </div>
      </nav>

      {/* ── Content ── */}
      <div style={{ maxWidth: 900, margin: '0 auto', padding: '2rem 1.5rem' }}>
        <div style={{ marginBottom: '2rem' }} className="fade-up">
          <h1 style={{ fontSize: '1.8rem', fontWeight: 700, marginBottom: '0.3rem' }}>
            Your Categories
          </h1>
          <p style={{ color: '#5c6bc0', fontSize: '0.9rem' }}>
            {categories.length} {categories.length === 1 ? 'category' : 'categories'} — tap one to view bills
          </p>
        </div>

        {categories.length === 0 ? (
          <div className="glass-card fade-up" style={{ padding: '3rem', textAlign: 'center' }}>
            <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>📂</div>
            <p style={{ color: '#5c6bc0', marginBottom: '1.5rem' }}>No categories yet.</p>
            <Link to="/home/edit" className="btn btn-primary">Create one</Link>
          </div>
        ) : (
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(160px, 1fr))',
            gap: '1.25rem',
          }}>
            {categories.map((cat, i) => (
              <TiltCard
                key={cat.uuid}
                cat={cat}
                onClick={() => navigate(`/category/${cat.uuid}`)}
                delay={`${i * 0.07}s`}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

const nav = {
  bar: {
    position: 'sticky',
    top: 0,
    zIndex: 100,
    background: 'rgba(255,255,255,0.88)',
    backdropFilter: 'blur(20px)',
    WebkitBackdropFilter: 'blur(20px)',
    borderBottom: '1px solid rgba(91,141,239,0.18)',
    boxShadow: '0 2px 16px rgba(91,141,239,0.08)',
  },
  inner: {
    maxWidth: 900,
    margin: '0 auto',
    padding: '0.9rem 1.5rem',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  logo: {
    fontSize: '1.15rem',
    fontWeight: 800,
    letterSpacing: '-0.01em',
    color: '#1a237e',
  },
  links: {
    display: 'flex',
    alignItems: 'center',
    gap: '1.25rem',
  },
};
