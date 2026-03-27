'use client';

export default function CheckoutPage() {
  return (
    <div className="container-fluid p-4 mt-5">
      <div className="alert alert-warning text-center mb-4">
        <i className="fas fa-lock me-2"></i>
        <strong>Login Required:</strong> Please <a href="#" className="alert-link">login</a> to proceed with checkout.
      </div>

      <div className="text-center py-5">
        <i className="fas fa-lock fa-4x mb-3" style={{ color: 'rgba(255,255,255,0.3)', display: 'block' }}></i>
        <h3 style={{ color: '#fff' }}>Checkout requires authentication</h3>
        <p style={{ color: 'rgba(255,255,255,0.7)' }}>Please login or register to complete your purchase.</p>
        <div className="d-flex gap-3 justify-content-center mt-4">
          <a href="#" className="btn-cta btn-cta-primary">
            <i className="fas fa-user-plus"></i> Create Account
          </a>
          <a href="#" className="btn-cta btn-cta-secondary">
            <i className="fas fa-sign-in-alt"></i> Sign In
          </a>
        </div>
      </div>
    </div>
  );
}
