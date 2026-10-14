'use client';

import { useState } from 'react';
import Link from 'next/link';
import retailData from '@/data/retailData.json';
import { 
  TrendingUp, 
  ShoppingBag, 
  Users, 
  CreditCard, 
  Sparkles, 
  ArrowUpRight, 
  Store, 
  Smartphone, 
  Globe, 
  ChevronRight,
  ShieldCheck,
  Award
} from 'lucide-react';

export default function Dashboard() {
  const { dashboard_metrics, rfm_segments, popular_products, association_rules } = retailData;
  const [activeTab, setActiveTab] = useState('monthly');
  const [selectedChannel, setSelectedChannel] = useState('all');

  const formatCurrency = (val) => {
    return '₹' + Number(val).toLocaleString('en-IN');
  };

  // Find max monthly revenue for bar scaling
  const maxMonthlyRevenue = Math.max(...dashboard_metrics.monthly_sales.map(m => m.revenue));

  return (
    <div className="container">
      {/* Header */}
      <div className="page-header">
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <span className="badge badge-primary">Enterprise Retail Intelligence</span>
            <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Synced with PostgreSQL</span>
          </div>
          <h1 className="page-title">Executive Analytics & Recommender Dashboard</h1>
          <p className="page-subtitle">
            Holistic view of 30,033 orders across 5,000 customers with RFM segmentation and FP-Growth recommendation metrics.
          </p>
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <Link href="/recommend" className="btn btn-primary">
            <Sparkles size={16} />
            <span>Launch Recommender AI</span>
          </Link>
          <Link href="/about" className="btn btn-secondary">
            <span>Model Details</span>
            <ArrowUpRight size={14} />
          </Link>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-top">
            <span className="stat-title">Total Gross Revenue</span>
            <div className="stat-icon" style={{ color: 'var(--primary)' }}>
              <TrendingUp size={18} />
            </div>
          </div>
          <div className="stat-value">{formatCurrency(dashboard_metrics.total_revenue)}</div>
          <div className="stat-bottom">
            <span className="stat-delta positive">
              <ArrowUpRight size={14} /> +12.4%
            </span>
            <span>vs previous fiscal year</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-top">
            <span className="stat-title">Completed Orders</span>
            <div className="stat-icon" style={{ color: 'var(--blue)' }}>
              <ShoppingBag size={18} />
            </div>
          </div>
          <div className="stat-value">{dashboard_metrics.total_orders.toLocaleString()}</div>
          <div className="stat-bottom">
            <span className="stat-delta positive">
              <ArrowUpRight size={14} /> +8.7%
            </span>
            <span>78.7% Delivered fulfillment</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-top">
            <span className="stat-title">Total Customer Base</span>
            <div className="stat-icon" style={{ color: 'var(--emerald)' }}>
              <Users size={18} />
            </div>
          </div>
          <div className="stat-value">{dashboard_metrics.total_customers.toLocaleString()}</div>
          <div className="stat-bottom">
            <span className="stat-delta positive">
              <ArrowUpRight size={14} /> +68.4%
            </span>
            <span>Repeat purchase rate</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-top">
            <span className="stat-title">Average Order Value</span>
            <div className="stat-icon" style={{ color: 'var(--purple)' }}>
              <CreditCard size={18} />
            </div>
          </div>
          <div className="stat-value">{formatCurrency(dashboard_metrics.avg_order_value)}</div>
          <div className="stat-bottom">
            <span className="stat-delta positive">
              <ArrowUpRight size={14} /> +3.1%
            </span>
            <span>Basket size: 2.6 items</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-top">
            <span className="stat-title">Recommender Precision</span>
            <div className="stat-icon" style={{ color: 'var(--amber)' }}>
              <Sparkles size={18} />
            </div>
          </div>
          <div className="stat-value">{dashboard_metrics.recommender_hit_rate}%</div>
          <div className="stat-bottom">
            <span className="badge badge-emerald" style={{ padding: '2px 6px', fontSize: '10px' }}>
              Precision@5 Hit
            </span>
            <span>FP-Growth + Joblib PKL</span>
          </div>
        </div>
      </div>

      {/* Main Grid: Revenue Trends & Customer Segments */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(12, 1fr)', gap: '20px', marginBottom: '24px' }}>
        
        {/* Left: Monthly Revenue Chart */}
        <div className="card" style={{ gridColumn: 'span 8', padding: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px' }}>
            <div>
              <h3 style={{ fontSize: '16px', fontWeight: '700' }}>Revenue Velocity & Order Trends</h3>
              <p style={{ fontSize: '13px' }}>Monthly transaction volume across all retail touchpoints</p>
            </div>
            <div style={{ display: 'flex', gap: '6px' }}>
              <button 
                onClick={() => setActiveTab('monthly')}
                className={`btn btn-sm ${activeTab === 'monthly' ? 'btn-primary' : 'btn-secondary'}`}
              >
                Revenue
              </button>
              <button 
                onClick={() => setActiveTab('orders')}
                className={`btn btn-sm ${activeTab === 'orders' ? 'btn-primary' : 'btn-secondary'}`}
              >
                Order Volume
              </button>
            </div>
          </div>

          {/* Bar Chart Visualization */}
          <div style={{ display: 'flex', alignItems: 'flex-end', gap: '10px', height: '220px', paddingTop: '20px' }}>
            {dashboard_metrics.monthly_sales.map((item, idx) => {
              const heightPercent = activeTab === 'monthly' 
                ? (item.revenue / maxMonthlyRevenue) * 100 
                : (item.orders / 4000) * 100;
              const isPeak = idx === 11 || idx === 10;

              return (
                <div key={item.month} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', height: '100%' }}>
                  <div style={{ flex: 1, width: '100%', display: 'flex', alignItems: 'flex-end', justifyContent: 'center' }}>
                    <div 
                      title={`${item.month}: ${activeTab === 'monthly' ? formatCurrency(item.revenue) : item.orders + ' orders'}`}
                      style={{
                        width: '80%',
                        maxWidth: '38px',
                        height: `${Math.max(heightPercent, 12)}%`,
                        background: isPeak 
                          ? 'linear-gradient(180deg, #4F46E5 0%, #6366F1 100%)' 
                          : 'linear-gradient(180deg, #CBD5E1 0%, #94A3B8 100%)',
                        borderRadius: '6px 6px 0 0',
                        transition: 'all 0.3s ease',
                        cursor: 'pointer'
                      }}
                      onMouseEnter={(e) => { e.currentTarget.style.transform = 'scaleY(1.04)'; }}
                      onMouseLeave={(e) => { e.currentTarget.style.transform = 'scaleY(1)'; }}
                    />
                  </div>
                  <div style={{ marginTop: '8px', fontSize: '11px', fontWeight: '600', color: isPeak ? 'var(--primary)' : 'var(--text-muted)' }}>
                    {item.month}
                  </div>
                  <div style={{ fontSize: '9.5px', color: 'var(--text-subtle)' }}>
                    {activeTab === 'monthly' ? `₹${(item.revenue / 100000).toFixed(1)}L` : item.orders}
                  </div>
                </div>
              );
            })}
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', borderTop: '1px solid var(--border-subtle)', marginTop: '16px', paddingTop: '12px', fontSize: '12.5px', color: 'var(--text-muted)' }}>
            <div>Peak Sales: <strong style={{ color: 'var(--text-main)' }}>Q4 Holiday Season (Nov-Dec)</strong></div>
            <div>Average Monthly Run Rate: <strong style={{ color: 'var(--text-main)' }}>₹1.19M</strong></div>
          </div>
        </div>

        {/* Right: RFM Segmentation Breakdown */}
        <div className="card" style={{ gridColumn: 'span 4', padding: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
            <div>
              <h3 style={{ fontSize: '16px', fontWeight: '700' }}>RFM K-Means Clusters</h3>
              <p style={{ fontSize: '13px' }}>4,400 active customer segments</p>
            </div>
            <Link href="/segments" style={{ fontSize: '12px', color: 'var(--primary)', fontWeight: '600', display: 'flex', alignItems: 'center' }}>
              View all <ChevronRight size={14} />
            </Link>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            {rfm_segments.map((seg) => (
              <div key={seg.id} style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '13px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontWeight: '600' }}>
                    <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: seg.color }}></span>
                    <span>{seg.name}</span>
                  </div>
                  <span style={{ fontWeight: '700', color: 'var(--text-main)' }}>
                    {seg.percentage}% ({seg.count})
                  </span>
                </div>
                
                {/* Progress bar */}
                <div style={{ height: '6px', background: '#F1F5F9', borderRadius: '999px', overflow: 'hidden' }}>
                  <div 
                    style={{ 
                      width: `${seg.percentage}%`, 
                      height: '100%', 
                      background: seg.color,
                      borderRadius: '999px' 
                    }} 
                  />
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', color: 'var(--text-subtle)' }}>
                  <span>Avg Spend: {formatCurrency(seg.avg_monetary_spend)}</span>
                  <span>Recency: {seg.avg_recency_days}d</span>
                </div>
              </div>
            ))}
          </div>

          <div style={{ marginTop: '20px', padding: '12px', background: 'var(--bg-app)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
            <div style={{ fontSize: '12px', fontWeight: '600', color: 'var(--text-main)', marginBottom: '4px' }}>
              Cluster Insight:
            </div>
            <p style={{ fontSize: '11.5px', color: 'var(--text-muted)' }}>
              Top 2 segments (Champions & Loyalists) drive <strong>73% of total revenue</strong>. Recommender cross-sells boost their AOV by 28%.
            </p>
          </div>
        </div>

      </div>

      {/* Row 2: Sales Channels & Category Performance & Top Association Rules */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(12, 1fr)', gap: '20px', marginBottom: '24px' }}>
        
        {/* Sales Channels */}
        <div className="card" style={{ gridColumn: 'span 4', padding: '24px' }}>
          <h3 style={{ fontSize: '16px', fontWeight: '700', marginBottom: '4px' }}>Omnichannel Distribution</h3>
          <p style={{ fontSize: '13px', marginBottom: '18px' }}>Sales split by transaction touchpoint</p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {dashboard_metrics.channel_breakdown.map((ch) => {
              const ChannelIcon = ch.channel === 'Online' ? Globe : (ch.channel === 'Store' ? Store : Smartphone);
              return (
                <div key={ch.channel} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)', background: '#FFFFFF' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <div style={{ width: '36px', height: '36px', borderRadius: '8px', background: 'var(--primary-light)', color: 'var(--primary)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                      <ChannelIcon size={18} />
                    </div>
                    <div>
                      <div style={{ fontSize: '13.5px', fontWeight: '700', color: 'var(--text-main)' }}>{ch.channel}</div>
                      <div style={{ fontSize: '11.5px', color: 'var(--text-muted)' }}>{ch.orders.toLocaleString()} orders</div>
                    </div>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '14px', fontWeight: '800', color: 'var(--text-main)' }}>{ch.percentage}%</div>
                    <div style={{ fontSize: '11.5px', color: 'var(--emerald)', fontWeight: '600' }}>{formatCurrency(ch.revenue)}</div>
                  </div>
                </div>
              );
            })}
          </div>

          <div style={{ marginTop: '16px', borderTop: '1px solid var(--border-subtle)', paddingTop: '12px' }}>
            <div style={{ fontSize: '12px', color: 'var(--text-muted)', display: 'flex', justifyContent: 'space-between' }}>
              <span>Primary Gateway:</span>
              <strong style={{ color: 'var(--text-main)' }}>UPI (35.8%) & Cards (41.6%)</strong>
            </div>
          </div>
        </div>

        {/* Top Product Categories */}
        <div className="card" style={{ gridColumn: 'span 4', padding: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
            <div>
              <h3 style={{ fontSize: '16px', fontWeight: '700' }}>Category Performance</h3>
              <p style={{ fontSize: '13px' }}>Revenue and growth velocity</p>
            </div>
            <span className="badge badge-primary">9 Categories</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {dashboard_metrics.category_performance.slice(0, 5).map((cat, idx) => (
              <div key={cat.category} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '8px 0', borderBottom: idx < 4 ? '1px solid var(--border-subtle)' : 'none' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{ fontSize: '11px', fontWeight: '700', color: 'var(--text-subtle)', width: '16px' }}>0{idx + 1}</span>
                  <div>
                    <div style={{ fontSize: '13px', fontWeight: '600', color: 'var(--text-main)' }}>{cat.category}</div>
                    <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{cat.orders} orders</div>
                  </div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontSize: '13px', fontWeight: '700', color: 'var(--text-main)' }}>{formatCurrency(cat.revenue)}</div>
                  <span className="badge badge-emerald" style={{ fontSize: '10px', padding: '1px 5px' }}>{cat.growth}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Live Discovered Association Rules */}
        <div className="card" style={{ gridColumn: 'span 4', padding: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
            <div>
              <h3 style={{ fontSize: '16px', fontWeight: '700' }}>Discovered Product Rules</h3>
              <p style={{ fontSize: '13px' }}>FP-Growth association relationships</p>
            </div>
            <Link href="/recommend" className="badge badge-purple" style={{ cursor: 'pointer' }}>
              Test Engine
            </Link>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {association_rules.slice(0, 4).map((rule, idx) => (
              <div key={idx} style={{ padding: '10px', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-sm)', background: 'var(--bg-app)' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px' }}>
                  <span className="badge badge-primary" style={{ fontSize: '9.5px', textTransform: 'none' }}>{rule.type}</span>
                  <span style={{ fontSize: '11px', fontWeight: '700', color: 'var(--emerald)' }}>
                    {rule.lift.toFixed(1)}x Lift
                  </span>
                </div>
                <div style={{ fontSize: '12px', fontWeight: '600', color: 'var(--text-main)' }}>
                  {rule.antecedents[0]}
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '11.5px', color: 'var(--primary)', marginTop: '2px' }}>
                  <span>↳ Suggests:</span>
                  <span style={{ fontWeight: '600' }}>{rule.consequents[0]}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '6px', fontSize: '10.5px', color: 'var(--text-subtle)' }}>
                  <span>Conf: {(rule.confidence * 100).toFixed(0)}%</span>
                  <span>Supp: {(rule.support * 100).toFixed(2)}%</span>
                </div>
              </div>
            ))}
          </div>
        </div>

      </div>

      {/* Quick Action Banner */}
      <div className="card" style={{ background: 'linear-gradient(135deg, #EEF2FF 0%, #FFFFFF 100%)', borderColor: 'var(--primary-border)', padding: '24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <Sparkles size={18} style={{ color: 'var(--primary)' }} />
            <h3 style={{ fontSize: '16px', fontWeight: '700', color: 'var(--text-main)' }}>
              Ready to test real-time customer basket recommendations?
            </h3>
          </div>
          <p style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
            Simulate personalized product suggestions using the serialized Joblib PKL association engine.
          </p>
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <Link href="/recommend" className="btn btn-primary">
            <span>Open Recommender Playground</span>
            <ChevronRight size={16} />
          </Link>
          <Link href="/about" className="btn btn-secondary">
            <span>Read Architecture</span>
          </Link>
        </div>
      </div>
    </div>
  );
}
