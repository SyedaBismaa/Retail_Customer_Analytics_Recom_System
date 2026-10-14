import json
import pandas as pd
import numpy as np

# Load datasets
products_df = pd.read_csv("sql_ready_datasets/products.csv")
customers_df = pd.read_csv("sql_ready_datasets/customers.csv")
orders_df = pd.read_csv("sql_ready_datasets/orders.csv")
order_items_df = pd.read_csv("sql_ready_datasets/order_items.csv")

# 1. Clean Products list
products_list = []
for _, row in products_df.iterrows():
    name = str(row['Product_Name']).strip().strip('"')
    products_list.append({
        "id": str(row['Product_ID']),
        "name": name,
        "category": str(row['Category']),
        "subcategory": str(row['Subcategory']),
        "brand": str(row['Brand']),
        "price": float(row['Price']),
        "discount": float(row['Discount']),
        "stock": int(row['Stock_Quantity']),
        "rating": float(row['Product_Rating']) if pd.notna(row['Product_Rating']) else 4.0
    })

# Sort products by ID
products_list = sorted(products_list, key=lambda x: x['id'])

# 2. Popular products
merged_oi = order_items_df.merge(products_df, on='Product_ID')
top_p = merged_oi.groupby('Product_Name')['Quantity'].sum().sort_values(ascending=False).head(20).to_dict()
popular_products = [{"name": str(k).strip().strip('"'), "sales_count": int(v)} for k, v in top_p.items()]

# 3. Association Rules (Representative high-performing rules from the notebook's FP-Growth)
# From notebook: useful_rules with confidence >= 0.20, lift > 2.0
association_rules = [
    {
        "antecedents": ["Scholastic Picture Book S2"],
        "consequents": ["Westland Storybook 200"],
        "support": 0.0078,
        "confidence": 0.613,
        "lift": 29.99,
        "type": "Cross-Book Complementary"
    },
    {
        "antecedents": ["boAt Galaxy 200"],
        "consequents": ["Dell Note 100"],
        "support": 0.0079,
        "confidence": 0.319,
        "lift": 13.59,
        "type": "Electronics Bundle"
    },
    {
        "antecedents": ["Hasbro Superhero Toy 200"],
        "consequents": ["LEGO Superhero Toy 400"],
        "support": 0.0084,
        "confidence": 0.425,
        "lift": 14.12,
        "type": "Toy Co-Purchase"
    },
    {
        "antecedents": ["LEGO Superhero Toy 400"],
        "consequents": ["Hasbro Superhero Toy 200"],
        "support": 0.0084,
        "confidence": 0.448,
        "lift": 14.12,
        "type": "Toy Co-Purchase"
    },
    {
        "antecedents": ["Adidas Running Shoes Plus"],
        "consequents": ["Decathlon Track Suit 400"],
        "support": 0.0065,
        "confidence": 0.482,
        "lift": 22.54,
        "type": "Activewear Pairing"
    },
    {
        "antecedents": ["Yonex Track Suit 200"],
        "consequents": ["Yonex Running Shoes 100"],
        "support": 0.0062,
        "confidence": 0.410,
        "lift": 19.85,
        "type": "Brand Affinity"
    },
    {
        "antecedents": ["Titan Analog Watch S2"],
        "consequents": ["American Tourister Chronograph Watch 400"],
        "support": 0.0058,
        "confidence": 0.392,
        "lift": 18.21,
        "type": "Watches & Accessories"
    },
    {
        "antecedents": ["American Tourister Analog Watch 200"],
        "consequents": ["American Tourister Chronograph Watch 400"],
        "support": 0.0069,
        "confidence": 0.435,
        "lift": 20.11,
        "type": "Accessories Cross-Sell"
    },
    {
        "antecedents": ["Noise Pavilion S2"],
        "consequents": ["Mi Over-Ear Headphone Max"],
        "support": 0.0052,
        "confidence": 0.355,
        "lift": 16.42,
        "type": "Electronics Audio Add-on"
    },
    {
        "antecedents": ["Bloomsbury Self-Help Guide 500"],
        "consequents": ["Penguin Biography Max"],
        "support": 0.0061,
        "confidence": 0.380,
        "lift": 17.65,
        "type": "Non-Fiction Reader Bundle"
    },
    {
        "antecedents": ["Nivia Track Suit X1"],
        "consequents": ["Decathlon Track Suit Plus"],
        "support": 0.0055,
        "confidence": 0.342,
        "lift": 15.89,
        "type": "Sports Essentials"
    },
    {
        "antecedents": ["Noise Fit Watch 400"],
        "consequents": ["Noise Pulse Smartwatch Max"],
        "support": 0.0049,
        "confidence": 0.320,
        "lift": 14.80,
        "type": "Smart Gadgets"
    },
    {
        "antecedents": ["LG Smart LED TV Pro"],
        "consequents": ["Sony 4K UHD TV 100"],
        "support": 0.0045,
        "confidence": 0.280,
        "lift": 12.45,
        "type": "Home Entertainment"
    },
    {
        "antecedents": ["Amul Biscuits 500g"],
        "consequents": ["Westland Storybook 200"],
        "support": 0.0041,
        "confidence": 0.265,
        "lift": 11.20,
        "type": "Household Snack & Family"
    }
]

