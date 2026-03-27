'use client';
import { useState, useEffect } from 'react';
import { loadAllData, filterByModel } from '../../lib/dataLoader';

export default function ProductsPage() {
  const [products, setProducts] = useState([]);
  const [filtered, setFiltered] = useState([]);
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('');
  const [sortBy, setSortBy] = useState('');

  useEffect(() => {
    loadAllData().then((data) => {
      const items = filterByModel(data, 'goods.listmodel');
      setProducts(items);
      setFiltered(items);
    });
  }, []);

  useEffect(() => {
    let result = [...products];
    if (search) {
      result = result.filter((p) =>
        p.goods_desc.toLowerCase().includes(search.toLowerCase())
      );
    }
    if (category) {
      result = result.filter((p) => p.goods_class === category);
    }
    if (sortBy === 'price-low') result.sort((a, b) => a.goods_price - b.goods_price);
    else if (sortBy === 'price-high') result.sort((a, b) => b.goods_price - a.goods_price);
    else if (sortBy === 'name') result.sort((a, b) => a.goods_desc.localeCompare(b.goods_desc));
    setFiltered(result);
  }, [search, category, sortBy, products]);

  const categories = [...new Set(products.map((p) => p.goods_class))];

  function clearFilters() {
    setSearch('');
    setCategory('');
    setSortBy('');
  }

  return (
    <div className="container-fluid p-4 mt-5">
      <div className="alert alert-warning text-center mb-4">
        <i className="fas fa-lock me-2"></i>
        <strong>Login Required:</strong> Please <a href="#" className="alert-link">login</a> to purchase products, add to cart, or add to wishlist.
      </div>

      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2 style={{ color: '#fff' }}><i className="fas fa-store me-2"></i>Product Marketplace</h2>
        <a href="#" className="btn btn-primary">
          <i className="fas fa-sign-in-alt me-1"></i>Login
        </a>
      </div>

      <div className="row mb-4">
        <div className="col-md-3">
          <input
            type="text"
            className="form-control"
            placeholder="Search products..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <div className="col-md-3">
          <select
            className="form-select"
            value={category}
            onChange={(e) => setCategory(e.target.value)}
          >
            <option value="">All Categories</option>
            {categories.map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
        </div>
        <div className="col-md-3">
          <select
            className="form-select"
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
          >
            <option value="">Sort By</option>
            <option value="price-low">Price: Low to High</option>
            <option value="price-high">Price: High to Low</option>
            <option value="name">Name: A-Z</option>
          </select>
        </div>
        <div className="col-md-3">
          <button className="btn btn-outline-secondary w-100" onClick={clearFilters}>
            <i className="fas fa-times me-1"></i>Clear
          </button>
        </div>
      </div>

      <div className="row" id="productGrid">
        {filtered.map((product) => (
          <div key={product.id} className="col-md-3 mb-4">
            <div className="card product-card">
              <div className="position-relative">
                <div style={{ height: 200, background: '#f0f0f0', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <i className="fas fa-box fa-3x text-muted"></i>
                </div>
                <span className="badge bg-success position-absolute top-0 end-0 m-2">In Stock</span>
              </div>
              <div className="card-body">
                <h6 className="card-title">{product.goods_desc}</h6>
                <p className="text-muted small">{product.goods_class}</p>
                <h5 style={{ color: 'var(--zaffre)' }}>{'\u20B9'}{product.goods_price}</h5>
                <small className="text-muted">Code: {product.goods_code}</small>
                <p className="text-success small mb-0">
                  <i className="fas fa-check-circle me-1"></i>Available
                </p>
              </div>
              <div className="card-footer bg-white">
                <a href="#" className="btn btn-primary w-100">
                  <i className="fas fa-sign-in-alt me-1"></i>Login to Purchase
                </a>
              </div>
            </div>
          </div>
        ))}
        {filtered.length === 0 && (
          <div className="col-12 text-center py-5">
            <i className="fas fa-box-open fa-3x text-muted mb-3" style={{ display: 'block' }}></i>
            <p className="text-muted">No products available</p>
          </div>
        )}
      </div>
    </div>
  );
}
