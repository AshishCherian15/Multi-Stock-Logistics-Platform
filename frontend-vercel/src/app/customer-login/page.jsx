'use client';

import { useState } from 'react';

const demoCustomers = [
  { username: 'customer', password: 'customer123', role: '🟢 Customer', note: 'Marketplace & shopping access' },
  { username: 'customer_arjun', password: 'customer123', role: '🟢 Customer', note: 'Marketplace & shopping access' },
  { username: 'customer_deepika', password: 'customer123', role: '🟢 Customer', note: 'Marketplace & shopping access' },
];

export default function CustomerLoginPage() {
  const [showPassword, setShowPassword] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  function onSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      alert('Frontend demo page only. Use Django backend customer login for real authentication.');
    }, 700);
  }

  return (
    <>
      <style>{`
        .cl-page { min-height: 100vh; background: linear-gradient(135deg,#10b981 0%,#059669 50%,#047857 100%); position: relative; overflow: hidden; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
        .cl-bg { position: fixed; inset: 0; pointer-events: none; }
        .floating-icon { position:absolute; font-size:2.5rem; opacity:.1; animation: floatAround 8s ease-in-out infinite; }
        .icon-1 { top:15%; left:15%; animation-delay:0s; } .icon-2 { top:25%; right:20%; animation-delay:2s; } .icon-3 { bottom:30%; left:25%; animation-delay:4s; } .icon-4 { bottom:20%; right:15%; animation-delay:6s; }
        @keyframes floatAround { 0%,100%{transform:translate(0,0) rotate(0deg)} 25%{transform:translate(20px,-20px) rotate(90deg)} 50%{transform:translate(-10px,-30px) rotate(180deg)} 75%{transform:translate(-20px,10px) rotate(270deg)} }
        .cl-wrap { position: relative; z-index:1; min-height:100vh; display:flex; align-items:center; justify-content:center; padding:2rem 1rem; }
        .login-card { width:100%; max-width:600px; background:rgba(255,255,255,.98); border-radius:25px; padding:3rem; border:2px solid rgba(255,255,255,.4); box-shadow:0 30px 60px rgba(0,0,0,.3); position:relative; }
        .logo-top { position:absolute; top:20px; left:20px; display:flex; align-items:center; gap:8px; font-weight:700; color:#10b981; font-size:1.1rem; }
        .back-link { display:inline-flex; align-items:center; gap:.5rem; color:#6b7280; text-decoration:none; font-size:.9rem; margin-bottom:1.5rem; }
        .header { text-align:center; margin-bottom:2rem; }
        .header .icon { font-size:4rem; margin-bottom:1rem; }
        .header h2 { margin:0 0 .5rem; color:#1f2937; font-size:2.2rem; }
        .header p { margin:0; color:#6b7280; }
        .field { margin-bottom:1rem; }
        .field label { display:block; margin-bottom:.5rem; color:#1f2937; font-weight:600; font-size:.95rem; }
        .input-wrap { position:relative; }
        .input-wrap input { width:100%; height:48px; border:2px solid #e5e7eb; border-radius:8px; background:#f9fafb; padding:0 3rem 0 2.5rem; }
        .input-wrap i.left { position:absolute; left:.875rem; top:50%; transform:translateY(-50%); color:#9ca3af; }
        .pass-toggle { position:absolute; right:.875rem; top:50%; transform:translateY(-50%); border:none; background:none; color:#9ca3af; cursor:pointer; }
        .remember { margin:.75rem 0; display:flex; align-items:center; gap:.5rem; font-size:.95rem; color:#374151; }
        .forgot { text-align:center; margin:1rem 0; }
        .forgot a { color:#6b7280; text-decoration:none; background:rgba(107,114,128,.1); border-radius:20px; padding:.5rem 1rem; }
        .login-btn { width:100%; margin:1.5rem 0; border:none; border-radius:15px; padding:1.1rem; color:#fff; font-size:1.1rem; font-weight:600; background:linear-gradient(135deg,#10b981,#059669,#047857); cursor:pointer; }
        .demo { background:linear-gradient(45deg,#ecfdf5,#d1fae5); border-radius:15px; padding:1.5rem; margin-top:1rem; text-align:center; }
        .demo h6 { margin:0 0 .75rem; color:#047857; }
        .demo-item { padding:1rem; border-radius:12px; border:1px solid #d1fae5; background:#fff; margin-bottom:.5rem; cursor:pointer; transition:all .2s; }
        .demo-item:hover { background:#d1fae5; transform:scale(1.01); }
        .demo-role { font-weight:600; color:#047857; font-size:.9rem; margin-bottom:.25rem; }
        .demo-creds { font-family:monospace; color:#374151; font-size:.85rem; margin-bottom:.25rem; }
        .demo-note { font-size:.75rem; color:#6b7280; font-style:italic; }
        .features { background:linear-gradient(45deg,#f0fdfa,#ccfbf1); border-radius:15px; padding:1.5rem; margin-top:1rem; }
        .features h6 { margin:0 0 .75rem; color:#047857; text-align:center; }
        .feature-grid { display:grid; grid-template-columns:1fr 1fr; gap:.75rem; }
        .feature { background:#fff; border:1px solid #a7f3d0; border-radius:10px; padding:.75rem; color:#374151; font-size:.9rem; display:flex; align-items:center; gap:.5rem; }
        @media (max-width:768px){ .login-card{padding:2rem;} .header h2{font-size:1.5rem;} .feature-grid{grid-template-columns:1fr;} }
      `}</style>

      <div className="cl-page">
        <div className="cl-bg">
          <div className="floating-icon icon-1">🛒</div>
          <div className="floating-icon icon-2">🏪</div>
          <div className="floating-icon icon-3">📋</div>
          <div className="floating-icon icon-4">🎯</div>
        </div>

        <div className="cl-wrap">
          <div className="login-card">
            <div className="logo-top">
              <svg width="32" height="32" viewBox="0 0 512 512" fill="#10b981"><path d="M234.5 5.7c13.9-5 29.1-5 43.1 0l192 68.6C495 83.4 512 107.5 512 134.6V377.4c0 27-17 51.2-42.5 60.3l-192 68.6c-13.9 5-29.1 5-43.1 0l-192-68.6C17 428.6 0 404.5 0 377.4V134.6c0-27 17-51.2 42.5-60.3l192-68.6zM256 66L82.3 128 256 190l173.7-62L256 66zm32 368.6l160-57.1v-188L288 246.6v188z"/></svg>
              <span>MultiStock</span>
            </div>

            <form onSubmit={onSubmit}>
              <a href="/login-selection" className="back-link"><i className="fas fa-arrow-left"></i> Back to Login Options</a>

              <div className="header">
                <div className="icon">🛒</div>
                <h2>Customer Portal 🏪</h2>
                <p>Marketplace & Shopping Access</p>
              </div>

              <div className="field">
                <label htmlFor="id_username">Username or Email</label>
                <div className="input-wrap">
                  <i className="fas fa-user left"></i>
                  <input id="id_username" value={username} onChange={(e) => setUsername(e.target.value)} placeholder="Enter your username or email" required />
                </div>
              </div>

              <div className="field">
                <label htmlFor="id_password">Password</label>
                <div className="input-wrap">
                  <i className="fas fa-lock left"></i>
                  <input id="id_password" type={showPassword ? 'text' : 'password'} value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Enter your password" required />
                  <button type="button" className="pass-toggle" onClick={() => setShowPassword((s) => !s)}>
                    <i className={`fas ${showPassword ? 'fa-eye-slash' : 'fa-eye'}`}></i>
                  </button>
                </div>
              </div>

              <label className="remember"><input type="checkbox" /> Remember Me</label>
              <div className="forgot"><a href="#"><i className="fas fa-key"></i> Forgot Password?</a></div>

              <button className="login-btn" disabled={loading} type="submit">
                {loading ? <><i className="fas fa-spinner fa-spin"></i> Entering...</> : <><i className="fas fa-shopping-cart"></i> Enter Marketplace <i className="fas fa-arrow-right"></i></>}
              </button>
            </form>

            <div className="demo">
              <h6>🎁 Demo Accounts</h6>
              {demoCustomers.map((a) => (
                <div key={a.username} className="demo-item" onClick={() => { setUsername(a.username); setPassword(a.password); }}>
                  <div className="demo-role">{a.role}</div>
                  <div className="demo-creds">{a.username} / {a.password}</div>
                  <div className="demo-note">{a.note}</div>
                </div>
              ))}
              <div style={{ marginTop: '1rem', padding: '.5rem', background: 'rgba(16,185,129,0.1)', borderRadius: '8px', fontSize: '.85rem', color: '#047857' }}>
                <strong>Plus 46+ more customer accounts</strong><br />
                <small>All with password: customer123</small>
              </div>
            </div>

            <div className="features">
              <h6>🌟 What you can do:</h6>
              <div className="feature-grid">
                <div className="feature"><span>🛍</span> View Items</div>
                <div className="feature"><span>🎯</span> Place Bids</div>
                <div className="feature"><span>🏆</span> Win Auctions</div>
                <div className="feature"><span>💬</span> Forums</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