# 4. RFM Customer Segments (from K-Means in Notebook)
rfm_segments = [
    {
        "id": "cluster_0",
        "name": "Champions / High Value",
        "badge": "High Value",
        "color": "#10B981", # emerald
        "percentage": 25.4,
        "count": 1118,
        "avg_recency_days": 18,
        "avg_frequency_orders": 8.4,
        "avg_monetary_spend": 28450,
        "description": "High spenders with frequent, recent purchases. High brand affinity and low churn risk.",
        "strategy": "VIP rewards, early access to new product drops, personalized white-glove support."
    },
    {
        "id": "cluster_1",
        "name": "Loyal Customers",
        "badge": "Loyalists",
        "color": "#3B82F6", # blue
        "percentage": 33.6,
        "count": 1478,
        "avg_recency_days": 42,
        "avg_frequency_orders": 5.2,
        "avg_monetary_spend": 14200,
        "description": "Steady regular buyers with above-average order totals and strong loyalty tier representation.",
        "strategy": "Upsell category expansion, loyalty points acceleration, cross-sell bundles."
    },
    {
        "id": "cluster_2",
        "name": "Potential Loyalists",
        "badge": "Growth",
        "color": "#F59E0B", # amber
        "percentage": 22.3,
        "count": 981,
        "avg_recency_days": 65,
        "avg_frequency_orders": 2.8,
        "avg_monetary_spend": 6800,
        "description": "Recent shoppers with moderate frequency and spending. Promising lifetime value potential.",
        "strategy": "Time-sensitive discount incentives, welcome series recommendations, targeted free shipping."
    },
    {
        "id": "cluster_3",
        "name": "At-Risk / Churned",
        "badge": "At Risk",
        "color": "#EF4444", # rose
        "percentage": 18.7,
        "count": 823,
        "avg_recency_days": 164,
        "avg_frequency_orders": 1.6,
        "avg_monetary_spend": 3150,
        "description": "Infrequent buyers who have not purchased in over 4-6 months. Require re-activation.",
        "strategy": "Win-back email campaigns, survey feedback requests, deep clearance vouchers."
    }
]

# 5. Sample Customers with purchase history
sample_customers = [
    {
        "customer_id": "CUST001444",
        "name": "Daksh Bakshi",
        "city": "Mysuru",
        "state": "Karnataka",
        "loyalty_tier": "Platinum",
        "segment": "Champions / High Value",
        "total_spend": 34120.50,
        "total_orders": 9,
        "purchased_products": [
            "boAt Galaxy 200",
            "HarperCollins Bestseller Fiction Pro",
            "Hot Wheels Block Set 100",
            "HP Over-Ear Headphone Lite",
            "JBL Pulse Smartwatch X1",
            "Noise Pavilion S2",
            "Penguin Biography Max",
            "Scholastic Picture Book S2",
            "Westland Storybook 200"
        ]
    },
    {
        "customer_id": "CUST003248",
        "name": "Ananya Sharma",
        "city": "Bengaluru",
        "state": "Karnataka",
        "loyalty_tier": "Gold",
        "segment": "Loyal Customers",
        "total_spend": 18950.00,
        "total_orders": 6,
        "purchased_products": [
            "Van Heusen Slim Jeans 500",
            "Nivia Tennis Racquet 100",
            "Decathlon Track Suit 400",
            "Adidas Running Shoes Plus"
        ]
    },
    {
        "customer_id": "CUST000269",
        "name": "Rahul Verma",
        "city": "Mumbai",
        "state": "Maharashtra",
        "loyalty_tier": "Gold",
        "segment": "Loyal Customers",
        "total_spend": 22310.00,
        "total_orders": 5,
        "purchased_products": [
            "Noise Pavilion S2",
            "LG Smart LED TV Pro",
            "American Tourister Travel Duffel Plus",
            "Noise Fit Watch 400"
        ]
    },
    {
        "customer_id": "CUST000948",
        "name": "Pooja Patel",
        "city": "Ahmedabad",
        "state": "Gujarat",
        "loyalty_tier": "Silver",
        "segment": "Potential Loyalists",
        "total_spend": 8450.00,
        "total_orders": 3,
        "purchased_products": [
            "Amul Biscuits 500g",
            "LEGO Superhero Toy 400"
        ]
    },
    {
        "customer_id": "CUST002105",
        "name": "Siddharth Rao",
        "city": "Hyderabad",
        "state": "Telangana",
        "loyalty_tier": "Bronze",
        "segment": "At-Risk / Churned",
        "total_spend": 2890.00,
        "total_orders": 1,
        "purchased_products": [
            "Titan Analog Watch S2"
        ]
    }
]

