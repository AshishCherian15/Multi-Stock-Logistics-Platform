'use client';
import { useState, useEffect } from 'react';
import Link from 'next/link';
import { ShoppingCart, Trash2, Plus, Minus, Tag, ArrowRight } from 'lucide-react';
import { getCart, removeFromCart, updateQty, getCartTotal, getCartCount } from '../../lib/cart';

export default function CartPage() {
  const [cart, setCart] = useState([]);

  const refresh = () => setCart(getCart());

  useEffect(() => {
    refresh();
    window.addEventListener('cartUpdated', refresh);
    return () => window.removeEventListener('cartUpdated', refresh);
  }, []);

  const total = getCartTotal(cart);
  const tax = total * 0.18;
  const grand = total + tax;

  if (cart.length === 0) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-20 text-center">
        <ShoppingCart size={64} className="mx-auto mb-6 text-slate-300" />
        <h2 className="text-2xl font-bold text-slate-700 mb-3">Your cart is empty</h2>
        <p className="text-slate-500 mb-8">Add products, rentals, storage or lockers to your cart.</p>
        <Link href="/products" className="bg-blue-700 text-white px-8 py-3 rounded-xl font-semibold hover:bg-blue-800 transition">
          Browse Products
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-10">
      <div className="mb-8">
        <h1 className="section-heading">Shopping Cart</h1>
        <p className="text-slate-500">{getCartCount(cart)} item{getCartCount(cart) !== 1 ? 's' : ''} in your cart</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Items */}
        <div className="lg:col-span-2 space-y-4">
          {cart.map((item) => (
            <div key={`${item.type}-${item.id}`} className="bg-white border rounded-2xl p-5 flex items-center gap-5">
              <div className="w-16 h-16 bg-blue-50 rounded-xl flex items-center justify-center shrink-0">
                <ShoppingCart size={24} className="text-blue-400" />
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="font-semibold text-slate-800 truncate">{item.name}</h3>
                <p className="text-xs text-slate-400 capitalize mt-0.5">{item.type} {item.unit ? `· ${item.unit}` : ''}</p>
                <p className="text-blue-700 font-bold mt-1">₹{parseFloat(item.price).toFixed(2)}</p>
              </div>
              <div className="flex items-center gap-2 border rounded-xl overflow-hidden">
                <button
                  onClick={() => updateQty(item.id, item.type, (item.qty || 1) - 1)}
                  className="px-3 py-2 hover:bg-slate-100 transition text-slate-600"
                >
                  <Minus size={14} />
                </button>
                <span className="px-3 text-sm font-semibold min-w-[1.5rem] text-center">{item.qty || 1}</span>
                <button
                  onClick={() => updateQty(item.id, item.type, (item.qty || 1) + 1)}
                  className="px-3 py-2 hover:bg-slate-100 transition text-slate-600"
                >
                  <Plus size={14} />
                </button>
              </div>
              <div className="text-right">
                <p className="font-bold text-slate-800">₹{(parseFloat(item.price) * (item.qty || 1)).toFixed(2)}</p>
                <button
                  onClick={() => removeFromCart(item.id, item.type)}
                  className="text-red-400 hover:text-red-600 mt-1 transition"
                >
                  <Trash2 size={14} />
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* Summary */}
        <div className="space-y-4">
          {/* Coupon code */}
          <div className="bg-white border rounded-2xl p-5">
            <h3 className="font-semibold text-slate-800 mb-3 flex items-center gap-2"><Tag size={16} /> Coupon Code</h3>
            <div className="flex gap-2">
              <input
                type="text"
                placeholder="Enter code (e.g. WELCOME10)"
                className="flex-1 border rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300"
              />
              <button className="bg-blue-700 text-white px-4 py-2 rounded-xl text-sm font-medium hover:bg-blue-800 transition">
                Apply
              </button>
            </div>
            <p className="text-xs text-slate-400 mt-2">Try: WELCOME10 · SAVE20 · FLAT100</p>
          </div>

          {/* Order summary */}
          <div className="bg-white border rounded-2xl p-5">
            <h3 className="font-semibold text-slate-800 mb-4">Order Summary</h3>
            <div className="space-y-3 text-sm">
              <div className="flex justify-between text-slate-600">
                <span>Subtotal ({getCartCount(cart)} items)</span>
                <span>₹{total.toFixed(2)}</span>
              </div>
              <div className="flex justify-between text-slate-600">
                <span>GST (18%)</span>
                <span>₹{tax.toFixed(2)}</span>
              </div>
              <div className="flex justify-between text-slate-600">
                <span>Delivery</span>
                <span className="text-green-600 font-medium">Free</span>
              </div>
              <div className="border-t pt-3 flex justify-between font-bold text-slate-900 text-base">
                <span>Total</span>
                <span className="text-blue-700">₹{grand.toFixed(2)}</span>
              </div>
            </div>
            <Link
              href="/checkout"
              className="mt-5 w-full flex items-center justify-center gap-2 bg-blue-700 text-white py-3 rounded-xl font-semibold hover:bg-blue-800 transition"
            >
              Proceed to Checkout <ArrowRight size={16} />
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
