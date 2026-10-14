'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { LayoutDashboard, Sparkles, Users, Info, ShoppingBag } from 'lucide-react';

export default function Navbar() {
  const pathname = usePathname();

  const navItems = [
    { href: '/', label: 'Dashboard', icon: LayoutDashboard },
    { href: '/recommend', label: 'Recommender AI', icon: Sparkles },
    { href: '/segments', label: 'RFM Segments', icon: Users },
    { href: '/about', label: 'About Project', icon: Info },
  ];

  return (
    <header className="navbar">
      <div className="container">
        <div className="navbar-inner">
          <Link href="/" className="brand">
            <div className="brand-icon">
              <ShoppingBag size={20} strokeWidth={2.2} />
            </div>
            <div>
              <span>RetailPulse</span>
              <span style={{ color: 'var(--primary)', marginLeft: '4px', fontWeight: '800' }}>AI</span>
            </div>
          </Link>

          <nav className="nav-links">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`nav-item ${isActive ? 'active' : ''}`}
                >
                  <Icon size={16} strokeWidth={isActive ? 2.2 : 1.8} />
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </nav>

          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div className="nav-badge">
              <span className="pulse-dot"></span>
              <span>Model: Joblib PKL Ready</span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
