'use client';
import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Package, Warehouse, Lock, ShoppingBag, TrendingUp, Clock } from 'lucide-react';
import { loadAllData, filterByModel } from '../../lib/dataLoader';

export default function DashboardPage() {
  const [stats, setStats] = useState({
    products: 0, rentals: 0, storage: 0, lockers: 0,
    availableRentals: 0, availableStorage: 0, availableLockers: 0,
  });
  const [orders, setOrders] = useState([]);

  useEffect(() => {
    loadAllData().then((data) => {
      const products = filterByModel(data, 'goods.listmodel');
      const rentals = filterByModel(data, 'rentals.rentalitem');
      const storage = filterByModel(data, 'storage.storageunit');
      const lockers = filterByModel(data, 'lockers.locker');
      setStats({
        products: products.length,
        rentals: rentals.length,
        storage: storage.length,
        lockers: lockers.length,
        availableRentals: rentals.filter((r) => r.status === 'available').length,
        availableStorage: storage.filter((s) => s.status === 'available').length,
        availableLockers: lockers.filter((l) => l.status === 'available').length,
      });
    });
    // Load local orders
    setOrders(JSON.parse(localStorage.getItem('ms_orders') || '[]').reverse().slice(0, 5));
  }, []);

  const cards = [
    { label: 'Products', value: stats.products, sub: 'in catalog', icon: <Package size={22} className="text-blue-500" />, href: '/products', color: 'from-blue-50 to-blue-100', border: 'border-blue-100' },
    { label: 'Rental Items', value: stats.rentals, sub: `${stats.availableRentals} available`, icon: <Warehouse size={22} className="text-green-500" />, href: '/rentals', color: 'from-green-50 to-emerald-100', border: 'border-green-100' },
    { label: 'Storage Units', value: stats.storage, sub: `${stats.availableStorage} available`, icon: <TrendingUp size={22} className="text-purple-500" />, href: '/storage', color: 'from-purple-50 to-violet-100', border: 'border-purple-100' },
    { label: 'Smart Lockers', value: stats.lockers, sub: `${stats.availableLockers} available`, icon: <Lock size={22} className="text-orange-500" />, href: '/lockers', color: 'from-orange-50 to-amber-100', border: 'border-orange-100' },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 py-10">
      <div className="mb-8">
        <h1 className="section-heading">Platform Dashboard</h1>
        <p className="text-slate-500">Overview of the MultiStock Logistics Platform</p>
      </div>

      {/* Stats cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-6 mb-10">
        {cards.map((c) => (
          <Link key={c.href} href={c.href} className={`bg-gradient-to-br ${c.color} border ${c.border} rounded-2xl p-5 card-hover`}>
            <div className="flex items-center justify-between mb-3">
              <div className="w-10 h-10 bg-white rounded-xl flex items-center justify-center shadow-sm">
                {c.icon}
              </div>
              <span className="text-xs font-medium text-slate-400 bg-white rounded-full px-2 py-0.5">{c.sub}</span>
            </div>
            <div className="text-3xl font-black text-slate-900">{c.value}</div>
            <div className="text-sm font-medium text-slate-600 mt-0.5">{c.label}</div>
          </Link>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Quick actions */}
        <div className="bg-white border rounded-2xl p-6">
          <h2 className="font-semibold text-slate-800 mb-5">Quick Actions</h2>
          <div className="grid grid-cols-2 gap-3">
            {[
              { href: '/products', label: 'Browse Products', icon: <Package size={18} />, color: 'bg-blue-50 text-blue-700 hover:bg-blue-100' },
              { href: '/rentals', label: 'Book Rental', icon: <Warehouse size={18} />, color: 'bg-green-50 text-green-700 hover:bg-green-100' },
              { href: '/storage', label: 'Book Storage', icon: <TrendingUp size={18} />, color: 'bg-purple-50 text-purple-700 hover:bg-purple-100' },
              { href: '/lockers', label: 'Book Locker', icon: <Lock size={18} />, color: 'bg-orange-50 text-orange-700 hover:bg-orange-100' },
              { href: '/cart', label: 'View Cart', icon: <ShoppingBag size={18} />, color: 'bg-slate-50 text-slate-700 hover:bg-slate-100' },
              { href: '/checkout', label: 'Checkout', icon: <TrendingUp size={18} />, color: 'bg-teal-50 text-teal-700 hover:bg-teal-100' },
            ].map((a) => (
              <Link
                key={a.href}
                href={a.href}
                className={`flex items-center gap-2.5 px-4 py-3 rounded-xl font-medium text-sm transition ${a.color}`}
              >
                {a.icon}
                {a.label}
              </Link>
            ))}
          </div>
        </div>

        {/* Recent orders */}
        <div className="bg-white border rounded-2xl p-6">
          <div className="flex items-center justify-between mb-5">
            <h2 className="font-semibold text-slate-800">Recent Orders</h2>
            <span className="text-xs text-slate-400">(this session)</span>
          </div>
          {orders.length === 0 ? (
            <div className="text-center py-8 text-slate-400">
              <ShoppingBag size={32} className="mx-auto mb-3 opacity-40" />
              <p className="text-sm">No orders yet</p>
              <Link href="/products" className="text-xs text-blue-600 hover:underline mt-1 block">Start shopping →</Link>
            </div>
          ) : (
            <div className="space-y-3">
              {orders.map((o) => (
                <div key={o.orderNum} className="flex items-center justify-between p-3 bg-slate-50 rounded-xl">
                  <div>
                    <p className="font-semibold text-sm text-slate-800">{o.orderNum}</p>
                    <p className="text-xs text-slate-400 flex items-center gap-1 mt-0.5">
                      <Clock size={10} />
                      {new Date(o.date).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="font-bold text-blue-700 text-sm">₹{parseFloat(o.total).toFixed(2)}</p>
                    <span className="badge badge-green text-xs">Confirmed</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Platform info */}
      <div className="mt-8 bg-gradient-to-r from-blue-700 to-blue-800 rounded-2xl p-6 text-white">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div>
            <h3 className="font-bold text-lg mb-1">Multi-Stock Logistics Platform</h3>
            <p className="text-blue-200 text-sm">Final Year B.E. CS Engineering Project · USN: 4KM22CS018 · 2025-26</p>
          </div>
          <div className="flex gap-3">
            <Link href="/products" className="bg-white text-blue-700 px-5 py-2.5 rounded-xl font-semibold text-sm hover:bg-blue-50 transition">
              Explore Platform
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
