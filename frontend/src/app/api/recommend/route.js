import { NextResponse } from 'next/server';
import rulesData from '@/data/rules_database.json';
import retailData from '@/data/retailData.json';

export async function POST(request) {
  try {
    const body = await request.json();
    const { purchased_products = [], top_n = 5 } = body;

    const purchasedSet = new Set(purchased_products);
    const productCatalogMap = new Map();
    retailData.products.forEach(p => productCatalogMap.set(p.name, p));

    const recommendations = new Map();

    // 1. Check association rules
    for (const rule of rulesData.rules) {
      if (purchasedSet.has(rule.antecedent)) {
        const item = rule.consequent;
        if (!purchasedSet.has(item)) {
          if (!recommendations.has(item) || rule.lift > recommendations.get(item).lift) {
            const productInfo = productCatalogMap.get(item) || {
              name: item,
              category: 'General',
              price: 1499,
              rating: 4.2,
              discount: 5
            };
            recommendations.set(item, {
              product_name: item,
              product_info: productInfo,
              confidence: rule.confidence,
              lift: rule.lift,
              support: rule.support,
              source: 'Association Rule'
            });
          }
        }
      }
    }

    // Sort by lift desc, then confidence desc
    const ranked = Array.from(recommendations.values()).sort((a, b) => {
      if (b.lift !== a.lift) return b.lift - a.lift;
      return b.confidence - a.confidence;
    });

    const results = ranked.slice(0, top_n);
    const recommendedNames = new Set(results.map(r => r.product_name));

    // 2. Fallback to Popularity
    for (const popularName of rulesData.popular) {
      if (results.length >= top_n) break;
      if (!purchasedSet.has(popularName) && !recommendedNames.has(popularName)) {
        const productInfo = productCatalogMap.get(popularName) || {
          name: popularName,
          category: 'Bestseller',
          price: 1999,
          rating: 4.4,
          discount: 10
        };
        results.push({
          product_name: popularName,
          product_info: productInfo,
          confidence: null,
          lift: null,
          support: null,
          source: 'Popularity Fallback'
        });
        recommendedNames.add(popularName);
      }
    }

    return NextResponse.json({
      status: 'success',
      query: {
        purchased_products,
        count_purchased: purchased_products.length,
        top_n
      },
      recommendations: results
    });
  } catch (error) {
    console.error('Recommendation API error:', error);
    return NextResponse.json(
      { status: 'error', message: 'Failed to generate recommendations' },
      { status: 500 }
    );
  }
}
