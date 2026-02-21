/* Shared style constants used across pages */

export const page = {
  position: 'relative',
  zIndex: 1,
  maxWidth: 880,
  margin: '0 auto',
  padding: '2rem 1.5rem',
};

export const narrowPage = {
  position: 'relative',
  zIndex: 1,
  maxWidth: 480,
  margin: '0 auto',
  padding: '3rem 1.5rem',
};

export const glassCard = {
  background: 'rgba(255,255,255,0.82)',
  backdropFilter: 'blur(24px)',
  WebkitBackdropFilter: 'blur(24px)',
  border: '1px solid rgba(180,200,255,0.35)',
  borderRadius: 18,
  padding: '2rem',
  boxShadow: '0 4px 24px rgba(91,141,239,0.10)',
};

export const headerRow = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  marginBottom: '1.75rem',
};

export const pageTitle = {
  fontSize: '1.55rem',
  fontWeight: 700,
  letterSpacing: '-0.01em',
  margin: 0,
};

export const form = {
  display: 'flex',
  flexDirection: 'column',
  gap: '1.1rem',
};

export const fieldLabel = {
  display: 'block',
  fontSize: '0.78rem',
  fontWeight: 600,
  color: '#3949ab',
  textTransform: 'uppercase',
  letterSpacing: '0.07em',
  marginBottom: '0.35rem',
};

export const Loader = () => (
  <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh', zIndex: 1, position: 'relative' }}>
    <div className="spinner" />
  </div>
);
