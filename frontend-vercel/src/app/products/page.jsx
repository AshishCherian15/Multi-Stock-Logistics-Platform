'use client';
import { useState, useEffect } from 'react';
import { Package, Search, ShoppingCart, Filter } from 'lucide-react';
import { loadAllData, filterByModel } from '../../lib/dataLoader';
import { addToCart } from '../../lib/cart';

export default function ProductsPage() {
  const [products, setProducts] = useState([]);
  const [filtered, setFiltered] = useState([]);
  const [query, setQuery] = useState('');
  const [sortBy, setSortBy] = useState('name');
  const [added, setAdded] = useState(null);

  useEffect(() => {
    loadAllData().then((data) => {
      const p = filterByModel(data, 'goods.listmodel');
      setProducts(p);
      setFiltered(p);
    });
  }, []);

  useEffect(() => {
    let result = products.filter((p) =>
      (p.goods_desc || p.goods_name || '').toLowerCase().includes(query.toLowerCase()) ||
      (p.goods_code || '').toLowerCase().includes(query.toLowerCase())
    );
    if (sortBy === 'price_asc') result = [...result].sort((a, b) => (parseFloat(a.goods_price) || 0) - (parseFloat(b.goods_price) || 0));
    if (sortBy === 'price_desc') result = [...result].sort((a, b) => (parseFloat(b.goods_price) || 0) - (parseFloat(a.goods_price) || 0));
    if (sortBy === 'stock') result = [...result].sort((a, b) => (b.onhand_stock || 0) - (a.onhand_stock || 0));
    setFiltered(result);
  }, [query, sortBy, products]);

  const handleAdd = (p) => {
    addToCart({
      id: p.id,
      type: 'product',
      name: p.goods_desc || p.goods_name || 'Product',
      price: p.goods_price || 0,
      sku: p.goods_code,
    });
    setAdded(p.id);
    setTimeout(() => setAdded(null), 1500);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-10">
      {/* Header */}
      <div className="mb-8">
        <h1 className="section-heading">Product Marketplace</h1>
        <p className="text-slate-500">Browse {products.length} products from verified suppliers</p>
      </div>

      {/* Filters */}
      <div className="bg-white border rounded-2xl p-4 mb-8 flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Search products..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2.5 border rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-300"
          />
        </div>
        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value)}
          className="px-4 py-2.5 border rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-300"
        >
          <option value="name">Sort: Name</option>
          <option value="price_asc">Price: Low → High</option>
          <option value="price_desc">Price: High → Low</option>
          <option value="stock">Most Stock</option>
        </select>
        <div className="flex items-center gap-2 text-sm text-slate-400">
          <Filter size={14} />
          {filtered.length} results
        </div>
      </div>

      {/* Grid */}
      {filtered.length === 0 ? (
        <div className="text-center py-20 text-slate-400">
          <Package size={48} className="mx-auto mb-4 opacity-40" />
          <p className="text-lg font-medium">No products found</p>
          <p className="text-sm">Try changing your search query</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 xl:grid-cols-4 gap-6">
          {filtered.map((p) => (
            <div key={p.id} className="bg-white border rounded-2xl overflow-hidden card-hover flex flex-col">
              <div className="h-40 bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
                <Package size={48} className="text-blue-400" />
              </div>
              <div className="p-4 flex flex-col flex-1">
                <span className="badge badge-green text-xs mb-2">
                  {(p.onhand_stock ?? 0) > 0 ? 'In Stock' : 'Out of Stock'}
                </span>
                <h3 className="font-semibold text-slate-800 text-sm leading-snug mb-1 flex-1">
                  {p.goods_desc || p.goods_name || 'Product'}
                </h3>
                <p className="text-xs text-slate-400 mb-1">SKU: {p.goods_code || '—'}</p>
                <p className="text-xs text-slate-400 mb-3">Unit: {p.goods_unit || '—'} · Stock: {p.onhand_stock ?? '—'}</p>
                <div className="flex items-center justify-between mt-auto">
                  <span className="font-bold text-blue-700 text-lg">
                    ₹{p.goods_price || '0'}
                  </span>
                  <button
                    onClick={() => handleAdd(p)}
                    className={`flex items-center gap-1.5 text-xs font-semibold px-3 py-2 rounded-lg transition ${
                      added === p.id
                        ? 'bg-green-100 text-green-700'
                        : 'bg-blue-700 text-white hover:bg-blue-800'
                    }`}
                  >
                    <ShoppingCart size={13} />
                    {added === p.id ? 'Added!' : 'Add to Cart'}
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
