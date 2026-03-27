'use client';
import { useState, useEffect } from 'react';
import Link from 'next/link';
import { CheckCircle, ShoppingCart, User, MapPin, CreditCard, Truck } from 'lucide-react';
import { getCart, getCartTotal, clearCart } from '../../lib/cart';

export default function CheckoutPage() {
  const [cart, setCart] = useState([]);
  const [step, setStep] = useState(1); // 1=info, 2=payment, 3=success
  const [form, setForm] = useState({
    name: '', email: '', phone: '', address: '', city: '', state: 'Karnataka', pincode: '',
    paymentMethod: 'card',
  });
  const [orderNum, setOrderNum] = useState('');

  useEffect(() => {
    setCart(getCart());
  }, []);

  const total = getCartTotal(cart);
  const tax = total * 0.18;
  const grand = total + tax;

  const handleChange = (e) => setForm((f) => ({ ...f, [e.target.name]: e.target.value }));

  const handlePlaceOrder = () => {
    const num = 'MS' + Date.now().toString().slice(-8);
    setOrderNum(num);
    // Save to localStorage as order history
    const existing = JSON.parse(localStorage.getItem('ms_orders') || '[]');
    existing.push({ orderNum: num, date: new Date().toISOString(), cart, total: grand, form });
    localStorage.setItem('ms_orders', JSON.stringify(existing));
    clearCart();
    setStep(3);
  };

  if (step === 3) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-20 text-center">
        <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
          <CheckCircle size={40} className="text-green-600" />
        </div>
        <h1 className="text-3xl font-black text-slate-900 mb-3">Order Placed!</h1>
        <p className="text-slate-500 mb-2">Your order <strong className="text-slate-800">{orderNum}</strong> has been confirmed.</p>
        <p className="text-slate-500 mb-10">You'll receive a confirmation shortly. Thank you for choosing MultiStock!</p>
        <div className="flex flex-wrap gap-4 justify-center">
          <Link href="/dashboard" className="bg-blue-700 text-white px-8 py-3 rounded-xl font-semibold hover:bg-blue-800 transition">
            View Dashboard
          </Link>
          <Link href="/products" className="border border-slate-300 text-slate-700 px-8 py-3 rounded-xl font-semibold hover:bg-slate-50 transition">
            Continue Shopping
          </Link>
        </div>
      </div>
    );
  }

  if (cart.length === 0) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-20 text-center">
        <ShoppingCart size={48} className="mx-auto mb-4 text-slate-300" />
        <h2 className="text-xl font-bold text-slate-700 mb-4">No items to checkout</h2>
        <Link href="/products" className="bg-blue-700 text-white px-8 py-3 rounded-xl font-semibold hover:bg-blue-800 transition">
          Shop Now
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto px-4 py-10">
      <h1 className="section-heading mb-2">Checkout</h1>

      {/* Steps */}
      <div className="flex items-center gap-2 mb-10 text-sm">
        {[{ n: 1, label: 'Delivery Info' }, { n: 2, label: 'Payment' }].map((s, i) => (
          <div key={s.n} className="flex items-center gap-2">
            <div className={`w-7 h-7 rounded-full flex items-center justify-center font-bold text-xs ${step >= s.n ? 'bg-blue-700 text-white' : 'bg-slate-100 text-slate-400'}`}>{s.n}</div>
            <span className={step >= s.n ? 'text-blue-700 font-medium' : 'text-slate-400'}>{s.label}</span>
            {i < 1 && <div className="w-8 h-px bg-slate-300 mx-1" />}
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Form */}
        <div className="lg:col-span-2">
          {step === 1 && (
            <div className="bg-white border rounded-2xl p-6">
              <h2 className="font-semibold text-slate-800 mb-5 flex items-center gap-2"><User size={16} /> Delivery Information</h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {[
                  { name: 'name', label: 'Full Name', placeholder: 'John Doe', type: 'text' },
                  { name: 'email', label: 'Email', placeholder: 'john@example.com', type: 'email' },
                  { name: 'phone', label: 'Phone', placeholder: '+91 98765 43210', type: 'tel' },
                  { name: 'pincode', label: 'Pincode', placeholder: '560001', type: 'text' },
                ].map((f) => (
                  <div key={f.name}>
                    <label className="block text-xs font-medium text-slate-600 mb-1">{f.label}</label>
                    <input
                      type={f.type}
                      name={f.name}
                      value={form[f.name]}
                      onChange={handleChange}
                      placeholder={f.placeholder}
                      className="w-full border rounded-xl px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300"
                    />
                  </div>
                ))}
                <div className="sm:col-span-2">
                  <label className="block text-xs font-medium text-slate-600 mb-1">Address</label>
                  <input
                    type="text"
                    name="address"
                    value={form.address}
                    onChange={handleChange}
                    placeholder="Street address, building, flat no."
                    className="w-full border rounded-xl px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-600 mb-1">City</label>
                  <input
                    type="text"
                    name="city"
                    value={form.city}
                    onChange={handleChange}
                    placeholder="Bengaluru"
                    className="w-full border rounded-xl px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-600 mb-1">State</label>
                  <select
                    name="state"
                    value={form.state}
                    onChange={handleChange}
                    className="w-full border rounded-xl px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300"
                  >
                    {['Karnataka', 'Maharashtra', 'Tamil Nadu', 'Delhi', 'Telangana', 'Kerala', 'Gujarat'].map((s) => (
                      <option key={s}>{s}</option>
                    ))}
                  </select>
                </div>
              </div>
              <button
                onClick={() => setStep(2)}
                className="mt-6 w-full bg-blue-700 text-white py-3 rounded-xl font-semibold hover:bg-blue-800 transition"
              >
                Continue to Payment →
              </button>
            </div>
          )}

          {step === 2 && (
            <div className="bg-white border rounded-2xl p-6">
              <h2 className="font-semibold text-slate-800 mb-5 flex items-center gap-2"><CreditCard size={16} /> Payment Method</h2>
              <div className="space-y-3 mb-6">
                {[
                  { value: 'card', label: 'Credit / Debit Card', icon: '💳' },
                  { value: 'upi', label: 'UPI (Google Pay, PhonePe, Paytm)', icon: '📱' },
                  { value: 'cod', label: 'Cash on Delivery', icon: '💵' },
                  { value: 'wallet', label: 'MultiStock Wallet', icon: '👛' },
                ].map((m) => (
                  <label
                    key={m.value}
                    className={`flex items-center gap-3 p-4 border rounded-xl cursor-pointer transition ${form.paymentMethod === m.value ? 'border-blue-500 bg-blue-50' : 'border-slate-200 hover:border-blue-300'}`}
                  >
                    <input
                      type="radio"
                      name="paymentMethod"
                      value={m.value}
                      checked={form.paymentMethod === m.value}
                      onChange={handleChange}
                      className="accent-blue-700"
                    />
                    <span className="text-lg">{m.icon}</span>
                    <span className="font-medium text-slate-700 text-sm">{m.label}</span>
                  </label>
                ))}
              </div>
              <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-3 text-xs text-yellow-800 mb-5 flex items-start gap-2">
                <span>ℹ️</span>
                <span>This is a demo platform. No real payment is processed. Clicking Place Order will simulate a successful order.</span>
              </div>
              <div className="flex gap-3">
                <button
                  onClick={() => setStep(1)}
                  className="border border-slate-300 text-slate-700 px-6 py-3 rounded-xl font-semibold hover:bg-slate-50 transition"
                >
                  ← Back
                </button>
                <button
                  onClick={handlePlaceOrder}
                  className="flex-1 bg-green-600 text-white py-3 rounded-xl font-semibold hover:bg-green-700 transition"
                >
                  ✓ Place Order — ₹{grand.toFixed(2)}
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Order summary */}
        <div className="bg-white border rounded-2xl p-5 h-fit">
          <h3 className="font-semibold text-slate-800 mb-4">Order Summary</h3>
          <div className="space-y-2 mb-4 max-h-48 overflow-y-auto">
            {cart.map((item) => (
              <div key={`${item.type}-${item.id}`} className="flex justify-between text-xs text-slate-600">
                <span className="truncate mr-2">{item.name} ×{item.qty}</span>
                <span className="shrink-0 font-medium">₹{(parseFloat(item.price) * (item.qty || 1)).toFixed(0)}</span>
              </div>
            ))}
          </div>
          <div className="border-t pt-3 space-y-2 text-sm">
            <div className="flex justify-between text-slate-500"><span>Subtotal</span><span>₹{total.toFixed(2)}</span></div>
            <div className="flex justify-between text-slate-500"><span>GST 18%</span><span>₹{tax.toFixed(2)}</span></div>
            <div className="flex justify-between font-bold text-base border-t pt-2">
              <span>Total</span><span className="text-blue-700">₹{grand.toFixed(2)}</span>
            </div>
          </div>
          <div className="flex items-center gap-2 text-xs text-slate-400 mt-4">
            <Truck size={12} /><span>Free delivery across India</span>
          </div>
        </div>
      </div>
    </div>
  );
}
