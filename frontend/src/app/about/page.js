'use client';

import { useState } from 'react';
import Link from 'next/link';
import { 
  Database, 
  Cpu, 
  Sparkles, 
  Layers, 
  CheckCircle2, 
  Copy, 
  Check, 
  Code2, 
  BookOpen, 
  ChevronRight,
  TrendingUp,
  GitBranch,
  ShieldCheck
} from 'lucide-react';

export default function AboutPage() {
  const [copied, setCopied] = useState(false);

  const pythonSnippet = `# How to load and run the serialized Joblib model in Python:
import joblib

# 1. Load the serialized recommendation model
model = joblib.load('models/recommendation_engine.pkl')

# 2. Provide customer past purchases / current basket
basket = ["boAt Galaxy 200", "LEGO Superhero Toy 400"]

# 3. Generate top-5 ranked recommendations with confidence & lift
recommendations = model.recommend(basket, top_n=5)

for i, rec in enumerate(recommendations, 1):
    print(f"{i}. {rec['product_name']} | Source: {rec['source']} | Lift: {rec['lift']}")
`;

  const copyCode = () => {
    navigator.clipboard.writeText(pythonSnippet);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="container">
      {/* Header */}
      <div className="page-header">
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <span className="badge badge-primary">Technical Documentation</span>
            <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Machine Learning Architecture & Schema</span>
          </div>
          <h1 className="page-title">About the Retail Analytics & Recommendation System</h1>
          <p className="page-subtitle">
            Comprehensive overview of database modeling, RFM customer segmentation, FP-Growth association rules, and Joblib serialization.
          </p>
        </div>

        <Link href="/recommend" className="btn btn-primary">
          <Sparkles size={16} />
          <span>Launch Recommender</span>
        </Link>
      </div>

      {/* Architecture Cards Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '20px', marginBottom: '32px' }}>
        
        <div className="card" style={{ padding: '24px' }}>
          <div style={{ width: '40px', height: '40px', borderRadius: '10px', background: 'var(--primary-light)', color: 'var(--primary)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '14px' }}>
            <Database size={20} />
          </div>
          <h3 style={{ fontSize: '16px', fontWeight: '700', marginBottom: '6px' }}>1. PostgreSQL Relational Layer</h3>
          <p style={{ fontSize: '13px', color: 'var(--text-muted)', lineHeight: '1.6' }}>
            Normalizes 4 core entities: <strong>Customers</strong> (5,000 records), <strong>Products</strong> (208 SKUs), <strong>Orders</strong> (30,033 transactions), and <strong>Order Items</strong> (78,610 entries) using PostgreSQL and SQLAlchemy.
          </p>
        </div>

        <div className="card" style={{ padding: '24px' }}>
          <div style={{ width: '40px', height: '40px', borderRadius: '10px', background: 'var(--emerald-light)', color: 'var(--emerald)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '14px' }}>
            <Layers size={20} />
          </div>
          <h3 style={{ fontSize: '16px', fontWeight: '700', marginBottom: '6px' }}>2. RFM & K-Means Clustering</h3>
          <p style={{ fontSize: '13px', color: 'var(--text-muted)', lineHeight: '1.6' }}>
            Transforms customer purchasing history into Recency, Frequency, and Monetary scores. Skewness handled via Yeo-Johnson, scaled, and reduced with PCA (96.6% variance) into 4 distinct behavioral clusters.
          </p>
        </div>

        <div className="card" style={{ padding: '24px' }}>
          <div style={{ width: '40px', height: '40px', borderRadius: '10px', background: 'var(--amber-light)', color: 'var(--amber)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '14px' }}>
            <Sparkles size={20} />
          </div>
          <h3 style={{ fontSize: '16px', fontWeight: '700', marginBottom: '6px' }}>3. FP-Growth Association Mining</h3>
          <p style={{ fontSize: '13px', color: 'var(--text-muted)', lineHeight: '1.6' }}>
            Discovers frequent itemsets and co-purchase patterns with zero candidate generation overhead. Filtered by confidence &ge; 20% and lift &gt; 2.0x, backed by a popularity fallback engine.
          </p>
        </div>

        <div className="card" style={{ padding: '24px' }}>
          <div style={{ width: '40px', height: '40px', borderRadius: '10px', background: 'var(--purple-light)', color: 'var(--purple)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '14px' }}>
            <Cpu size={20} />
          </div>
          <h3 style={{ fontSize: '16px', fontWeight: '700', marginBottom: '6px' }}>4. Joblib PKL Serialization</h3>
          <p style={{ fontSize: '13px', color: 'var(--text-muted)', lineHeight: '1.6' }}>
            The trained association rules and K-Means segmentation pipeline are packaged into standalone binary files (<code style={{ fontSize: '12px' }}>.pkl</code>) via Python Joblib for high-speed sub-millisecond production inference.
          </p>
        </div>

      </div>

      {/* Code Snippet & Python Integration */}
      <div className="card" style={{ padding: '28px', marginBottom: '32px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px', flexWrap: 'wrap', gap: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Code2 size={20} style={{ color: 'var(--primary)' }} />
            <div>
              <h3 style={{ fontSize: '17px', fontWeight: '700' }}>Joblib Model Integration Snippet</h3>
              <p style={{ fontSize: '13px' }}>How the frontend and backend load the serialized model in production</p>
            </div>
          </div>

          <button 
            onClick={copyCode}
            className="btn btn-secondary btn-sm"
            style={{ display: 'flex', alignItems: 'center', gap: '6px' }}
          >
            {copied ? <Check size={14} style={{ color: 'var(--emerald)' }} /> : <Copy size={14} />}
            <span>{copied ? 'Copied to Clipboard' : 'Copy Python Code'}</span>
          </button>
        </div>

        <div style={{ background: '#0F172A', borderRadius: 'var(--radius-md)', padding: '20px', overflowX: 'auto', border: '1px solid #1E293B' }}>
          <pre style={{ margin: 0, fontFamily: 'var(--font-mono)', fontSize: '13px', color: '#E2E8F0', lineHeight: '1.6' }}>
            <code>{pythonSnippet}</code>
          </pre>
        </div>

        <div style={{ display: 'flex', gap: '20px', marginTop: '18px', paddingTop: '16px', borderTop: '1px solid var(--border-subtle)', flexWrap: 'wrap', fontSize: '12.5px', color: 'var(--text-muted)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <CheckCircle2 size={15} style={{ color: 'var(--emerald)' }} />
            <span>Artifact Location: <code style={{ color: 'var(--text-main)' }}>models/recommendation_engine.pkl</code></span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <CheckCircle2 size={15} style={{ color: 'var(--emerald)' }} />
            <span>Customer Model: <code style={{ color: 'var(--text-main)' }}>models/customer_segmentation.pkl</code></span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <CheckCircle2 size={15} style={{ color: 'var(--emerald)' }} />
            <span>Serialization Tool: <code style={{ color: 'var(--text-main)' }}>joblib 1.4+</code></span>
          </div>
        </div>
      </div>

      {/* Dataset & Methodology Table */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(12, 1fr)', gap: '24px' }}>
        
        {/* Dataset Breakdown */}
        <div className="card" style={{ gridColumn: 'span 6', padding: '24px' }}>
          <h3 style={{ fontSize: '16px', fontWeight: '700', marginBottom: '6px' }}>Dataset Specifications</h3>
          <p style={{ fontSize: '13px', marginBottom: '16px' }}>Cleaned and prepared tables in PostgreSQL</p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {[
              { name: 'customers.csv', records: '5,000 rows', cols: '10 features', desc: 'Demographics, location, occupation, loyalty tiers (Bronze to Platinum)' },
              { name: 'products.csv', records: '208 rows', cols: '10 features', desc: '9 categories (Electronics, Sports, Books, Toys, etc.), prices, margins' },
              { name: 'orders.csv', records: '30,033 rows', cols: '9 features', desc: 'Transactions across Online, Store, and Mobile channels (UPI, Cards)' },
              { name: 'order_items.csv', records: '78,610 rows', cols: '7 features', desc: 'Item-level quantities, discounts, and line totals for basket analysis' }
            ].map(table => (
              <div key={table.name} style={{ padding: '12px', background: 'var(--bg-app)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                  <strong style={{ fontSize: '13px', color: 'var(--text-main)', fontFamily: 'var(--font-mono)' }}>{table.name}</strong>
                  <span className="badge badge-primary" style={{ fontSize: '10px' }}>{table.records}</span>
                </div>
                <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>{table.desc}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Model Performance & Evaluation */}
        <div className="card" style={{ gridColumn: 'span 6', padding: '24px' }}>
          <h3 style={{ fontSize: '16px', fontWeight: '700', marginBottom: '6px' }}>Evaluation & Validation</h3>
          <p style={{ fontSize: '13px', marginBottom: '16px' }}>Temporal train/test evaluation on future orders</p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '12px', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)' }}>
              <div>
                <div style={{ fontSize: '13.5px', fontWeight: '700' }}>Mean Precision@5</div>
                <div style={{ fontSize: '11.5px', color: 'var(--text-muted)' }}>Proportion of recommendations actually purchased</div>
              </div>
              <div style={{ fontSize: '18px', fontWeight: '800', color: 'var(--primary)' }}>36.3%</div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '12px', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)' }}>
              <div>
                <div style={{ fontSize: '13.5px', fontWeight: '700' }}>Mean Recall@5</div>
                <div style={{ fontSize: '11.5px', color: 'var(--text-muted)' }}>Coverage of customer future purchases</div>
              </div>
              <div style={{ fontSize: '18px', fontWeight: '800', color: 'var(--emerald)' }}>38.7%</div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '12px', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)' }}>
              <div>
                <div style={{ fontSize: '13.5px', fontWeight: '700' }}>PCA Variance Retained</div>
                <div style={{ fontSize: '11.5px', color: 'var(--text-muted)' }}>Dimensionality reduction from 3 RFM features to 2 components</div>
              </div>
              <div style={{ fontSize: '18px', fontWeight: '800', color: 'var(--purple)' }}>96.6%</div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '12px', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)' }}>
              <div>
                <div style={{ fontSize: '13.5px', fontWeight: '700' }}>Max Discovered Rule Lift</div>
                <div style={{ fontSize: '11.5px', color: 'var(--text-muted)' }}>Highest co-purchase multiplier vs baseline chance</div>
              </div>
              <div style={{ fontSize: '18px', fontWeight: '800', color: 'var(--amber)' }}>29.99x</div>
            </div>
          </div>
        </div>

      </div>

    </div>
  );
}
