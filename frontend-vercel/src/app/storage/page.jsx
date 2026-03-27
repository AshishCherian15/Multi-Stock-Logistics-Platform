'use client';
import { useState, useEffect } from 'react';
import { loadAllData, filterByModel } from '../../lib/dataLoader';

export default function StoragePage() {
  const [units, setUnits] = useState([]);

  useEffect(() => {
    loadAllData().then((data) => {
      setUnits(filterByModel(data, 'storage.storageunit'));
    });
  }, []);

  const available = units.filter((u) => u.status === 'available').length;
  const occupied = units.filter((u) => u.status === 'occupied').length;
  const maintenance = units.filter((u) => u.status === 'maintenance').length;

  return (
    <div className="container-fluid p-4 mt-5">
      <div className="alert alert-warning text-center mb-4">
        <i className="fas fa-lock me-2"></i>
        <strong>Login Required:</strong> Please <a href="#" className="alert-link">login</a> to book storage units, add to cart, or add to wishlist.
      </div>

      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2 style={{ color: '#fff' }}><i className="fas fa-warehouse me-2"></i>Storage Units</h2>
        <a href="#" className="btn btn-primary">
          <i className="fas fa-sign-in-alt me-1"></i>Login
        </a>
      </div>

      {/* Summary Dashboard */}
      <div className="row g-3 mb-4">
        <div className="col-md-3">
          <div className="stats-card">
            <div className="stats-number">{units.length}</div>
            <div>Total Units</div>
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

      {/* Storage Units Grid */}
      <div className="row g-4">
        {units.map((unit) => (
          <div key={unit.id} className="col-md-4">
            <div className="card storage-card">
              <div className="unit-header">
                <h3 className="mb-0">Unit {unit.unit_number}</h3>
                <small>{unit.type}</small>
              </div>

              <div className="card-body">
                {/* Status */}
                <div className="text-center mb-3">
                  <span className={`status-badge status-${unit.status === 'available' ? 'available' : unit.status === 'maintenance' ? 'maintenance' : 'booked'}`}>
                    <i className={`fas fa-${unit.status === 'available' ? 'check-circle' : unit.status === 'maintenance' ? 'wrench' : 'times-circle'} me-1`}></i>
                    {unit.status.charAt(0).toUpperCase() + unit.status.slice(1)}
                  </span>
                </div>

                {/* Details */}
                <div className="mb-3">
                  <div className="d-flex justify-content-between mb-2">
                    <span><i className="fas fa-map-marker-alt text-primary me-2"></i>Location:</span>
                    <strong>{unit.location}</strong>
                  </div>
                  <div className="d-flex justify-content-between mb-2">
                    <span><i className="fas fa-building text-primary me-2"></i>Floor:</span>
                    <strong>{unit.floor}</strong>
                  </div>
                  <div className="d-flex justify-content-between mb-2">
                    <span><i className="fas fa-ruler-combined text-primary me-2"></i>Size:</span>
                    <strong>{unit.size_sqft} sq ft</strong>
                  </div>
                  <div className="d-flex justify-content-between mb-2">
                    <span><i className="fas fa-map-signs text-primary me-2"></i>Zone:</span>
                    <strong>{unit.zone}</strong>
                  </div>
                </div>

                {/* Features */}
                {unit.is_climate_controlled && (
                  <div className="mb-3 text-center">
                    <span className="badge bg-info">
                      <i className="fas fa-snowflake me-1"></i>Climate Controlled
                    </span>
                  </div>
                )}

                {/* Price */}
                <div className="text-center mb-3">
                  <div style={{ fontSize: '2rem', fontWeight: 700, color: 'var(--zaffre)' }}>{'\u20B9'}{unit.price_per_month}</div>
                  <small className="text-muted">per month</small>
                </div>
              </div>
              <div className="card-footer bg-white">
                <a href="#" className="btn btn-primary w-100">
                  <i className="fas fa-sign-in-alt me-1"></i>Login to Book
                </a>
              </div>
            </div>
          </div>
        ))}
        {units.length === 0 && (
          <div className="col-12 text-center py-5">
            <i className="fas fa-inbox fa-4x text-muted mb-3" style={{ display: 'block' }}></i>
            <h4 className="text-muted">No storage units available</h4>
          </div>
        )}
      </div>
    </div>
  );
}
