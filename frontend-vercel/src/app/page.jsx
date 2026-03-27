'use client';
import { useState, useEffect } from 'react';
import { loadAllData, filterByModel } from '../lib/dataLoader';

export default function HomePage() {
  const [productCount, setProductCount] = useState(0);
  const [rentalCount, setRentalCount] = useState(0);
  const [storageCount, setStorageCount] = useState(0);
  const [lockerCount, setLockerCount] = useState(0);

  useEffect(() => {
    loadAllData().then((data) => {
      setProductCount(filterByModel(data, 'goods.listmodel').length);
      setRentalCount(filterByModel(data, 'rentals.rentalitem').length);
      setStorageCount(filterByModel(data, 'storage.storageunit').length);
      setLockerCount(filterByModel(data, 'lockers.locker').length);
    });
  }, []);

  return (
    <div className="container">
      {/* Hero Section */}
      <div className="dashboard-hero">
        <h1><i className="fas fa-rocket me-3"></i>Welcome to MultiStock</h1>
        <p>Explore our enterprise inventory management platform. Browse products and join our community!</p>
      </div>

      {/* Info Banner */}
      <div className="info-banner d-flex align-items-center">
        <i className="fas fa-info-circle"></i>
        <div>
          <strong>You&apos;re in Guest Mode!</strong> Explore with read-only access.{' '}
          <a href="#">Create a free account</a> or{' '}
          <a href="#">sign in</a> to unlock all features.
        </div>
      </div>

      {/* Animated Stat Cards */}
      <div className="stat-cards-grid">
        <a href="/products" className="stat-card">
          <div className="stat-icon">
            <i className="fas fa-store"></i>
          </div>
          <span className="stat-number">{productCount}</span>
          <div className="stat-label">Marketplace Items</div>
          <div className="stat-description">Browse verified products from sellers worldwide</div>
          <i className="fas fa-arrow-right stat-arrow"></i>
        </a>

        <a href="/rentals" className="stat-card">
          <div className="stat-icon">
            <i className="fas fa-key"></i>
          </div>
          <span className="stat-number">{rentalCount}</span>
          <div className="stat-label">Rental Equipment</div>
          <div className="stat-description">Hire professional equipment at competitive rates</div>
          <i className="fas fa-arrow-right stat-arrow"></i>
        </a>

        <a href="/storage" className="stat-card">
          <div className="stat-icon">
            <i className="fas fa-warehouse"></i>
          </div>
          <span className="stat-number">{storageCount}</span>
          <div className="stat-label">Storage Units</div>
          <div className="stat-description">Secure, climate-controlled storage solutions</div>
          <i className="fas fa-arrow-right stat-arrow"></i>
        </a>
      </div>

      {/* Call to Action */}
      <div className="cta-section">
        <h2><i className="fas fa-rocket me-2"></i>Ready to Get Started?</h2>
        <p>Join thousands of businesses using MultiStock for their inventory management needs. Create your free account today!</p>
        <div className="cta-buttons">
          <a href="#" className="btn-cta btn-cta-primary">
            <i className="fas fa-user-plus"></i> Create Free Account
          </a>
          <a href="#" className="btn-cta btn-cta-secondary">
            <i className="fas fa-sign-in-alt"></i> Sign In
          </a>
        </div>
      </div>
    </div>
  );
}
