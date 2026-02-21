import React from 'react';
import { useLocation, Link } from 'react-router-dom';
import { page, headerRow, pageTitle } from '../theme';

function parseBillName(name) {
  const parts = name.split('_');
  if (parts.length < 4) return { date: '', time: '', category: name, value: '' };
  return {
    category: parts[0],
    date: parts[1],
    time: parts[2],
    value: parseFloat(parts[3]).toFixed(2),
  };
}

export default function ChosenBills() {
  const location = useLocation();
  const bills = location.state?.bills || [];

  const total = bills.reduce((sum, name) => {
    const b = parseBillName(name);
    return sum + parseFloat(b.value || '0');
  }, 0);

  return (
    <div style={page}>
      <div className="fade-up" style={headerRow}>
        <div>
          <h2 style={pageTitle}>Export Results</h2>
          {bills.length > 0 && (
            <p style={{ color: '#5c6bc0', fontSize: '0.85rem', marginTop: '0.2rem' }}>
              {bills.length} {bills.length === 1 ? 'bill' : 'bills'} found
            </p>
          )}
        </div>
        <Link to="/home" className="btn btn-ghost btn-sm">← Home</Link>
      </div>

      {bills.length === 0 ? (
        <div className="glass-card fade-up" style={{ padding: '3rem', textAlign: 'center' }}>
          <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>📭</div>
          <p style={{ color: '#5c6bc0' }}>No bills found for the selected period.</p>
        </div>
      ) : (
        <>
          <div className="glass-card fade-up" style={{ padding: 0, overflow: 'hidden', marginBottom: '1.25rem' }}>
            <table className="dw-table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Time</th>
                  <th>Category</th>
                  <th>Value (£)</th>
                </tr>
              </thead>
              <tbody>
                {bills.map((name, i) => {
                  const b = parseBillName(name);
                  return (
                    <tr key={name} style={{ animationDelay: `${i * 0.035}s`, cursor: 'default' }}>
                      <td>{b.date}</td>
                      <td style={{ color: '#5c6bc0' }}>{b.time}</td>
                      <td>{b.category}</td>
                      <td style={{ fontWeight: 600, color: '#2e7d32' }}>£{b.value}</td>
                    </tr>
                  );
                })}
                <tr className="total-row">
                  <td></td>
                  <td></td>
                  <td>TOTAL</td>
                  <td>£{total.toFixed(2)}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div className="fade-up" style={{ display: 'flex', justifyContent: 'flex-end' }}>
            <a
              href="/api/export/pdf/"
              target="_blank"
              rel="noreferrer"
              className="btn btn-primary"
              style={{ padding: '0.7rem 1.6rem' }}
            >
              📄 Download PDF
            </a>
          </div>
        </>
      )}
    </div>
  );
}
