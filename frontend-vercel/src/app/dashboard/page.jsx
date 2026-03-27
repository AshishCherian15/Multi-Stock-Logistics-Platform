'use client';
import { useState, useEffect } from 'react';
import { loadAllData, filterByModel } from '../../lib/dataLoader';

export default function DashboardPage() {
  const [stats, setStats] = useState({ products: 0, rentals: 0, storage: 0, lockers: 0, orders: 0 });

  useEffect(() => {
    loadAllData().then((data) => {
      setStats({
        products: filterByModel(data, 'goods.listmodel').length,
        rentals: filterByModel(data, 'rentals.rentalitem').length,
        storage: filterByModel(data, 'storage.storageunit').length,
        lockers: filterByModel(data, 'lockers.locker').length,
        orders: filterByModel(data, 'orders.order').length,
      });
    });
  }, []);

  return (
    <div className="container-fluid p-4 mt-5">
      <div className="alert alert-warning text-center mb-4">
        <i className="fas fa-lock me-2"></i>
        <strong>Login Required:</strong> Please <a href="#" className="alert-link">login</a> for full dashboard access.
      </div>

      <h2 className="mb-4" style={{ color: '#fff' }}><i className="fas fa-tachometer-alt me-2"></i>Dashboard Overview</h2>

      <div className="row g-3 mb-4">
        <div className="col-md-3">
          <div className="stats-card">
            <div className="stats-number">{stats.products}</div>
            <div>Products</div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="stats-card" style={{ background: 'linear-gradient(135deg, #10b981, #059669)' }}>
            <div className="stats-number">{stats.rentals}</div>
            <div>Rentals</div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="stats-card" style={{ background: 'linear-gradient(135deg, #8b5cf6, #7c3aed)' }}>
            <div className="stats-number">{stats.storage}</div>
            <div>Storage Units</div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="stats-card" style={{ background: 'linear-gradient(135deg, #f59e0b, #d97706)' }}>
            <div className="stats-number">{stats.lockers}</div>
            <div>Lockers</div>
          </div>
        </div>
      </div>

      <div className="row g-3">
        <div className="col-md-6">
          <div className="stat-card" style={{ padding: '2rem' }}>
            <div className="stat-icon" style={{ width: 60, height: 60, margin: '0 auto 1rem' }}>
              <i className="fas fa-box" style={{ fontSize: '1.5rem' }}></i>
            </div>
            <h4>Recent Orders</h4>
            <p style={{ color: 'rgba(255,255,255,0.7)' }}>{stats.orders} total orders in the system</p>
            <a href="#" className="btn btn-guest-login mt-2">
              <i className="fas fa-sign-in-alt me-1"></i>Login to View
            </a>
          </div>
        </div>
        <div className="col-md-6">
          <div className="stat-card" style={{ padding: '2rem' }}>
            <div className="stat-icon" style={{ width: 60, height: 60, margin: '0 auto 1rem' }}>
              <i className="fas fa-chart-line" style={{ fontSize: '1.5rem' }}></i>
            </div>
            <h4>Analytics</h4>
            <p style={{ color: 'rgba(255,255,255,0.7)' }}>View detailed analytics and reports</p>
            <a href="#" className="btn btn-guest-login mt-2">
              <i className="fas fa-sign-in-alt me-1"></i>Login to View
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
