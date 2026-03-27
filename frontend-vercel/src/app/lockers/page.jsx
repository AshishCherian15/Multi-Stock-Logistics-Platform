'use client';
import { useState, useEffect } from 'react';
import { loadAllData, filterByModel } from '../../lib/dataLoader';

export default function LockersPage() {
  const [lockers, setLockers] = useState([]);
  const [lockerTypes, setLockerTypes] = useState({});

  useEffect(() => {
    loadAllData().then((data) => {
      const types = filterByModel(data, 'lockers.lockertype');
      const typeMap = {};
      types.forEach((t) => { typeMap[t.id] = t; });
      setLockerTypes(typeMap);
      setLockers(filterByModel(data, 'lockers.locker'));
    });
  }, []);

  const available = lockers.filter((l) => l.status === 'available').length;
  const occupied = lockers.filter((l) => l.status === 'occupied').length;
  const maintenance = lockers.filter((l) => l.status === 'maintenance').length;

  return (
    <div className="container-fluid p-4 mt-5">
      <div className="alert alert-warning text-center mb-4">
        <i className="fas fa-lock me-2"></i>
        <strong>Login Required:</strong> Please <a href="#" className="alert-link">login</a> to book lockers, add to cart, or add to wishlist.
      </div>

      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2 style={{ color: '#fff' }}><i className="fas fa-box me-2"></i>Smart Lockers</h2>
        <a href="#" className="btn btn-primary">
          <i className="fas fa-sign-in-alt me-1"></i>Login
        </a>
      </div>

      {/* Summary Dashboard */}
      <div className="row g-3 mb-4">
        <div className="col-md-3">
          <div className="stats-card">
            <div className="stats-number">{lockers.length}</div>
            <div>Total Lockers</div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="stats-card" style={{ background: 'linear-gradient(135deg, #10b981, #059669)' }}>
            <div className="stats-number">{available}</div>
            <div>Available</div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="stats-card" style={{ background: 'linear-gradient(135deg, #ef4444, #dc2626)' }}>
            <div className="stats-number">{occupied}</div>
            <div>Occupied</div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="stats-card" style={{ background: 'linear-gradient(135deg, #f59e0b, #d97706)' }}>
            <div className="stats-number">{maintenance}</div>
            <div>Maintenance</div>
          </div>
        </div>
      </div>

      {/* Lockers Grid */}
      <div className="row g-4">
        {lockers.map((locker) => {
          const lt = lockerTypes[locker.locker_type] || {};
          return (
            <div key={locker.id} className="col-md-4">
              <div className="card locker-card">
                <div className="locker-header">
                  <span className="status-badge status-available">
                    <i className="fas fa-check-circle me-1"></i>Available
                  </span>
                  <div className="locker-icon">
                    <i className="fas fa-box fa-2x"></i>
                  </div>
                  <div className="locker-number">{locker.locker_number}</div>
                  <small>{lt.size || ''}</small>
                </div>

                <div className="card-body">
                  {/* Locker Type */}
                  <h5 className="mb-3">{lt.name || 'Locker'}</h5>

                  {/* Location */}
                  <div className="mb-3">
                    <div className="d-flex align-items-center mb-2">
                      <i className="fas fa-map-marker-alt text-primary me-2"></i>
                      <span>{locker.location}</span>
                    </div>
                  </div>

                  {/* Features */}
                  <div className="mb-3">
                    {lt.has_climate_control && (
                      <span className="feature-badge">
                        <i className="fas fa-snowflake me-1"></i>Climate Control
                      </span>
                    )}
                    {lt.has_security_monitoring && (
                      <span className="feature-badge">
                        <i className="fas fa-shield-alt me-1"></i>Security Monitored
                      </span>
                    )}
                  </div>

                  {/* Pricing */}
                  <div className="price-box">
                    <div className="price-item">
                      <span>Hourly:</span>
                      <span className="price-value">{'\u20B9'}{lt.hourly_rate || '0'}/hr</span>
                    </div>
                    <div className="price-item">
                      <span>Daily:</span>
                      <span className="price-value">{'\u20B9'}{lt.daily_rate || '0'}/day</span>
                    </div>
                    <div className="price-item">
                      <span>Weekly:</span>
                      <span className="price-value">{'\u20B9'}{lt.weekly_rate || '0'}/week</span>
                    </div>
                    <div className="price-item">
                      <span>Monthly:</span>
                      <span className="price-value">{'\u20B9'}{lt.monthly_rate || '0'}/month</span>
                    </div>
                  </div>
                </div>
                <div className="card-footer bg-white">
                  <a href="#" className="btn btn-primary w-100">
                    <i className="fas fa-sign-in-alt me-1"></i>Login to Book
                  </a>
                </div>
              </div>
            </div>
          );
        })}
        {lockers.length === 0 && (
          <div className="col-12 text-center py-5">
            <i className="fas fa-inbox fa-4x text-muted mb-3" style={{ display: 'block' }}></i>
            <h4 className="text-muted">No lockers available</h4>
          </div>
        )}
      </div>
    </div>
  );
}
