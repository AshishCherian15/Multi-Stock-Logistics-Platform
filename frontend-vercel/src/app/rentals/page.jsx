'use client';
import { useState, useEffect } from 'react';
import { loadAllData, filterByModel } from '../../lib/dataLoader';

export default function RentalsPage() {
  const [items, setItems] = useState([]);
  const [filtered, setFiltered] = useState([]);
  const [search, setSearch] = useState('');
  const [sortBy, setSortBy] = useState('name');

  useEffect(() => {
    loadAllData().then((data) => {
      const rentals = filterByModel(data, 'rentals.rentalitem');
      setItems(rentals);
      setFiltered(rentals);
    });
  }, []);

  useEffect(() => {
    let result = [...items];
    if (search) {
      result = result.filter((r) =>
        r.name.toLowerCase().includes(search.toLowerCase())
      );
    }
    if (sortBy === 'name') result.sort((a, b) => a.name.localeCompare(b.name));
    else if (sortBy === 'price-low') result.sort((a, b) => parseFloat(a.daily_rate) - parseFloat(b.daily_rate));
    else if (sortBy === 'price-high') result.sort((a, b) => parseFloat(b.daily_rate) - parseFloat(a.daily_rate));
    setFiltered(result);
  }, [search, sortBy, items]);

  function clearFilters() {
    setSearch('');
    setSortBy('name');
  }

  return (
    <div className="container-fluid p-4 mt-5">
      <div className="alert alert-warning text-center mb-4">
        <i className="fas fa-lock me-2"></i>
        <strong>Login Required:</strong> Please <a href="#" className="alert-link">login</a> to book rentals, add to cart, or add to wishlist.
      </div>

      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2 style={{ color: '#fff' }}><i className="fas fa-key me-2"></i>Rental Equipment</h2>
        <a href="#" className="btn btn-primary">
          <i className="fas fa-sign-in-alt me-1"></i>Login
        </a>
      </div>

      {/* Search and Filters */}
      <div className="card mb-4" style={{ border: 'none', borderRadius: 15, boxShadow: '0 2px 12px rgba(0, 20, 168, 0.1)' }}>
        <div className="card-body">
          <div className="row g-3 mb-3">
            <div className="col-md-6">
              <input
                type="text"
                className="form-control"
                placeholder="Search equipment..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>
            <div className="col-md-3">
              <select
                className="form-select"
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
              >
                <option value="name">Sort by Name</option>
                <option value="price-low">Price: Low to High</option>
                <option value="price-high">Price: High to Low</option>
              </select>
            </div>
            <div className="col-md-3">
              <button className="btn btn-outline-secondary w-100" onClick={clearFilters}>
                <i className="fas fa-times me-1"></i>Clear Filters
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Rental Items Grid */}
      <div className="row g-4">
        {filtered.map((item) => (
          <div key={item.id} className="col-md-4">
            <div className="card rental-card">
              <div className="position-relative">
                <div className="rental-image bg-light d-flex align-items-center justify-content-center" style={{ height: 200 }}>
                  <i className="fas fa-image fa-3x text-muted"></i>
                </div>
                <span className="status-badge status-available">
                  <i className="fas fa-check-circle me-1"></i>Available
                </span>
              </div>

              <div className="card-body">
                <h5 className="card-title mb-2">{item.name}</h5>
                <p className="text-muted small mb-3">{item.description ? item.description.substring(0, 80) + '...' : ''}</p>

                {/* Pricing */}
                <div className="mb-3">
                  <div className="d-flex justify-content-between align-items-center mb-2">
                    <small className="text-muted">Hourly:</small>
                    <span className="price-tag">{'\u20B9'}{item.hourly_rate}/hr</span>
                  </div>
                  <div className="d-flex justify-content-between align-items-center mb-2">
                    <small className="text-muted">Daily:</small>
                    <span className="price-tag">{'\u20B9'}{item.daily_rate}/day</span>
                  </div>
                  <div className="d-flex justify-content-between align-items-center mb-2">
                    <small className="text-muted">Weekly:</small>
                    <span className="price-tag">{'\u20B9'}{item.weekly_rate}/week</span>
                  </div>
                  <div className="d-flex justify-content-between align-items-center">
                    <small className="text-muted">Monthly:</small>
                    <span className="price-tag">{'\u20B9'}{item.monthly_rate}/month</span>
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
        ))}
        {filtered.length === 0 && (
          <div className="col-12 text-center py-5">
            <i className="fas fa-inbox fa-4x text-muted mb-3" style={{ display: 'block' }}></i>
            <h4 className="text-muted">No rental items available</h4>
          </div>
        )}
      </div>
    </div>
  );
}
