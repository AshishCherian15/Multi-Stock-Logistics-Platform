'use client';
import { useState, useEffect } from 'react';
import { getCart, removeFromCart, updateQty, getCartTotal } from '../../lib/cart';

export default function CartPage() {
  const [cart, setCart] = useState([]);

  function refresh() { setCart(getCart()); }
  useEffect(() => { refresh(); window.addEventListener('cartUpdated', refresh); return () => window.removeEventListener('cartUpdated', refresh); }, []);

  const total = getCartTotal(cart);

  return (
    <div className="container-fluid p-4 mt-5">
      <div className="alert alert-warning text-center mb-4">
        <i className="fas fa-lock me-2"></i>
        <strong>Login Required:</strong> Please <a href="#" className="alert-link">login</a> to manage your cart and place orders.
      </div>

      <h2 className="mb-4" style={{ color: '#fff' }}><i className="fas fa-shopping-cart me-2"></i>Shopping Cart</h2>

      {cart.length === 0 ? (
        <div className="text-center py-5">
          <i className="fas fa-shopping-cart fa-4x mb-3" style={{ color: 'rgba(255,255,255,0.3)', display: 'block' }}></i>
          <h4 style={{ color: 'rgba(255,255,255,0.7)' }}>Your cart is empty</h4>
          <a href="/products" className="btn btn-primary mt-3">
            <i className="fas fa-store me-1"></i>Browse Products
          </a>
        </div>
      ) : (
        <div className="row">
          <div className="col-md-8">
            {cart.map((item) => (
              <div key={`${item.type}-${item.id}`} className="card mb-3" style={{ borderRadius: 15 }}>
                <div className="card-body d-flex justify-content-between align-items-center">
                  <div>
                    <h5 className="mb-1">{item.name}</h5>
                    <span className="badge bg-info">{item.type}</span>
                    <p className="mb-0 mt-2" style={{ color: 'var(--zaffre)', fontWeight: 700 }}>{'\u20B9'}{item.price}</p>
                  </div>
                  <div className="d-flex align-items-center gap-2">
                    <button className="btn btn-outline-secondary btn-sm" onClick={() => updateQty(item.id, item.type, item.qty - 1)}>-</button>
                    <span className="fw-bold">{item.qty}</span>
                    <button className="btn btn-outline-secondary btn-sm" onClick={() => updateQty(item.id, item.type, item.qty + 1)}>+</button>
                    <button className="btn btn-outline-danger btn-sm ms-2" onClick={() => removeFromCart(item.id, item.type)}>
                      <i className="fas fa-trash"></i>
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
          <div className="col-md-4">
            <div className="card" style={{ borderRadius: 15 }}>
              <div className="card-body">
                <h5>Order Summary</h5>
                <hr />
                <div className="d-flex justify-content-between mb-2">
                  <span>Items:</span>
                  <strong>{cart.length}</strong>
                </div>
                <div className="d-flex justify-content-between mb-3">
                  <span>Total:</span>
                  <strong style={{ color: 'var(--zaffre)', fontSize: '1.5rem' }}>{'\u20B9'}{total.toFixed(2)}</strong>
                </div>
                <a href="#" className="btn btn-primary w-100">
                  <i className="fas fa-sign-in-alt me-1"></i>Login to Checkout
                </a>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
