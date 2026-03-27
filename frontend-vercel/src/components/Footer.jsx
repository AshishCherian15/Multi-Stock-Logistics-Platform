import Link from 'next/link';
import { Warehouse, Mail, MapPin, Phone } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="bg-slate-900 text-slate-300 mt-16">
      <div className="max-w-7xl mx-auto px-4 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div>
            <div className="flex items-center gap-2 mb-4">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <Warehouse size={16} color="white" />
              </div>
              <span className="font-bold text-white text-lg">MultiStock</span>
            </div>
            <p className="text-sm leading-relaxed text-slate-400">
              Enterprise-grade warehouse and logistics management platform. Products,
              rentals, storage, and smart lockers — all in one place.
            </p>
          </div>

          <div>
            <h4 className="font-semibold text-white mb-4">Services</h4>
            <ul className="space-y-2 text-sm">
              {[
                { href: '/products', label: 'Marketplace' },
                { href: '/rentals', label: 'Equipment Rentals' },
                { href: '/storage', label: 'Storage Units' },
                { href: '/lockers', label: 'Smart Lockers' },
              ].map((l) => (
                <li key={l.href}>
                  <Link href={l.href} className="hover:text-blue-400 transition">
                    {l.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h4 className="font-semibold text-white mb-4">Platform</h4>
            <ul className="space-y-2 text-sm">
              {[
                { href: '/dashboard', label: 'Dashboard' },
                { href: '/cart', label: 'Cart' },
                { href: '/checkout', label: 'Checkout' },
              ].map((l) => (
                <li key={l.href}>
                  <Link href={l.href} className="hover:text-blue-400 transition">
                    {l.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h4 className="font-semibold text-white mb-4">Contact</h4>
            <ul className="space-y-2 text-sm">
              <li className="flex items-center gap-2"><MapPin size={14} /> Bengaluru, Karnataka, India</li>
              <li className="flex items-center gap-2"><Mail size={14} /> support@multistock.com</li>
              <li className="flex items-center gap-2"><Phone size={14} /> +91 98765 43210</li>
            </ul>
          </div>
        </div>

        <div className="border-t border-slate-700 mt-8 pt-6 flex flex-col md:flex-row justify-between items-center gap-4 text-sm text-slate-500">
          <span>© 2026 MultiStock Logistics Platform. Final Year Project — USN: 4KM22CS018</span>
          <span>Built with Next.js + Tailwind CSS · Deployed on Vercel</span>
        </div>
      </div>
    </footer>
  );
}