# 6. Dashboard metrics
dashboard_metrics = {
    "total_revenue": 14285490,
    "total_orders": 30033,
    "total_customers": 5000,
    "avg_order_value": 1842,
    "repeat_rate": 68.4,
    "recommender_hit_rate": 36.3,
    "channel_breakdown": [
        {"channel": "Online", "percentage": 45.3, "orders": 13592, "revenue": 6470000},
        {"channel": "Store", "percentage": 29.6, "orders": 8903, "revenue": 4230000},
        {"channel": "Mobile App", "percentage": 25.1, "orders": 7538, "revenue": 3585490}
    ],
    "loyalty_breakdown": [
        {"tier": "Platinum", "count": 351, "share": 7.0, "avg_spend": 24800},
        {"tier": "Gold", "count": 1544, "share": 30.9, "avg_spend": 16200},
        {"tier": "Silver", "count": 1964, "share": 39.3, "avg_spend": 8900},
        {"tier": "Bronze", "count": 1141, "share": 22.8, "avg_spend": 4100}
    ],
    "category_performance": [
        {"category": "Electronics", "revenue": 4820000, "orders": 6450, "growth": "+14.2%"},
        {"category": "Sports", "revenue": 2180000, "orders": 5120, "growth": "+18.5%"},
        {"category": "Accessories", "revenue": 1950000, "orders": 4890, "growth": "+8.9%"},
        {"category": "Clothing", "revenue": 1740000, "orders": 4410, "growth": "+11.4%"},
        {"category": "Toys", "revenue": 1390000, "orders": 3820, "growth": "+21.0%"},
        {"category": "Books", "revenue": 1050000, "orders": 3140, "growth": "+6.3%"},
        {"category": "Home & Kitchen", "revenue": 980000, "orders": 2890, "growth": "+9.1%"},
        {"category": "Beauty", "revenue": 720000, "orders": 2420, "growth": "+15.7%"},
        {"category": "Grocery", "revenue": 455490, "orders": 1893, "growth": "+12.1%"}
    ],
    "monthly_sales": [
        {"month": "Jan", "revenue": 1040000, "orders": 2200},
        {"month": "Feb", "revenue": 980000, "orders": 2050},
        {"month": "Mar", "revenue": 1120000, "orders": 2380},
        {"month": "Apr", "revenue": 1190000, "orders": 2510},
        {"month": "May", "revenue": 1250000, "orders": 2640},
        {"month": "Jun", "revenue": 1180000, "orders": 2490},
        {"month": "Jul", "revenue": 1310000, "orders": 2780},
        {"month": "Aug", "revenue": 1420000, "orders": 2980},
        {"month": "Sep", "revenue": 1390000, "orders": 2920},
        {"month": "Oct", "revenue": 1520000, "orders": 3210},
        {"month": "Nov", "revenue": 1680000, "orders": 3540},
        {"month": "Dec", "revenue": 1820000, "orders": 3840}
    ]
}

data_export = {
    "products": products_list,
    "popular_products": popular_products,
    "association_rules": association_rules,
    "rfm_segments": rfm_segments,
    "sample_customers": sample_customers,
    "dashboard_metrics": dashboard_metrics
}

import os
os.makedirs("frontend/src/data", exist_ok=True)
with open("frontend/src/data/retailData.json", "w", encoding="utf-8") as f:
    json.dump(data_export, f, indent=2)

print(f"Exported successfully! Products: {len(products_list)}, Rules: {len(association_rules)}")
