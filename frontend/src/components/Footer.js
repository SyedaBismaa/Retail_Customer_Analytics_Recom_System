import Link from 'next/link';
import { Database, Cpu, Sparkles, Layers } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="footer">
      <div className="container">
        <div className="footer-inner">
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <div style={{ fontWeight: '700', color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span>Retail Customer Analytics & Recommendation Engine</span>
              <span className="badge badge-primary">v2.4</span>
            </div>
            <p style={{ fontSize: '12.5px', color: 'var(--text-muted)' }}>
              End-to-End Retail Intelligence powered by PostgreSQL, K-Means RFM Segmentation, FP-Growth Association Rules & Joblib.
            </p>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '20px', fontSize: '12.5px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--text-muted)' }}>
              <Database size={14} style={{ color: 'var(--primary)' }} />
              <span>PostgreSQL + SQLAlchemy</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--text-muted)' }}>
              <Layers size={14} style={{ color: 'var(--emerald)' }} />
              <span>RFM + PCA + K-Means</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--text-muted)' }}>
              <Cpu size={14} style={{ color: 'var(--purple)' }} />
              <span>Joblib .pkl Model</span>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
