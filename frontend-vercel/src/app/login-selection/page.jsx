'use client';

import { useEffect, useState } from 'react';

const roleData = {
  owner: {
    icon: '👑',
    desc: 'Full control over the entire MultiStock ecosystem.',
    access: [
      'System settings & configurations',
      'Automation workflows',
      'All warehouses & suppliers',
      'User roles & permissions',
      'Advanced analytics & reports',
    ],
  },
  partner: {
    icon: '🤝',
    desc: 'Manages operations, procurement, orders, suppliers, finances, and departments.',
    access: [
      'Inventory management',
      'Order controls & approvals',
      'Workflow management',
      'Financial reporting',
      'Marketplace operations',
    ],
  },
  subadmin: {
    icon: '🟡',
    desc: 'Handles daily warehouse and rental operations.',
    access: [
      'Rental management',
      'Locker operations',
      'Order processing',
      'Task tracking',
      'Team coordination',
    ],
  },
  employee: {
    icon: '👤',
    desc: 'Executes assigned tasks with guided workflows.',
    access: [
      'Check-ins & checkouts',
      'Barcode scanning',
      'Storage logs',
      'Task assignments',
      'Basic reporting',
    ],
  },
};

export default function LoginSelectionPage() {
  const [theme, setTheme] = useState('light');
  const [role, setRole] = useState('');

  useEffect(() => {
    const savedTheme = localStorage.getItem('theme') || 'light';
    setTheme(savedTheme);
    document.documentElement.setAttribute('data-theme', savedTheme);
  }, []);

  function toggleTheme() {
    const next = theme === 'dark' ? 'light' : 'dark';
    setTheme(next);
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('theme', next);
  }

  function continueToTeamLogin() {
    if (!role) return;
    localStorage.setItem('selectedRole', role);
    window.location.href = '/team-login';
  }

  function guestAccess() {
    window.location.href = '/';
  }

  const selected = role ? roleData[role] : null;

  return (
    <>
      <style>{`
        :root {
          --bg-primary: #0014A8;
          --bg-secondary: #000E75;
          --card-bg: rgba(255, 255, 255, 0.95);
          --text-primary: #1f2937;
          --text-secondary: #6b7280;
        }
        [data-theme='dark'] {
          --bg-primary: #1a1a2e;
          --bg-secondary: #16213e;
          --card-bg: rgba(30, 30, 46, 0.95);
          --text-primary: #e9ecef;
          --text-secondary: #adb5bd;
        }
        .ls-page * { box-sizing: border-box; }
        .ls-page {
          min-height: 100vh;
          background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
          position: relative;
          overflow-x: hidden;
        }
        .ls-page::before {
          content: '';
          position: fixed;
          inset: 0;
          background:
            radial-gradient(circle at 20% 50%, rgba(255,255,255,0.1) 0%, transparent 50%),
            radial-gradient(circle at 80% 80%, rgba(255,255,255,0.1) 0%, transparent 50%);
          pointer-events: none;
        }
        .floating-shape {
          position: fixed;
          border-radius: 50%;
          opacity: 0.1;
          animation: float 20s infinite ease-in-out;
          pointer-events: none;
        }
        .shape1 { width: 300px; height: 300px; background: #fff; top: 10%; left: 5%; animation-delay: 0s; }
        .shape2 { width: 200px; height: 200px; background: #fff; top: 60%; right: 10%; animation-delay: 5s; }
        .shape3 { width: 150px; height: 150px; background: #fff; bottom: 10%; left: 15%; animation-delay: 10s; }
        @keyframes float {
          0%,100% { transform: translate(0,0) rotate(0deg); }
          25% { transform: translate(30px,-30px) rotate(90deg); }
          50% { transform: translate(-20px,-50px) rotate(180deg); }
          75% { transform: translate(-30px,20px) rotate(270deg); }
        }
        .ls-wrap { position: relative; z-index: 1; }
        .ls-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 1.5rem 2rem;
          background: rgba(255,255,255,0.1);
          backdrop-filter: blur(10px);
          border-bottom: 1px solid rgba(255,255,255,0.2);
        }
        .logo { display: flex; align-items: center; gap: 10px; color: #fff; font-size: 1.8rem; font-weight: 700; }
        .theme-btn {
          background: rgba(255,255,255,0.2);
          border: 1px solid rgba(255,255,255,0.3);
          color: #fff;
          border-radius: 8px;
          padding: 0.5rem 1rem;
          cursor: pointer;
        }
        .hero { color:#fff; text-align:center; padding: 3rem 1rem 2rem; }
        .hero h1 { font-size: 3rem; margin: 0 0 1rem; }
        .hero h2 { font-size: 1.4rem; font-weight: 400; opacity: 0.95; margin: 0 0 1rem; }
        .hero p { max-width: 800px; margin: 0 auto; opacity: 0.9; }
        .roles-grid {
          max-width: 1600px;
          margin: 0 auto;
          padding: 2rem;
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
          gap: 1.5rem;
        }
        .role-card {
          background: var(--card-bg);
          border-radius: 20px;
          padding: 2rem;
          backdrop-filter: blur(20px);
          border: 1px solid rgba(255,255,255,0.3);
          box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }
        .role-icon { font-size: 3rem; margin-bottom: 1rem; }
        .role-title { font-size: 1.5rem; font-weight: 700; color: var(--text-primary); margin: 0 0 0.5rem; }
        .role-desc { color: var(--text-secondary); margin: 0 0 1rem; }
        .role-access { background: rgba(0,20,168,0.1); border-radius: 10px; padding: 1rem; margin-bottom: 1rem; }
        .role-access h4 { font-size: 0.9rem; margin: 0 0 0.5rem; color: var(--text-primary); }
        .role-access ul { margin: 0; padding-left: 1rem; color: var(--text-secondary); }
        .role-btn {
          width: 100%;
          border: none;
          border-radius: 12px;
          padding: 1rem;
          cursor: pointer;
          font-weight: 600;
          color: #fff;
          background: linear-gradient(135deg, #0014A8, #000E75);
        }
        .role-dropdown {
          width: 100%;
          border: 2px solid rgba(0,20,168,0.3);
          border-radius: 10px;
          padding: 0.8rem;
          margin-bottom: 1rem;
          font-weight: 600;
          color: var(--text-primary);
          background: rgba(255,255,255,0.6);
        }
        .social-login { text-align:center; padding: 2rem; color: #fff; }
        .social-btns { display:flex; justify-content:center; gap:1rem; flex-wrap:wrap; }
        .social-btn { border:none; border-radius:10px; background:#fff; padding:0.8rem 1.5rem; font-weight:600; }
        .tagline {
          max-width: 900px;
          margin: 0 auto;
          text-align: center;
          color: #fff;
          padding: 2rem;
          border-top: 1px solid rgba(255,255,255,0.2);
          border-bottom: 1px solid rgba(255,255,255,0.2);
        }
        .footer { text-align: center; color:#fff; padding: 2rem; background: rgba(0,0,0,0.3); margin-top: 2rem; }
        .footer-links { display:flex; justify-content:center; gap: 2rem; flex-wrap:wrap; margin-bottom: 1rem; }
        .footer-links a { color:#fff; text-decoration:none; opacity:0.8; }
        @media (max-width: 768px) {
          .hero h1 { font-size: 2rem; }
          .ls-header { flex-direction: column; gap: 1rem; }
          .roles-grid { padding: 1rem; }
        }
      `}</style>

      <div className="ls-page">
        <div className="floating-shape shape1"></div>
        <div className="floating-shape shape2"></div>
        <div className="floating-shape shape3"></div>

        <div className="ls-wrap">
          <header className="ls-header">
            <div className="logo">
              <svg width="48" height="48" viewBox="0 0 512 512" fill="#fff">
                <path d="M234.5 5.7c13.9-5 29.1-5 43.1 0l192 68.6C495 83.4 512 107.5 512 134.6V377.4c0 27-17 51.2-42.5 60.3l-192 68.6c-13.9 5-29.1 5-43.1 0l-192-68.6C17 428.6 0 404.5 0 377.4V134.6c0-27 17-51.2 42.5-60.3l192-68.6zM256 66L82.3 128 256 190l173.7-62L256 66zm32 368.6l160-57.1v-188L288 246.6v188z" />
              </svg>
              MultiStock
            </div>
            <button className="theme-btn" onClick={toggleTheme}>
              <i className={`fas ${theme === 'dark' ? 'fa-sun' : 'fa-moon'}`}></i>
            </button>
          </header>

          <section className="hero">
            <h1>Welcome to MultiStock</h1>
            <h2>Choose your login path. Your experience is customized based on your access level.</h2>
            <p>MultiStock uses a secure RBAC system to personalize dashboards and workflows for every user.</p>
          </section>

          <div className="roles-grid">
            <div className="role-card">
              <div className="role-icon">{selected?.icon || '👥'}</div>
              <h3 className="role-title">Team Login</h3>
              <p className="role-desc">{selected?.desc || 'Access for staff, managers, and administrators.'}</p>

              <label style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--text-primary)', display: 'block', marginBottom: '0.5rem' }}>
                Select Your Role:
              </label>
              <select className="role-dropdown" value={role} onChange={(e) => setRole(e.target.value)}>
                <option value="" disabled>-- Select your role --</option>
                <option value="owner">👑 Owner (SuperAdmin)</option>
                <option value="partner">🤝 Admin (Partner/Manager)</option>
                <option value="subadmin">🟡 SubAdmin (Supervisor/SeniorStaff)</option>
                <option value="employee">👤 Employee (Staff)</option>
              </select>

              <div className="role-access">
                <h4>Access Includes:</h4>
                <ul>
                  {selected ? (
                    selected.access.map((a) => <li key={a}>{a}</li>)
                  ) : (
                    <li style={{ fontStyle: 'italic' }}>Select a role to view access permissions</li>
                  )}
                </ul>
              </div>

              <button className="role-btn" onClick={continueToTeamLogin} disabled={!role} style={!role ? { opacity: 0.5, cursor: 'not-allowed' } : {}}>
                Continue as {role ? role.charAt(0).toUpperCase() + role.slice(1) : 'Team Member'} <i className="fas fa-arrow-right"></i>
              </button>
            </div>

            <div className="role-card" onClick={() => (window.location.href = '/customer-login')}>
              <div className="role-icon">🛒</div>
              <h3 className="role-title">Customer Login</h3>
              <p className="role-desc">For customers exploring rentals, storage units, lockers, marketplace & auctions.</p>
              <div className="role-access">
                <h4>Access Includes:</h4>
                <ul>
                  <li>Browse & order products</li>
                  <li>Rental bookings</li>
                  <li>Storage unit reservations</li>
                  <li>Auction participation</li>
                  <li>Subscription plans & coupons</li>
                </ul>
              </div>
              <button className="role-btn">Continue as Customer <i className="fas fa-arrow-right"></i></button>
            </div>

            <div className="role-card" onClick={() => (window.location.href = '#')}>
              <div className="role-icon">✨</div>
              <h3 className="role-title">New User</h3>
              <p className="role-desc">Create a new account to get started with MultiStock.</p>
              <div className="role-access">
                <h4>Registration Includes:</h4>
                <ul>
                  <li>Role selection options</li>
                  <li>Secure onboarding flow</li>
                  <li>Email verification</li>
                  <li>Instant account activation</li>
                  <li>Quick setup process</li>
                </ul>
              </div>
              <button className="role-btn" style={{ background: 'linear-gradient(135deg,#10b981,#059669)' }}>Create New Account <i className="fas fa-arrow-right"></i></button>
            </div>

            <div className="role-card" onClick={guestAccess}>
              <div className="role-icon">🌍</div>
              <h3 className="role-title">Browse as Guest</h3>
              <p className="role-desc">Explore our platform without creating an account.</p>
              <div className="role-access">
                <h4>Guest Access Includes:</h4>
                <ul>
                  <li>Browse marketplace & products</li>
                  <li>View live auctions</li>
                  <li>Read community forums</li>
                  <li>Access analytics dashboard</li>
                  <li>View inventory catalog</li>
                </ul>
              </div>
              <button className="role-btn" style={{ background: 'linear-gradient(135deg,#10b981,#059669)' }}>Continue as Guest <i className="fas fa-arrow-right"></i></button>
            </div>
          </div>

          <section className="social-login">
            <h3>Or continue with</h3>
            <div className="social-btns">
              <button className="social-btn"><i className="fab fa-google" style={{ color: '#DB4437' }}></i> Google</button>
              <button className="social-btn"><i className="fab fa-microsoft" style={{ color: '#00A4EF' }}></i> Microsoft</button>
              <button className="social-btn"><i className="fab fa-linkedin" style={{ color: '#0077B5' }}></i> LinkedIn</button>
            </div>
          </section>

          <section className="tagline">
            <h3 style={{ fontSize: '2rem', marginBottom: '1rem' }}>Logistics Made Simple</h3>
            <p style={{ margin: 0 }}>Powering modern inventory, rentals, storage, and warehouse operations for 10,000+ businesses.</p>
          </section>

          <footer className="footer">
            <div className="footer-links">
              <a href="#">Terms of Service</a>
              <a href="#">Privacy Policy</a>
              <a href="#">Help & Support</a>
              <a href="#">Contact</a>
            </div>
            <p style={{ margin: 0 }}>MultiStock v2.0 © 2025 - Enterprise Inventory & Marketplace Platform</p>
          </footer>
        </div>
      </div>
    </>
  );
}
