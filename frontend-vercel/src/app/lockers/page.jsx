'use client';
import { useState, useEffect } from 'react';
import { Lock, Search, ShoppingCart, MapPin, Grid } from 'lucide-react';
import { loadAllData, filterByModel } from '../../lib/dataLoader';
import { addToCart } from '../../lib/cart';

export default function LockersPage() {
  const [lockers, setLockers] = useState([]);
  const [filtered, setFiltered] = useState([]);
  const [query, setQuery] = useState('');
  const [sizeFilter, setSizeFilter] = useState('all');
  const [added, setAdded] = useState(null);

  useEffect(() => {
    loadAllData().then((data) => {
      const l = filterByModel(data, 'lockers.locker');
      setLockers(l);
      setFiltered(l);
    });
  }, []);

  const sizes = [...new Set(lockers.map((l) => l.size).filter(Boolean))];

  useEffect(() => {
    let result = lockers.filter((l) => {
      const matchQuery =
        (l.locker_number || '').toLowerCase().includes(query.toLowerCase()) ||
        (l.location || '').toLowerCase().includes(query.toLowerCase());
      const matchSize = sizeFilter === 'all' || l.size === sizeFilter;
      return matchQuery && matchSize;
    });
    setFiltered(result);
  }, [query, sizeFilter, lockers]);

  const handleAdd = (l) => {
    addToCart({
      id: l.id,
      type: 'locker',
      name: `Smart Locker ${l.locker_number || l.id}`,
      price: l.daily_rate || l.hourly_rate || 0,
      unit: 'per day',
    });
    setAdded(l.id);
    setTimeout(() => setAdded(null), 1500);
  };

  const statusColor = (s) => {
    if (s === 'available') return 'badge-green';
    if (s === 'occupied') return 'badge-red';
    if (s === 'reserved') return 'badge-yellow';
    if (s === 'maintenance') return 'badge-gray';
    return 'badge-blue';
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-10">
      <div className="mb-8">
        <h1 className="section-heading">Smart Lockers</h1>
        <p className="text-slate-500">Book a secure smart locker — ideal for short-term deliveries and parcels</p>
      </div>

      {/* Filters */}
      <div className="bg-white border rounded-2xl p-4 mb-8 flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Search by locker number or location..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2.5 border rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-300"
          />
        </div>
        <select
          value={sizeFilter}
          onChange={(e) => setSizeFilter(e.target.value)}
          className="px-4 py-2.5 border rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-300"
        >
          <option value="all">All Sizes</option>
          {sizes.map((s) => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
        <div className="flex items-center gap-2 text-sm text-slate-400">
          <Grid size={14} />
          {filtered.length} lockers
        </div>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        {[
          { label: 'Total Lockers', value: lockers.length, color: 'text-blue-700' },
          { label: 'Available', value: lockers.filter((l) => l.status === 'available').length, color: 'text-green-700' },
          { label: 'Occupied', value: lockers.filter((l) => l.status === 'occupied').length, color: 'text-red-700' },
          { label: 'Reserved', value: lockers.filter((l) => l.status === 'reserved').length, color: 'text-yellow-700' },
        ].map((s) => (
          <div key={s.label} className="bg-white border rounded-xl p-4 text-center">
            <div className={`text-3xl font-black ${s.color}`}>{s.value}</div>
            <div className="text-xs text-slate-500 mt-1">{s.label}</div>
          </div>
        ))}
      </div>

      {filtered.length === 0 ? (
        <div className="text-center py-20 text-slate-400">
          <Lock size={48} className="mx-auto mb-4 opacity-40" />
          <p className="text-lg font-medium">No lockers found</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 xl:grid-cols-4 gap-6">
          {filtered.map((l) => (
            <div key={l.id} className="bg-white border rounded-2xl overflow-hidden card-hover flex flex-col">
              <div className={`h-36 flex flex-col items-center justify-center relative ${
                l.status === 'available' ? 'bg-gradient-to-br from-orange-50 to-amber-100' : 'bg-gradient-to-br from-slate-50 to-slate-100'
              }`}>
                <Lock size={40} className={l.status === 'available' ? 'text-orange-400' : 'text-slate-300'} />
                <span className="text-slate-700 font-bold mt-2 text-sm">#{l.locker_number || l.id}</span>
                <span className={`badge ${statusColor(l.status)} absolute top-3 right-3`}>
                  {l.status || 'Available'}
                </span>
              </div>
              <div className="p-4 flex flex-col flex-1">
                <h3 className="font-semibold text-slate-800 mb-1">Locker {l.locker_number || `#${l.id}`}</h3>
                <p className="text-xs text-slate-400 flex items-center gap-1 mb-1">
                  <MapPin size={11} /> {l.location || 'Main Hub'}
                </p>
                <p className="text-xs text-slate-400 mb-3">Size: <strong>{l.size || 'Medium'}</strong> · Smart lock: ✓</p>

                <div className="grid grid-cols-2 gap-2 text-xs mb-4">
                  <div className="bg-slate-50 rounded-lg p-2 text-center">
                    <div className="font-bold text-slate-700">₹{l.hourly_rate || '—'}</div>
                    <div className="text-slate-400">/ hour</div>
                  </div>
                  <div className="bg-orange-50 rounded-lg p-2 text-center">
                    <div className="font-bold text-orange-700">₹{l.daily_rate || '—'}</div>
                    <div className="text-slate-400">/ day</div>
                  </div>
                </div>

                <button
                  onClick={() => handleAdd(l)}
                  disabled={l.status !== 'available'}
                  className={`flex items-center justify-center gap-2 text-sm font-semibold px-4 py-2.5 rounded-xl transition ${
                    added === l.id
                      ? 'bg-green-100 text-green-700'
                      : l.status !== 'available'
                      ? 'bg-slate-100 text-slate-400 cursor-not-allowed'
                      : 'bg-orange-500 text-white hover:bg-orange-600'
                  }`}
                >
                  <ShoppingCart size={14} />
                  {added === l.id ? 'Added!' : l.status !== 'available' ? 'Not Available' : 'Book Locker'}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
