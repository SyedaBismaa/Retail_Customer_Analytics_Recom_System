'use client';

import { useState } from 'react';
import retailData from '@/data/retailData.json';
import Link from 'next/link';
import { 
  Users, 
  Target, 
  ArrowUpRight, 
  Sparkles, 
  ShoppingBag, 
  Award, 
  Calendar, 
  IndianRupee, 
  CheckCircle2, 
  Filter,
  Layers,
  ChevronRight
} from 'lucide-react';

export default function SegmentsPage() {
  const { rfm_segments, sample_customers } = retailData;
  const [selectedSegmentId, setSelectedSegmentId] = useState('cluster_0');
  const [tierFilter, setTierFilter] = useState('All');

  const formatCurrency = (val) => '₹' + Number(val).toLocaleString('en-IN');

  const selectedSegment = rfm_segments.find(s => s.id === selectedSegmentId) || rfm_segments[0];

  // Filter sample customers
  const filteredCustomers = sample_customers.filter(c => {
    const matchTier = tierFilter === 'All' || c.loyalty_tier === tierFilter;
    return matchTier;
  });

  return (
    <div className="container">
      {/* Header */}
      <div className="page-header">
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <span className="badge badge-primary">Unsupervised Machine Learning</span>
            <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>PCA + Yeo-Johnson + K-Means (k=4)</span>
          </div>
          <h1 className="page-title">RFM Customer Segmentation & Behavioral Clusters</h1>
          <p className="page-subtitle">
            Customer lifetime value mapping using Recency, Frequency, and Monetary scores across 5,000 retail consumers.
          </p>
        </div>

        <Link href="/recommend" className="btn btn-primary">
          <Sparkles size={16} />
          <span>Cross-Sell Recommender</span>
        </Link>
      </div>

      {/* Segments High-Level Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '18px', marginBottom: '28px' }}>
        {rfm_segments.map(seg => {
          const isSelected = selectedSegmentId === seg.id;
          return (
            <div
              key={seg.id}
              onClick={() => setSelectedSegmentId(seg.id)}
              className="card"
              style={{
                padding: '20px',
                cursor: 'pointer',
                borderColor: isSelected ? seg.color : 'var(--border-card)',
                boxShadow: isSelected ? `0 0 0 1px ${seg.color}, var(--shadow-md)` : 'var(--shadow-sm)',
                background: isSelected ? 'linear-gradient(180deg, #FFFFFF 0%, #FAFAFC 100%)' : '#FFFFFF',
                position: 'relative',
                overflow: 'hidden'
              }}
            >
              <div style={{ width: '4px', height: '100%', position: 'absolute', left: 0, top: 0, backgroundColor: seg.color }}></div>

              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px' }}>
                <span className="badge" style={{ backgroundColor: `${seg.color}15`, color: seg.color, border: `1px solid ${seg.color}35` }}>
                  {seg.badge}
                </span>
                <span style={{ fontSize: '18px', fontWeight: '800', color: 'var(--text-main)' }}>
                  {seg.percentage}%
                </span>
              </div>

              <h3 style={{ fontSize: '16px', fontWeight: '700', marginBottom: '6px' }}>{seg.name}</h3>
              <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '16px', height: '36px', overflow: 'hidden' }}>
                {seg.description}
              </p>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '8px', paddingTop: '12px', borderTop: '1px solid var(--border-subtle)', textAlign: 'center' }}>
                <div>
                  <div style={{ fontSize: '10px', color: 'var(--text-subtle)', textTransform: 'uppercase' }}>Recency</div>
                  <div style={{ fontSize: '13px', fontWeight: '700', color: 'var(--text-main)' }}>{seg.avg_recency_days}d</div>
                </div>
                <div>
                  <div style={{ fontSize: '10px', color: 'var(--text-subtle)', textTransform: 'uppercase' }}>Frequency</div>
                  <div style={{ fontSize: '13px', fontWeight: '700', color: 'var(--text-main)' }}>{seg.avg_frequency_orders}x</div>
                </div>
                <div>
                  <div style={{ fontSize: '10px', color: 'var(--text-subtle)', textTransform: 'uppercase' }}>Avg Spend</div>
                  <div style={{ fontSize: '13px', fontWeight: '700', color: 'var(--text-main)' }}>{formatCurrency(seg.avg_monetary_spend)}</div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Selected Segment Deep Dive */}
      <div className="card" style={{ padding: '28px', marginBottom: '28px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '14px', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '18px', marginBottom: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{ width: '40px', height: '40px', borderRadius: '10px', background: `${selectedSegment.color}20`, color: selectedSegment.color, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Target size={22} />
            </div>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <h2 style={{ fontSize: '20px', fontWeight: '800' }}>{selectedSegment.name}</h2>
                <span className="badge" style={{ backgroundColor: `${selectedSegment.color}15`, color: selectedSegment.color }}>
                  {selectedSegment.count} Customers
                </span>
              </div>
              <p style={{ fontSize: '13.5px', color: 'var(--text-muted)' }}>{selectedSegment.description}</p>
            </div>
          </div>

          <div style={{ display: 'flex', gap: '12px' }}>
            <div style={{ padding: '8px 16px', background: 'var(--bg-app)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)', textAlign: 'right' }}>
              <div style={{ fontSize: '11px', color: 'var(--text-subtle)' }}>Total Segment Value</div>
              <div style={{ fontSize: '16px', fontWeight: '800', color: selectedSegment.color }}>
                {formatCurrency(selectedSegment.count * selectedSegment.avg_monetary_spend)}
              </div>
            </div>
          </div>
        </div>

        {/* Actionable Strategy Section */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(12, 1fr)', gap: '20px' }}>
          <div style={{ gridColumn: 'span 7', display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <h4 style={{ fontSize: '14.5px', fontWeight: '700', color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Target size={16} style={{ color: selectedSegment.color }} />
              <span>Prescribed Marketing Strategy & Retention Playbook</span>
            </h4>
            <div style={{ padding: '16px', background: 'var(--bg-app)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
              <p style={{ fontSize: '13.5px', color: 'var(--text-main)', lineHeight: '1.6', marginBottom: '10px' }}>
                {selectedSegment.strategy}
              </p>
              <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                <span className="badge badge-primary">Personalized Recommender Engine</span>
                <span className="badge badge-emerald">Dynamic Tier Pricing</span>
                <span className="badge badge-blue">Category Cross-Sell</span>
              </div>
            </div>
          </div>

          <div style={{ gridColumn: 'span 5', display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <h4 style={{ fontSize: '14.5px', fontWeight: '700', color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Layers size={16} style={{ color: 'var(--primary)' }} />
              <span>Cluster RFM Centroids</span>
            </h4>
            <div style={{ padding: '14px', background: 'var(--bg-app)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)', display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '12.5px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-muted)' }}>Recency Window:</span>
                <strong style={{ color: 'var(--text-main)' }}>&lt; {selectedSegment.avg_recency_days} Days</strong>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-muted)' }}>Order Cadence:</span>
                <strong style={{ color: 'var(--text-main)' }}>{selectedSegment.avg_frequency_orders} purchases/year</strong>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-muted)' }}>Customer Lifetime Value:</span>
                <strong style={{ color: 'var(--text-main)' }}>{formatCurrency(selectedSegment.avg_monetary_spend)}</strong>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Customer Explorer Table */}
      <div className="card" style={{ padding: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '18px', flexWrap: 'wrap', gap: '12px' }}>
          <div>
            <h3 style={{ fontSize: '17px', fontWeight: '700' }}>Sample Customer Profiles & Order History</h3>
            <p style={{ fontSize: '13px' }}>Direct from cleaned dataset with real purchase baskets</p>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Filter Loyalty:</span>
            {['All', 'Platinum', 'Gold', 'Silver', 'Bronze'].map(tier => (
              <button
                key={tier}
                onClick={() => setTierFilter(tier)}
                className={`btn btn-sm ${tierFilter === tier ? 'btn-primary' : 'btn-secondary'}`}
              >
                {tier}
              </button>
            ))}
          </div>
        </div>

        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '13px' }}>
            <thead>
              <tr style={{ borderBottom: '2px solid var(--border-subtle)', color: 'var(--text-muted)' }}>
                <th style={{ padding: '10px 12px', fontWeight: '600' }}>Customer</th>
                <th style={{ padding: '10px 12px', fontWeight: '600' }}>Loyalty Tier</th>
                <th style={{ padding: '10px 12px', fontWeight: '600' }}>RFM Segment</th>
                <th style={{ padding: '10px 12px', fontWeight: '600' }}>Location</th>
                <th style={{ padding: '10px 12px', fontWeight: '600' }}>Total Spend</th>
                <th style={{ padding: '10px 12px', fontWeight: '600' }}>Purchased Products Sample</th>
                <th style={{ padding: '10px 12px', fontWeight: '600', textAlign: 'right' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredCustomers.map(cust => (
                <tr key={cust.customer_id} style={{ borderBottom: '1px solid var(--border-subtle)', transition: 'background 0.15s ease' }}>
                  <td style={{ padding: '12px' }}>
                    <div style={{ fontWeight: '700', color: 'var(--text-main)' }}>{cust.name}</div>
                    <div style={{ fontSize: '11px', color: 'var(--text-subtle)' }}>{cust.customer_id}</div>
                  </td>
                  <td style={{ padding: '12px' }}>
                    <span className={`badge ${cust.loyalty_tier === 'Platinum' ? 'badge-purple' : (cust.loyalty_tier === 'Gold' ? 'badge-amber' : 'badge-primary')}`}>
                      {cust.loyalty_tier}
                    </span>
                  </td>
                  <td style={{ padding: '12px' }}>
                    <span style={{ fontWeight: '600', color: 'var(--text-main)' }}>{cust.segment}</span>
                  </td>
                  <td style={{ padding: '12px', color: 'var(--text-muted)' }}>
                    {cust.city}, {cust.state}
                  </td>
                  <td style={{ padding: '12px', fontWeight: '700', color: 'var(--text-main)' }}>
                    {formatCurrency(cust.total_spend)}
                  </td>
                  <td style={{ padding: '12px', maxWidth: '320px' }}>
                    <div style={{ display: 'flex', gap: '4px', flexWrap: 'wrap' }}>
                      {cust.purchased_products.slice(0, 3).map((prod, idx) => (
                        <span key={idx} style={{ fontSize: '11px', padding: '2px 6px', background: 'var(--bg-app)', border: '1px solid var(--border-subtle)', borderRadius: '4px', whiteSpace: 'nowrap' }}>
                          {prod}
                        </span>
                      ))}
                      {cust.purchased_products.length > 3 && (
                        <span style={{ fontSize: '11px', color: 'var(--text-subtle)' }}>
                          +{cust.purchased_products.length - 3} more
                        </span>
                      )}
                    </div>
                  </td>
                  <td style={{ padding: '12px', textAlign: 'right' }}>
                    <Link href="/recommend" className="btn btn-secondary btn-sm" style={{ color: 'var(--primary)' }}>
                      <span>Test Recs</span>
                      <ChevronRight size={12} />
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
