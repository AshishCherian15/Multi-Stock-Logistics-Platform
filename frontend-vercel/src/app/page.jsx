'use client';
import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Package, Warehouse, Lock, TrendingUp, ShieldCheck, Truck, Star } from 'lucide-react';
import { loadAllData, filterByModel } from '../lib/dataLoader';

export default function HomePage() {
  const [products, setProducts] = useState([]);
  const [rentals, setRentals] = useState([]);
  const [storage, setStorage] = useState([]);
  const [lockers, setLockers] = useState([]);

  useEffect(() => {
    loadAllData().then((data) => {
      setProducts(filterByModel(data, 'goods.listmodel').slice(0, 6));
      setRentals(filterByModel(data, 'rentals.rentalitem').slice(0, 4));
      setStorage(filterByModel(data, 'storage.storageunit').slice(0, 4));
      setLockers(filterByModel(data, 'lockers.locker').slice(0, 4));
    });
  }, []);

  const stats = [
    { label: 'Products', value: '500+', icon: <Package size={24} className="text-blue-600" /> },
    { label: 'Warehouses', value: '12', icon: <Warehouse size={24} className="text-blue-600" /> },
    { label: 'Orders', value: '10K+', icon: <Truck size={24} className="text-blue-600" /> },
    { label: 'Satisfaction', value: '98%', icon: <Star size={24} className="text-blue-600" /> },
  ];

  return (
    <div>
      {/* Hero */}
      <section className="hero-gradient text-white py-20 px-4">
        <div className="max-w-7xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 bg-white/20 rounded-full px-4 py-1.5 text-sm mb-6">
            <ShieldCheck size={14} />
            Enterprise Warehouse & Logistics Platform
          </div>
          <h1 className="text-4xl md:text-6xl font-black leading-tight mb-6">
            Multi-Stock<br />
            <span className="text-blue-200">Logistics Platform</span>
          </h1>
          <p className="text-blue-100 text-lg md:text-xl max-w-2xl mx-auto mb-10">
            Your one-stop solution for inventory management, equipment rentals, storage
            bookings, and smart locker services.
          </p>
          <div className="flex flex-wrap gap-4 justify-center">
            <Link href="/products" className="bg-white text-blue-700 font-semibold px-8 py-3 rounded-xl hover:bg-blue-50 transition">
              Browse Products
            </Link>
            <Link href="/rentals" className="bg-blue-600/50 text-white border border-white/30 font-semibold px-8 py-3 rounded-xl hover:bg-blue-600 transition">
              View Rentals
            </Link>
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="bg-white border-b py-10 px-4">
        <div className="max-w-7xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-8">
          {stats.map((s) => (
            <div key={s.label} className="text-center">
              <div className="flex justify-center mb-2">{s.icon}</div>
              <div className="text-3xl font-black text-slate-900">{s.value}</div>
              <div className="text-sm text-slate-500 mt-1">{s.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Services */}
      <section className="max-w-7xl mx-auto px-4 py-16">
        <h2 className="section-heading text-center">Our Services</h2>
        <p className="text-slate-500 text-center mb-10">Everything you need in one logistics platform</p>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[
            { href: '/products', icon: <Package size={32} className="text-blue-600" />, title: 'Marketplace', desc: 'Buy products from verified suppliers with real-time stock tracking.' },
            { href: '/rentals', icon: <Warehouse size={32} className="text-green-600" />, title: 'Equipment Rentals', desc: 'Hourly to monthly rental equipment for logistics operations.' },
            { href: '/storage', icon: <TrendingUp size={32} className="text-purple-600" />, title: 'Storage Units', desc: 'Flexible storage booking by size and duration.' },
            { href: '/lockers', icon: <Lock size={32} className="text-orange-600" />, title: 'Smart Lockers', desc: 'Book, pay, and access smart lockers for secure deliveries.' },
          ].map((s) => (
            <Link key={s.href} href={s.href} className="bg-white border rounded-2xl p-6 card-hover cursor-pointer group">
              <div className="mb-4">{s.icon}</div>
              <h3 className="font-bold text-lg text-slate-900 mb-2 group-hover:text-blue-700 transition">{s.title}</h3>
              <p className="text-sm text-slate-500 leading-relaxed">{s.desc}</p>
            </Link>
          ))}
        </div>
      </section>

      {/* Featured Products */}
      {products.length > 0 && (
        <section className="bg-slate-50 py-16 px-4">
          <div className="max-w-7xl mx-auto">
            <div className="flex items-center justify-between mb-8">
              <div>
                <h2 className="section-heading">Featured Products</h2>
                <p className="text-slate-500 text-sm">Latest items from our marketplace</p>
              </div>
              <Link href="/products" className="text-blue-700 font-semibold text-sm hover:underline">View all →</Link>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
              {products.map((p) => (
                <div key={p.id} className="bg-white border rounded-2xl p-5 card-hover">
                  <div className="w-full h-36 bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl flex items-center justify-center mb-4">
                    <Package size={40} className="text-blue-400" />
                  </div>
                  <div className="badge badge-green mb-2">{p.goods_unit || 'In Stock'}</div>
                  <h3 className="font-semibold text-slate-900 text-sm mb-1 line-clamp-2">{p.goods_desc || p.goods_name || 'Product'}</h3>
                  <p className="text-slate-400 text-xs mb-3">SKU: {p.goods_code || '—'}</p>
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-blue-700 text-lg">₹{p.goods_price || '0'}</span>
                    <span className="text-xs text-slate-400">Stock: {p.onhand_stock ?? '—'}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* Rentals preview */}
      {rentals.length > 0 && (
        <section className="max-w-7xl mx-auto px-4 py-16">
          <div className="flex items-center justify-between mb-8">
            <div>
              <h2 className="section-heading">Equipment Rentals</h2>
              <p className="text-slate-500 text-sm">Available for hourly, daily, weekly or monthly hire</p>
            </div>
            <Link href="/rentals" className="text-blue-700 font-semibold text-sm hover:underline">View all →</Link>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-5">
            {rentals.map((r) => (
              <div key={r.id} className="bg-white border rounded-2xl p-5 card-hover">
                <div className="w-full h-28 bg-gradient-to-br from-green-50 to-green-100 rounded-xl flex items-center justify-center mb-4">
                  <Warehouse size={32} className="text-green-400" />
                </div>
                <span className={`badge ${r.status === 'available' ? 'badge-green' : 'badge-yellow'} mb-2`}>{r.status || 'Available'}</span>
                <h3 className="font-semibold text-slate-900 text-sm mb-1 line-clamp-2">{r.name || 'Rental Item'}</h3>
                <p className="text-xs text-slate-400 mb-2">{r.category_name || r.category || 'Equipment'}</p>
                <span className="font-bold text-green-700">₹{r.daily_rate || r.hourly_rate || '0'}<span className="text-xs font-normal text-slate-400">/day</span></span>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* CTA */}
      <section className="bg-blue-700 text-white py-16 px-4">
        <div className="max-w-3xl mx-auto text-center">
          <h2 className="text-3xl font-black mb-4">Ready to get started?</h2>
          <p className="text-blue-200 mb-8">Browse our full catalog of products, rent equipment, book storage or a locker today.</p>
          <div className="flex flex-wrap gap-4 justify-center">
            <Link href="/products" className="bg-white text-blue-700 font-semibold px-8 py-3 rounded-xl hover:bg-blue-50 transition">Shop Now</Link>
            <Link href="/dashboard" className="border border-white/50 text-white font-semibold px-8 py-3 rounded-xl hover:bg-white/10 transition">View Dashboard</Link>
          </div>
        </div>
      </section>
    </div>
  );
}
