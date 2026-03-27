'use client';
import { useState, useEffect } from 'react';
import Link from 'next/link';
import { ShoppingCart, Package, Menu, X, Warehouse, Lock, Home, ChevronDown } from 'lucide-react';
import { getCartCount, getCart } from '../lib/cart';

export default function Header() {
  const [menuOpen, setMenuOpen] = useState(false);
  const [cartCount, setCartCount] = useState(0);

  useEffect(() => {
    const update = () => setCartCount(getCartCount(getCart()));
    update();
    window.addEventListener('cartUpdated', update);
    return () => window.removeEventListener('cartUpdated', update);
  }, []);

  const nav = [
    { href: '/', label: 'Home', icon: <Home size={15} /> },
    { href: '/products', label: 'Products', icon: <Package size={15} /> },
    { href: '/rentals', label: 'Rentals', icon: <Warehouse size={15} /> },
    { href: '/storage', label: 'Storage', icon: <Package size={15} /> },
    { href: '/lockers', label: 'Lockers', icon: <Lock size={15} /> },
  ];

  return (
    <header className="bg-white header-shadow sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2">
          <div className="w-9 h-9 bg-blue-700 rounded-lg flex items-center justify-center">
            <Warehouse size={20} color="white" />
          </div>
          <div>
            <span className="font-bold text-lg text-blue-700">MultiStock</span>
            <span className="block text-xs text-slate-500 -mt-1">Logistics Platform</span>
          </div>
        </Link>

        {/* Desktop nav */}
        <nav className="hidden md:flex items-center gap-1">
          {nav.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="flex items-center gap-1.5 px-3 py-2 rounded-md text-sm font-medium text-slate-600 hover:bg-blue-50 hover:text-blue-700 transition"
            >
              {item.icon}
              {item.label}
            </Link>
          ))}
        </nav>

        {/* Actions */}
        <div className="flex items-center gap-3">
          <Link
            href="/cart"
            className="relative flex items-center gap-1.5 bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-800 transition"
          >
            <ShoppingCart size={16} />
            Cart
            {cartCount > 0 && (
              <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center font-bold">
                {cartCount}
              </span>
            )}
          </Link>

          {/* Mobile hamburger */}
          <button
            className="md:hidden p-2 rounded-md text-slate-600 hover:bg-slate-100"
            onClick={() => setMenuOpen(!menuOpen)}
          >
            {menuOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>
      </div>

      {/* Mobile menu */}
      {menuOpen && (
        <div className="md:hidden border-t bg-white px-4 py-3 flex flex-col gap-2">
          {nav.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              onClick={() => setMenuOpen(false)}
              className="flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium text-slate-700 hover:bg-blue-50 hover:text-blue-700"
            >
              {item.icon}
              {item.label}
            </Link>
          ))}
        </div>
      )}
    </header>
  );
}
