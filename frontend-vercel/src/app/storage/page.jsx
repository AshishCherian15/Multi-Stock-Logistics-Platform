'use client';
import { useState, useEffect } from 'react';
import { Package, Search, ShoppingCart, Ruler, MapPin } from 'lucide-react';
import { loadAllData, filterByModel } from '../../lib/dataLoader';
import { addToCart } from '../../lib/cart';

export default function StoragePage() {
  const [units, setUnits] = useState([]);
  const [filtered, setFiltered] = useState([]);
  const [query, setQuery] = useState('');
  const [sizeFilter, setSizeFilter] = useState('all');
  const [added, setAdded] = useState(null);

  useEffect(() => {
    loadAllData().then((data) => {
      const u = filterByModel(data, 'storage.storageunit');
      setUnits(u);
      setFiltered(u);
    });
  }, []);

  const sizes = [...new Set(units.map((u) => u.size).filter(Boolean))];

  useEffect(() => {
    let result = units.filter((u) => {
      const matchQuery = (u.unit_number || u.name || '').toLowerCase().includes(query.toLowerCase());
      const matchSize = sizeFilter === 'all' || u.size === sizeFilter;
      return matchQuery && matchSize;
    });
    setFiltered(result);
  }, [query, sizeFilter, units]);

  const handleAdd = (u) => {
    addToCart({
      id: u.id,
      type: 'storage',
      name: `Storage Unit ${u.unit_number || u.id}`,
      price: u.monthly_rate || u.daily_rate || 0,
      unit: 'per month',
    });
    setAdded(u.id);
    setTimeout(() => setAdded(null), 1500);
  };

  const statusColor = (s) => {
    if (s === 'available') return 'badge-green';
    if (s === 'occupied') return 'badge-red';
    if (s === 'reserved') return 'badge-yellow';
    return 'badge-gray';
  };

  const sizeLabel = (s) => {
    const map = { small: 'Small (5×5 ft)', medium: 'Medium (10×10 ft)', large: 'Large (20×20 ft)', extra_large: 'Extra Large (30×30 ft)' };
    return map[s] || s || '—';
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-10">
      <div className="mb-8">
        <h1 className="section-heading">Storage Units</h1>
        <p className="text-slate-500">Flexible storage solutions — book by size and duration</p>
      </div>

      {/* Filters */}
      <div className="bg-white border rounded-2xl p-4 mb-8 flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Search units..."
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
            <option key={s} value={s}>{sizeLabel(s)}</option>
          ))}
        </select>
        <div className="flex items-center gap-2 text-sm text-slate-400">
          {filtered.length} units
        </div>
      </div>

      {/* Size guide */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        {[
          { size: 'small', label: 'Small', dims: '5×5 ft', desc: 'Boxes, small items' },
          { size: 'medium', label: 'Medium', dims: '10×10 ft', desc: 'Furniture, appliances' },
          { size: 'large', label: 'Large', dims: '20×20 ft', desc: 'Vehicles, bulk goods' },
          { size: 'extra_large', label: 'Extra Large', dims: '30×30 ft', desc: 'Industrial storage' },
        ].map((s) => (
          <button
            key={s.size}
            onClick={() => setSizeFilter(s.size === sizeFilter ? 'all' : s.size)}
            className={`p-4 rounded-xl border text-left text-sm transition ${sizeFilter === s.size ? 'border-blue-500 bg-blue-50' : 'border-slate-200 bg-white hover:border-blue-300'}`}
          >
            <div className="flex items-center gap-1.5 mb-1">
              <Ruler size={13} className="text-blue-500" />
              <span className="font-semibold text-slate-700">{s.label}</span>
            </div>
            <div className="text-blue-700 font-bold">{s.dims}</div>
            <div className="text-slate-400 text-xs mt-1">{s.desc}</div>
          </button>
        ))}
      </div>

      {filtered.length === 0 ? (
        <div className="text-center py-20 text-slate-400">
          <Package size={48} className="mx-auto mb-4 opacity-40" />
          <p className="text-lg font-medium">No storage units found</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 xl:grid-cols-4 gap-6">
          {filtered.map((u) => (
            <div key={u.id} className="bg-white border rounded-2xl overflow-hidden card-hover flex flex-col">
              <div className="h-36 bg-gradient-to-br from-purple-50 to-violet-100 flex flex-col items-center justify-center relative p-4">
                <Package size={40} className="text-purple-400 mb-2" />
                <span className="text-purple-600 font-bold text-lg">{sizeLabel(u.size)}</span>
                <span className={`badge ${statusColor(u.status)} absolute top-3 right-3`}>
                  {u.status || 'Available'}
                </span>
              </div>
              <div className="p-4 flex flex-col flex-1">
                <h3 className="font-semibold text-slate-800 mb-1">Unit {u.unit_number || `#${u.id}`}</h3>
                <p className="text-xs text-slate-400 flex items-center gap-1 mb-3">
                  <MapPin size={11} /> {u.location || 'Warehouse A'} · Climate: {u.climate_controlled ? 'Controlled ❄️' : 'Standard'}
                </p>

                <div className="grid grid-cols-2 gap-2 text-xs mb-4">
                  <div className="bg-slate-50 rounded-lg p-2 text-center">
                    <div className="font-bold text-slate-700">₹{u.daily_rate || '—'}</div>
                    <div className="text-slate-400">/ day</div>
                  </div>
                  <div className="bg-purple-50 rounded-lg p-2 text-center">
                    <div className="font-bold text-purple-700">₹{u.monthly_rate || '—'}</div>
                    <div className="text-slate-400">/ month</div>
                  </div>
                </div>

                <button
                  onClick={() => handleAdd(u)}
                  disabled={u.status === 'occupied'}
                  className={`flex items-center justify-center gap-2 text-sm font-semibold px-4 py-2.5 rounded-xl transition ${
                    added === u.id
                      ? 'bg-green-100 text-green-700'
                      : u.status === 'occupied'
                      ? 'bg-slate-100 text-slate-400 cursor-not-allowed'
                      : 'bg-purple-600 text-white hover:bg-purple-700'
                  }`}
                >
                  <ShoppingCart size={14} />
                  {added === u.id ? 'Added!' : u.status === 'occupied' ? 'Not Available' : 'Book Unit'}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
