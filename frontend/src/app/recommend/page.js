'use client';

import { useState, useEffect } from 'react';
import retailData from '@/data/retailData.json';
import rulesData from '@/data/rules_database.json';
import { 
  Sparkles, 
  ShoppingBag, 
  Plus, 
  Trash2, 
  Search, 
  User, 
  CheckCircle2, 
  Zap, 
  HelpCircle, 
  TrendingUp,
  Tag,
  Star,
  RefreshCw,
  SlidersHorizontal
} from 'lucide-react';

export default function RecommendPage() {
  const { products, sample_customers, popular_products } = retailData;

  // Selected customer preset
  const [selectedCustomerId, setSelectedCustomerId] = useState(sample_customers[0].customer_id);
  // Basket items (product names)
  const [basket, setBasket] = useState(sample_customers[0].purchased_products);
  // Recommendations state
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [topN, setTopN] = useState(5);

  // Search & Filter for adding products
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');

  // Categories list
  const categories = ['All', 'Electronics', 'Sports', 'Toys', 'Books', 'Clothing', 'Accessories', 'Beauty', 'Home & Kitchen', 'Grocery'];

  // Map product catalog for quick lookup
  const productCatalogMap = new Map();
  products.forEach(p => productCatalogMap.set(p.name, p));

  // Compute recommendations whenever basket or topN changes
  const computeRecommendations = async (currentBasket, n = 5) => {
    setLoading(true);
    try {
      const res = await fetch('/api/recommend', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ purchased_products: currentBasket, top_n: n })
      });
      if (res.ok) {
        const data = await res.json();
        setRecommendations(data.recommendations || []);
      } else {
        // Fallback local computation if API fails
        fallbackLocalCompute(currentBasket, n);
      }
    } catch (e) {
      fallbackLocalCompute(currentBasket, n);
    } finally {
      setLoading(false);
    }
  };

  const fallbackLocalCompute = (currentBasket, n) => {
    const purchasedSet = new Set(currentBasket);
    const recs = new Map();

    for (const rule of rulesData.rules) {
      if (purchasedSet.has(rule.antecedent) && !purchasedSet.has(rule.consequent)) {
        if (!recs.has(rule.consequent) || rule.lift > recs.get(rule.consequent).lift) {
          const info = productCatalogMap.get(rule.consequent) || {
            name: rule.consequent,
            category: 'Retail',
            price: 1999,
            rating: 4.1
          };
          recs.set(rule.consequent, {
            product_name: rule.consequent,
            product_info: info,
            confidence: rule.confidence,
            lift: rule.lift,
            support: rule.support,
            source: 'Association Rule'
          });
        }
      }
    }

    const sorted = Array.from(recs.values()).sort((a, b) => (b.lift || 0) - (a.lift || 0));
    const results = sorted.slice(0, n);
    const resultNames = new Set(results.map(r => r.product_name));

    for (const popName of rulesData.popular) {
      if (results.length >= n) break;
      if (!purchasedSet.has(popName) && !resultNames.has(popName)) {
        const info = productCatalogMap.get(popName) || {
          name: popName,
          category: 'Bestseller',
          price: 1499,
          rating: 4.5
        };
        results.push({
          product_name: popName,
          product_info: info,
          confidence: null,
          lift: null,
          support: null,
          source: 'Popularity Fallback'
        });
        resultNames.add(popName);
      }
    }

    setRecommendations(results);
  };

  useEffect(() => {
    computeRecommendations(basket, topN);
  }, [basket, topN]);

  // Handle customer preset switch
  const handleCustomerChange = (custId) => {
    setSelectedCustomerId(custId);
    const cust = sample_customers.find(c => c.customer_id === custId);
    if (cust) {
      setBasket(cust.purchased_products);
    }
  };

  // Add product to basket
  const addToBasket = (productName) => {
    if (!basket.includes(productName)) {
      setBasket([...basket, productName]);
    }
  };

  // Remove product from basket
  const removeFromBasket = (productName) => {
    setBasket(basket.filter(item => item !== productName));
  };

  // Clear basket
  const clearBasket = () => {
    setBasket([]);
  };

  // Filter products for adding
  const filteredProducts = products.filter(p => {
    const matchCat = selectedCategory === 'All' || p.category === selectedCategory;
    const matchQuery = p.name.toLowerCase().includes(searchQuery.toLowerCase()) || 
                       p.brand.toLowerCase().includes(searchQuery.toLowerCase());
    return matchCat && matchQuery;
  }).slice(0, 15);

  const formatCurrency = (val) => '₹' + Number(val).toLocaleString('en-IN');

  return (
    <div className="container">
      {/* Header */}
      <div className="page-header">
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <span className="badge badge-emerald">Real-time Inference</span>
            <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>FP-Growth Association Mining Engine</span>
          </div>
          <h1 className="page-title">Personalized Product Recommendation Engine</h1>
          <p className="page-subtitle">
            Simulate basket intelligence, cross-sell lift, and popularity fallbacks trained on 30,000+ customer retail orders.
          </p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontSize: '12.5px', color: 'var(--text-muted)' }}>Top Recs:</span>
          {[3, 5, 8].map(n => (
            <button
              key={n}
              onClick={() => setTopN(n)}
              className={`btn btn-sm ${topN === n ? 'btn-primary' : 'btn-secondary'}`}
            >
              {n}
            </button>
          ))}
        </div>
      </div>

      {/* Profile Selector Toolbar */}
      <div className="card" style={{ padding: '16px 20px', marginBottom: '20px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '14px', background: '#FFFFFF' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '13px', fontWeight: '700', color: 'var(--text-main)' }}>
            <User size={16} style={{ color: 'var(--primary)' }} />
            <span>Load Customer Profile:</span>
          </div>
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
            {sample_customers.map(c => {
              const isSelected = selectedCustomerId === c.customer_id;
              return (
                <button
                  key={c.customer_id}
                  onClick={() => handleCustomerChange(c.customer_id)}
                  style={{
                    padding: '6px 12px',
                    borderRadius: 'var(--radius-full)',
                    fontSize: '12px',
                    fontWeight: '600',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px',
                    border: isSelected ? '1px solid var(--primary)' : '1px solid var(--border-subtle)',
                    background: isSelected ? 'var(--primary-light)' : '#FFFFFF',
                    color: isSelected ? 'var(--primary)' : 'var(--text-muted)',
                    transition: 'all 0.15s ease'
                  }}
                >
                  <span>{c.name}</span>
                  <span className={`badge ${c.loyalty_tier === 'Platinum' ? 'badge-purple' : (c.loyalty_tier === 'Gold' ? 'badge-amber' : 'badge-primary')}`} style={{ padding: '1px 5px', fontSize: '9px' }}>
                    {c.loyalty_tier}
                  </span>
                </button>
              );
            })}
          </div>
        </div>

        <button 
          onClick={clearBasket} 
          className="btn btn-secondary btn-sm"
          style={{ color: 'var(--rose)', borderColor: 'var(--rose-border)' }}
        >
          <Trash2 size={13} />
          <span>Clear Basket</span>
        </button>
      </div>

      {/* Main Grid: Basket & Recommendations */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(12, 1fr)', gap: '24px', marginBottom: '28px' }}>
        
        {/* Left Side: Current Basket & Add Products */}
        <div style={{ gridColumn: 'span 5', display: 'flex', flexDirection: 'column', gap: '20px' }}>
          
          {/* Current Active Basket Card */}
          <div className="card" style={{ padding: '20px' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <ShoppingBag size={18} style={{ color: 'var(--primary)' }} />
                <h3 style={{ fontSize: '15px', fontWeight: '700' }}>Current Customer Basket</h3>
              </div>
              <span className="badge badge-primary">{basket.length} items</span>
            </div>

            {basket.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '24px 12px', border: '1px dashed var(--border-subtle)', borderRadius: 'var(--radius-md)' }}>
                <ShoppingBag size={28} style={{ color: 'var(--text-subtle)', margin: '0 auto 8px' }} />
                <p style={{ fontSize: '13px', color: 'var(--text-muted)' }}>Your basket is currently empty.</p>
                <p style={{ fontSize: '11.5px', color: 'var(--text-subtle)' }}>Select products below to see real-time AI suggestions!</p>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', maxHeight: '280px', overflowY: 'auto', paddingRight: '4px' }}>
                {basket.map((item, idx) => {
                  const productInfo = productCatalogMap.get(item);
                  return (
                    <div 
                      key={idx} 
                      style={{ 
                        display: 'flex', 
                        alignItems: 'center', 
                        justifyContent: 'space-between', 
                        padding: '9px 12px', 
                        background: 'var(--bg-app)', 
                        border: '1px solid var(--border-subtle)', 
                        borderRadius: 'var(--radius-md)' 
                      }}
                    >
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '2px', maxWidth: '80%' }}>
                        <span style={{ fontSize: '12.5px', fontWeight: '600', color: 'var(--text-main)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                          {item}
                        </span>
                        <div style={{ display: 'flex', gap: '6px', fontSize: '11px', color: 'var(--text-muted)' }}>
                          <span>{productInfo?.category || 'Retail'}</span>
                          {productInfo && <span>• {formatCurrency(productInfo.price)}</span>}
                        </div>
                      </div>
                      <button 
                        onClick={() => removeFromBasket(item)}
                        style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-subtle)', padding: '4px' }}
                        title="Remove from basket"
                      >
                        <Trash2 size={14} onMouseEnter={(e) => e.currentTarget.style.color = 'var(--rose)'} onMouseLeave={(e) => e.currentTarget.style.color = 'var(--text-subtle)'} />
                      </button>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* Product Catalog Picker */}
          <div className="card" style={{ padding: '20px' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
              <h3 style={{ fontSize: '15px', fontWeight: '700' }}>Add Products from Catalog</h3>
              <span style={{ fontSize: '11px', color: 'var(--text-subtle)' }}>208 products available</span>
            </div>

            {/* Search Box */}
            <div style={{ position: 'relative', marginBottom: '12px' }}>
              <Search size={15} style={{ position: 'absolute', left: '12px', top: '10px', color: 'var(--text-subtle)' }} />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search products by title or brand..."
                style={{
                  width: '100%',
                  padding: '8px 12px 8px 36px',
                  borderRadius: 'var(--radius-md)',
                  border: '1px solid var(--border-card)',
                  fontSize: '13px',
                  outline: 'none',
                  background: 'var(--bg-app)',
                  fontFamily: 'inherit'
                }}
              />
            </div>

            {/* Category Filter Pills */}
            <div style={{ display: 'flex', gap: '6px', overflowX: 'auto', paddingBottom: '8px', marginBottom: '12px' }}>
              {categories.map(cat => (
                <button
                  key={cat}
                  onClick={() => setSelectedCategory(cat)}
                  style={{
                    padding: '4px 10px',
                    borderRadius: 'var(--radius-full)',
                    fontSize: '11.5px',
                    fontWeight: '600',
                    cursor: 'pointer',
                    whiteSpace: 'nowrap',
                    border: selectedCategory === cat ? '1px solid var(--primary)' : '1px solid var(--border-subtle)',
                    background: selectedCategory === cat ? 'var(--primary)' : '#FFFFFF',
                    color: selectedCategory === cat ? '#FFFFFF' : 'var(--text-muted)'
                  }}
                >
                  {cat}
                </button>
              ))}
            </div>

            {/* Product List */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', maxHeight: '300px', overflowY: 'auto' }}>
              {filteredProducts.map(p => {
                const inBasket = basket.includes(p.name);
                return (
                  <div
                    key={p.id}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      padding: '8px 12px',
                      border: '1px solid var(--border-subtle)',
                      borderRadius: 'var(--radius-sm)',
                      background: inBasket ? 'var(--emerald-light)' : '#FFFFFF',
                      transition: 'all 0.15s ease'
                    }}
                  >
                    <div style={{ maxWidth: '75%' }}>
                      <div style={{ fontSize: '12.5px', fontWeight: '600', color: 'var(--text-main)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                        {p.name}
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '11px', color: 'var(--text-muted)' }}>
                        <span>{p.brand}</span>
                        <span>•</span>
                        <strong style={{ color: 'var(--text-main)' }}>{formatCurrency(p.price)}</strong>
                      </div>
                    </div>

                    <button
                      onClick={() => inBasket ? removeFromBasket(p.name) : addToBasket(p.name)}
                      className={`btn btn-sm ${inBasket ? 'btn-secondary' : 'btn-primary'}`}
                      style={{ padding: '4px 8px', fontSize: '11px' }}
                    >
                      {inBasket ? (
                        <>
                          <CheckCircle2 size={12} style={{ color: 'var(--emerald)' }} />
                          <span>Added</span>
                        </>
                      ) : (
                        <>
                          <Plus size={12} />
                          <span>Add</span>
                        </>
                      )}
                    </button>
                  </div>
                );
              })}
            </div>

          </div>

        </div>

        {/* Right Side: AI Generated Recommendations */}
        <div style={{ gridColumn: 'span 7' }}>
          <div className="card" style={{ padding: '24px', height: '100%', display: 'flex', flexDirection: 'column' }}>
            
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '18px', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '14px' }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Sparkles size={18} style={{ color: 'var(--primary)' }} />
                  <h3 style={{ fontSize: '16px', fontWeight: '700' }}>Live Recommended Products</h3>
                </div>
                <p style={{ fontSize: '12.5px' }}>
                  Calculated based on antecedent co-purchase probability and lift factor
                </p>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                {loading && <RefreshCw size={14} className="spin" style={{ color: 'var(--primary)' }} />}
                <span className="badge badge-primary">{recommendations.length} Suggestions</span>
              </div>
            </div>

            {recommendations.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '60px 20px', margin: 'auto 0' }}>
                <Sparkles size={36} style={{ color: 'var(--text-subtle)', margin: '0 auto 12px' }} />
                <h4 style={{ fontSize: '15px', fontWeight: '600', marginBottom: '6px' }}>No recommendations yet</h4>
                <p style={{ fontSize: '13px', color: 'var(--text-muted)', maxWidth: '400px', margin: '0 auto' }}>
                  Add products to the basket on the left or select a sample customer to generate machine learning suggestions.
                </p>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
                {recommendations.map((rec, idx) => {
                  const info = rec.product_info || {};
                  const isRule = rec.source === 'Association Rule';

                  return (
                    <div
                      key={idx}
                      style={{
                        padding: '16px',
                        border: '1px solid var(--border-card)',
                        borderRadius: 'var(--radius-md)',
                        background: isRule ? 'linear-gradient(135deg, #FFFFFF 0%, #FAFAFF 100%)' : '#FFFFFF',
                        boxShadow: 'var(--shadow-xs)',
                        display: 'flex',
                        flexDirection: 'column',
                        gap: '12px',
                        transition: 'transform 0.15s ease, box-shadow 0.15s ease'
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.transform = 'translateY(-2px)';
                        e.currentTarget.style.boxShadow = 'var(--shadow-md)';
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.transform = 'translateY(0)';
                        e.currentTarget.style.boxShadow = 'var(--shadow-xs)';
                      }}
                    >
                      {/* Top Row: Rank, Title, Badges */}
                      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '12px' }}>
                        <div style={{ display: 'flex', alignItems: 'flex-start', gap: '10px' }}>
                          <div style={{ width: '28px', height: '28px', borderRadius: '6px', background: isRule ? 'var(--primary-light)' : 'var(--amber-light)', color: isRule ? 'var(--primary)' : 'var(--amber)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '13px', fontWeight: '700' }}>
                            {idx + 1}
                          </div>
                          <div>
                            <div style={{ fontSize: '14.5px', fontWeight: '700', color: 'var(--text-main)', marginBottom: '3px' }}>
                              {rec.product_name}
                            </div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px', color: 'var(--text-muted)' }}>
                              <span>{info.category || 'Retail'}</span>
                              <span>•</span>
                              <span>{info.brand || 'Premium Brand'}</span>
                              <span>•</span>
                              <div style={{ display: 'flex', alignItems: 'center', gap: '2px', color: '#D97706' }}>
                                <Star size={12} fill="#D97706" />
                                <span>{info.rating || 4.2}</span>
                              </div>
                            </div>
                          </div>
                        </div>

                        <div style={{ textAlign: 'right' }}>
                          <div style={{ fontSize: '16px', fontWeight: '800', color: 'var(--text-main)' }}>
                            {formatCurrency(info.price || 1999)}
                          </div>
                          {info.discount > 0 && (
                            <span style={{ fontSize: '11px', color: 'var(--emerald)', fontWeight: '600' }}>
                              {info.discount}% off
                            </span>
                          )}
                        </div>
                      </div>

                      {/* Middle: Algorithmic Explanations */}
                      <div style={{ display: 'flex', alignItems: 'center', gap: '16px', flexWrap: 'wrap', padding: '10px 14px', background: 'var(--bg-app)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)', fontSize: '12px' }}>
                        <div>
                          <span style={{ color: 'var(--text-muted)' }}>Engine Source: </span>
                          <span className={`badge ${isRule ? 'badge-emerald' : 'badge-amber'}`} style={{ padding: '2px 7px', fontSize: '10px' }}>
                            {rec.source}
                          </span>
                        </div>

                        {rec.lift && (
                          <div>
                            <span style={{ color: 'var(--text-muted)' }}>Lift Multiplier: </span>
                            <strong style={{ color: 'var(--primary)' }}>{rec.lift.toFixed(2)}x</strong>
                            <span style={{ fontSize: '10px', color: 'var(--text-subtle)', marginLeft: '3px' }}>(High Affinity)</span>
                          </div>
                        )}

                        {rec.confidence && (
                          <div>
                            <span style={{ color: 'var(--text-muted)' }}>Confidence: </span>
                            <strong style={{ color: 'var(--text-main)' }}>{(rec.confidence * 100).toFixed(1)}%</strong>
                          </div>
                        )}

                        {rec.support && (
                          <div>
                            <span style={{ color: 'var(--text-muted)' }}>Support: </span>
                            <strong style={{ color: 'var(--text-main)' }}>{(rec.support * 100).toFixed(2)}%</strong>
                          </div>
                        )}
                      </div>

                      {/* Bottom Action: Accept / Add to basket to chain */}
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', paddingTop: '4px' }}>
                        <span style={{ fontSize: '11.5px', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '4px' }}>
                          <Zap size={13} style={{ color: 'var(--primary)' }} />
                          <span>Frequently purchased together with items currently in your basket</span>
                        </span>

                        <button
                          onClick={() => addToBasket(rec.product_name)}
                          className="btn btn-secondary btn-sm"
                          style={{ borderColor: 'var(--primary-border)', color: 'var(--primary)' }}
                        >
                          <Plus size={13} />
                          <span>Add & Chain Next Recs</span>
                        </button>
                      </div>

                    </div>
                  );
                })}
              </div>
            )}

            {/* Explanation footer card */}
            <div style={{ marginTop: 'auto', paddingTop: '20px', borderTop: '1px solid var(--border-subtle)', display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px', fontSize: '11.5px' }}>
              <div style={{ padding: '8px', background: 'var(--bg-app)', borderRadius: '6px' }}>
                <strong style={{ color: 'var(--text-main)', display: 'block', marginBottom: '2px' }}>Confidence Score</strong>
                <p style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Probability that customer buys Item Y given they bought Item X.</p>
              </div>
              <div style={{ padding: '8px', background: 'var(--bg-app)', borderRadius: '6px' }}>
                <strong style={{ color: 'var(--primary)', display: 'block', marginBottom: '2px' }}>Lift Metric (&gt;1.0)</strong>
                <p style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Strength of the association compared to buying Item Y at random.</p>
              </div>
              <div style={{ padding: '8px', background: 'var(--bg-app)', borderRadius: '6px' }}>
                <strong style={{ color: 'var(--amber)', display: 'block', marginBottom: '2px' }}>Popularity Fallback</strong>
                <p style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Guarantees zero cold-start when no co-purchase rule is triggered.</p>
              </div>
            </div>

          </div>
        </div>

      </div>

    </div>
  );
}
