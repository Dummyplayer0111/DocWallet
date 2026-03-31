import React from 'react';

const ORBS = [
  { w: 500, h: 500, top: '-20%', left: '-10%', color: 'rgba(91,141,239,0.18)', dur: '18s', delay: '0s' },
  { w: 400, h: 400, bottom: '-15%', right: '-8%', color: 'rgba(155,116,247,0.18)', dur: '22s', delay: '3s' },
  { w: 280, h: 280, top: '45%', left: '35%', color: 'rgba(91,141,239,0.10)', dur: '14s', delay: '6s' },
];

export default function SignIn() {
  return (
    <div style={s.page}>
      {ORBS.map((o, i) => (
        <div key={i} style={{
          position: 'fixed', borderRadius: '50%', pointerEvents: 'none', zIndex: 0,
          width: o.w, height: o.h, top: o.top, left: o.left, right: o.right, bottom: o.bottom,
          background: `radial-gradient(circle, ${o.color} 0%, transparent 70%)`,
          filter: 'blur(50px)',
          animation: `orbA ${o.dur} ease-in-out ${o.delay} infinite`,
        }} />
      ))}

      <div className="glass-card fade-up" style={s.card}>
        <div style={s.icon}>💳</div>
        <h1 style={s.title}>
          Doc<span className="grad-text">Wallet</span>
        </h1>
        <p style={s.subtitle}>Your personal bill manager</p>

        <a href="https://dummyplayer0111.pythonanywhere.com//oauth2-start/" style={s.btn}>
          <GoogleIcon />
          Sign in with Google
        </a>
      </div>
    </div>
  );
}

function GoogleIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" style={{ flexShrink: 0 }}>
      <path fill="#fff" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
      <path fill="#fff" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
      <path fill="#fff" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
      <path fill="#fff" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
    </svg>
  );
}

const s = {
  page: {
    minHeight: '100vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    position: 'relative',
    overflow: 'hidden',
  },
  card: {
    position: 'relative',
    zIndex: 1,
    padding: '3rem 2.5rem',
    textAlign: 'center',
    width: '90%',
    maxWidth: 380,
    animation: 'fadeUp 0.6s cubic-bezier(0.22,1,0.36,1) both, float 6s ease-in-out 0.7s infinite',
  },
  icon: {
    fontSize: '3.5rem',
    display: 'block',
    marginBottom: '0.6rem',
    filter: 'drop-shadow(0 0 20px rgba(91,141,239,0.5))',
  },
  title: {
    fontSize: '2.8rem',
    fontWeight: 800,
    letterSpacing: '-0.03em',
    marginBottom: '0.4rem',
    color: '#1a237e',
    lineHeight: 1,
  },
  subtitle: {
    color: '#5c6bc0',
    marginBottom: '2.2rem',
    fontSize: '0.95rem',
    fontWeight: 400,
  },
  btn: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '0.6rem',
    padding: '0.9rem 1.6rem',
    background: 'linear-gradient(135deg, #5b8def, #9b74f7)',
    backgroundSize: '200% auto',
    color: '#fff',
    borderRadius: 12,
    textDecoration: 'none',
    fontWeight: 700,
    fontSize: '0.95rem',
    boxShadow: '0 6px 28px rgba(91,141,239,0.40)',
    transition: 'transform 0.2s, box-shadow 0.2s',
    letterSpacing: '0.01em',
  },
};
