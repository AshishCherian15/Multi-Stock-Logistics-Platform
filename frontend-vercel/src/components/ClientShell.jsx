'use client';

import { usePathname } from 'next/navigation';

const authRoutes = ['/login-selection', '/team-login', '/customer-login'];

export default function ClientShell({ children }) {
  const pathname = usePathname() || '';
  const isAuthPage = authRoutes.some((route) => pathname.startsWith(route));

  if (isAuthPage) {
    return <>{children}</>;
  }

  return (
    <>
      <div className="bg-particles">
        <div className="particle" style={{ width: 80, height: 80, left: '10%', animationDelay: '0s' }} />
        <div className="particle" style={{ width: 60, height: 60, left: '25%', animationDelay: '3s' }} />
        <div className="particle" style={{ width: 100, height: 100, left: '40%', animationDelay: '6s' }} />
        <div className="particle" style={{ width: 70, height: 70, left: '60%', animationDelay: '2s' }} />
        <div className="particle" style={{ width: 90, height: 90, left: '75%', animationDelay: '5s' }} />
        <div className="particle" style={{ width: 50, height: 50, left: '85%', animationDelay: '8s' }} />
      </div>

      <nav className="navbar navbar-expand-lg guest-navbar">
        <div className="container">
          <a className="navbar-brand" href="/">
            <i className="fas fa-cube"></i>
            MultiStock
            <span className="guest-badge">GUEST</span>
          </a>

          <button
            className="navbar-toggler"
            type="button"
            data-bs-toggle="collapse"
            data-bs-target="#guestNav"
            style={{ background: 'rgba(255,255,255,0.2)', border: '1px solid rgba(255,255,255,0.3)' }}
          >
            <i className="fas fa-bars text-white"></i>
          </button>

          <div className="collapse navbar-collapse" id="guestNav">
            <ul className="navbar-nav me-auto mb-2 mb-lg-0">
              <li className="nav-item"><a className="nav-link" href="/"><i className="fas fa-home me-1"></i> Dashboard</a></li>
              <li className="nav-item"><a className="nav-link" href="/products"><i className="fas fa-store me-1"></i> Marketplace</a></li>
              <li className="nav-item"><a className="nav-link" href="/rentals"><i className="fas fa-key me-1"></i> Rentals</a></li>
              <li className="nav-item"><a className="nav-link" href="/storage"><i className="fas fa-warehouse me-1"></i> Storage</a></li>
              <li className="nav-item"><a className="nav-link" href="/lockers"><i className="fas fa-box me-1"></i> Lockers</a></li>
              <li className="nav-item"><a className="nav-link" href="#"><i className="fas fa-comments me-1"></i> Forums</a></li>
              <li className="nav-item"><a className="nav-link" href="#"><i className="fas fa-info-circle me-1"></i> About</a></li>
            </ul>

            <div className="d-flex gap-2 align-items-center">
              <a href="#" className="btn btn-guest-register"><i className="fas fa-user-plus me-1"></i> Register</a>
              <a href="/login-selection" className="btn btn-guest-login"><i className="fas fa-sign-in-alt me-1"></i> Login</a>
              <a href="/" className="btn btn-exit-guest"><i className="fas fa-sign-out-alt me-1"></i> Exit</a>
            </div>
          </div>
        </div>
      </nav>

      <div className="main-content">{children}</div>

      <footer className="guest-footer">
        <div className="container">
          <div className="row">
            <div className="col-md-4 mb-4">
              <h5><i className="fas fa-cube me-2"></i>MultiStock</h5>
              <p className="mb-3">Enterprise-grade inventory management and marketplace platform for modern businesses.</p>
              <div className="social-links">
                <a href="#" className="me-3"><i className="fab fa-facebook fa-lg"></i></a>
                <a href="#" className="me-3"><i className="fab fa-twitter fa-lg"></i></a>
                <a href="#" className="me-3"><i className="fab fa-linkedin fa-lg"></i></a>
                <a href="#"><i className="fab fa-instagram fa-lg"></i></a>
              </div>
            </div>
            <div className="col-md-2 mb-4">
              <h5>Explore</h5>
              <ul className="list-unstyled">
                <li className="mb-2"><a href="/products"><i className="fas fa-chevron-right me-2"></i>Marketplace</a></li>
                <li className="mb-2"><a href="#"><i className="fas fa-chevron-right me-2"></i>Forums</a></li>
                <li className="mb-2"><a href="#"><i className="fas fa-chevron-right me-2"></i>About Us</a></li>
              </ul>
            </div>
            <div className="col-md-3 mb-4">
              <h5>Quick Links</h5>
              <ul className="list-unstyled">
                <li className="mb-2"><a href="#"><i className="fas fa-user-plus me-2"></i>Create Account</a></li>
                <li className="mb-2"><a href="/login-selection"><i className="fas fa-sign-in-alt me-2"></i>Login</a></li>
                <li className="mb-2"><a href="#"><i className="fas fa-file-contract me-2"></i>Terms of Service</a></li>
                <li className="mb-2"><a href="#"><i className="fas fa-shield-alt me-2"></i>Privacy Policy</a></li>
              </ul>
            </div>
            <div className="col-md-3 mb-4">
              <h5>Contact</h5>
              <ul className="list-unstyled">
                <li className="mb-2"><i className="fas fa-envelope me-2"></i>support@multistock.com</li>
                <li className="mb-2"><i className="fas fa-phone me-2"></i>+1 (555) 123-4567</li>
                <li className="mb-2"><i className="fas fa-map-marker-alt me-2"></i>123 Business St, City</li>
              </ul>
            </div>
          </div>
          <div className="footer-bottom">
            <p className="mb-0">&copy; 2025 MultiStock. All rights reserved. | Guest Mode - Limited Access</p>
            <small>Register for full access to all premium features!</small>
          </div>
        </div>
      </footer>
    </>
  );
}
