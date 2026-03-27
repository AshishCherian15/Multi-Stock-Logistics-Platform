'use client';
import { useState, useEffect } from 'react';
import { Warehouse, Search, ShoppingCart, Calendar, Tag } from 'lucide-react';
import { loadAllData, filterByModel } from '../../lib/dataLoader';
import { addToCart } from '../../lib/cart';

export default function RentalsPage() {
  const [items, setItems] = useState([]);
  const [filtered, setFiltered] = useState([]);
  const [query, setQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [added, setAdded] = useState(null);

  useEffect(() => {
    loadAllData().then((data) => {
      const r = filterByModel(data, 'rentals.rentalitem');
      setItems(r);
      setFiltered(r);
    });
  }, []);

  useEffect(() => {
    let result = items.filter((r) => {
      const matchName = (r.name || '').toLowerCase().includes(query.toLowerCase());
      const matchStatus = statusFilter === 'all' || r.status === statusFilter;
      return matchName && matchStatus;
    });
    setFiltered(result);
  }, [query, statusFilter, items]);

  const handleAdd = (r) => {
    addToCart({
      id: r.id,
      type: 'rental',
      name: r.name || 'Rental Item',
      price: r.daily_rate || r.hourly_rate || 0,
      unit: 'per day',
    });
    setAdded(r.id);
    setTimeout(() => setAdded(null), 1500);
  };

  const statusColor = (s) => {
    if (s === 'available') return 'badge-green';
    if (s === 'booked') return 'badge-yellow';
    if (s === 'maintenance') return 'badge-red';
    return 'badge-gray';
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-10">
      <div className="mb-8">
        <h1 className="section-heading">Equipment Rentals</h1>
        <p className="text-slate-500">Rent equipment by the hour, day, week or month</p>
      </div>

      {/* Filters */}
      <div className="bg-white border rounded-2xl p-4 mb-8 flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Search equipment..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2.5 border rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-300"
          />
        </div>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="px-4 py-2.5 border rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-300"
        >
          <option value="all">All Status</option>
          <option value="available">Available</option>
          <option value="booked">Booked</option>
          <option value="maintenance">Maintenance</option>
        </select>
        <div className="flex items-center gap-2 text-sm text-slate-400">
          {filtered.length} items
        </div>
      </div>

      {/* Pricing info banner */}
      <div className="bg-green-50 border border-green-200 rounded-xl p-4 mb-8 flex items-center gap-3 text-sm text-green-800">
        <Tag size={16} className="shrink-0" />
        <span><strong>Flexible pricing:</strong> Hourly · Daily · Weekly · Monthly rates available. Add to cart and choose duration at checkout.</span>
      </div>

      {/* Grid */}
      {filtered.length === 0 ? (
        <div className="text-center py-20 text-slate-400">
          <Warehouse size={48} className="mx-auto mb-4 opacity-40" />
          <p className="text-lg font-medium">No rental items found</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 xl:grid-cols-4 gap-6">
          {filtered.map((r) => (
            <div key={r.id} className="bg-white border rounded-2xl overflow-hidden card-hover flex flex-col">
              <div className="h-40 bg-gradient-to-br from-green-50 to-emerald-100 flex items-center justify-center relative">
                <Warehouse size={48} className="text-green-400" />
                <span className={`badge ${statusColor(r.status)} absolute top-3 right-3`}>
                  {r.status || 'Available'}
                </span>
              </div>
              <div className="p-4 flex flex-col flex-1">
                <h3 className="font-semibold text-slate-800 mb-1">{r.name || 'Rental Item'}</h3>
                <p className="text-xs text-slate-400 mb-1">{r.description || 'No description provided'}</p>
                <p className="text-xs text-slate-400 mb-4 flex items-center gap-1">
                  <Calendar size={11} /> Condition: {r.condition || 'Good'}
                </p>

                <div className="grid grid-cols-2 gap-2 text-xs mb-4">
                  <div className="bg-slate-50 rounded-lg p-2 text-center">
                    <div className="font-bold text-slate-700">₹{r.hourly_rate || '—'}</div>
                    <div className="text-slate-400">/ hour</div>
                  </div>
                  <div className="bg-blue-50 rounded-lg p-2 text-center">
                    <div className="font-bold text-blue-700">₹{r.daily_rate || '—'}</div>
                    <div className="text-slate-400">/ day</div>
                  </div>
                  <div className="bg-slate-50 rounded-lg p-2 text-center">
                    <div className="font-bold text-slate-700">₹{r.weekly_rate || '—'}</div>
                    <div className="text-slate-400">/ week</div>
                  </div>
                  <div className="bg-slate-50 rounded-lg p-2 text-center">
                    <div className="font-bold text-slate-700">₹{r.monthly_rate || '—'}</div>
                    <div className="text-slate-400">/ month</div>
                  </div>
                </div>

                <button
                  onClick={() => handleAdd(r)}
                  disabled={r.status === 'maintenance'}
                  className={`flex items-center justify-center gap-2 text-sm font-semibold px-4 py-2.5 rounded-xl transition ${
                    added === r.id
                      ? 'bg-green-100 text-green-700'
                      : r.status === 'maintenance'
                      ? 'bg-slate-100 text-slate-400 cursor-not-allowed'
                      : 'bg-green-600 text-white hover:bg-green-700'
                  }`}
                >
                  <ShoppingCart size={14} />
                  {added === r.id ? 'Added!' : r.status === 'maintenance' ? 'Under Maintenance' : 'Book Now'}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
