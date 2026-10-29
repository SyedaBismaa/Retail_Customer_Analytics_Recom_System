"""
Phase 3 Verification Script
Tests all Dashboard, Customer, Segmentation, and Recommendation endpoints.
"""

from fastapi.testclient import TestClient
from backend.main import app

def run_tests():
    with TestClient(app) as client:
        print("=== 1. Testing Dashboard Endpoints ===")
        r_sum = client.get("/api/dashboard/summary")
        print("Summary Status:", r_sum.status_code, r_sum.json())
        assert r_sum.status_code == 200
        data = r_sum.json()
        assert data["total_customers"] == 5000
        assert data["total_orders"] == 30033
        assert data["total_delivered_orders"] == 23629
        assert data["total_revenue"] > 0
        assert data["avg_order_value"] > 0

        r_trend = client.get("/api/dashboard/sales-trend")
        print("Sales Trend:", r_trend.status_code, len(r_trend.json()["trends"]), "monthly periods")
        assert r_trend.status_code == 200 and len(r_trend.json()["trends"]) > 0

        r_cat = client.get("/api/dashboard/category-performance")
        print("Category Performance:", r_cat.status_code, len(r_cat.json()["categories"]), "categories")
        assert r_cat.status_code == 200 and len(r_cat.json()["categories"]) == 9

        print("\n=== 2. Testing Customer Endpoints ===")
        r_custs = client.get("/api/customers?page=1&page_size=5")
        print("Customers List:", r_custs.status_code, "Total:", r_custs.json()["total"])
        assert r_custs.status_code == 200 and len(r_custs.json()["customers"]) == 5

        r_c1 = client.get("/api/customers/CUST001444")
        print("Single Customer:", r_c1.status_code, r_c1.json()["customer_id"], r_c1.json()["first_name"], r_c1.json()["segment"])
        assert r_c1.status_code == 200
        assert r_c1.json()["customer_id"] == "CUST001444"

        r_orders = client.get("/api/customers/CUST001444/orders")
        print("Customer Orders:", r_orders.status_code, "Order Count:", r_orders.json()["order_count"])
        assert r_orders.status_code == 200

        r_c_err = client.get("/api/customers/NON_EXISTENT_ID")
        print("Customer 404 Verification:", r_c_err.status_code)
        assert r_c_err.status_code == 404

        print("\n=== 3. Testing Segmentation Endpoints ===")
        r_seg = client.get("/api/segments/summary")
        print("Segments Summary:", r_seg.status_code, len(r_seg.json()["segments"]), "segments")
        assert r_seg.status_code == 200 and len(r_seg.json()["segments"]) == 5
        for s in r_seg.json()["segments"]:
            print(f"  * {s['segment_name']}: {s['count']} ({s['percentage']}%) | Recency: {s['avg_recency_days']}d | Spend: ₹{s['avg_monetary_spend']}")

        r_single_seg = client.get("/api/segments/High-Value%20Loyal")
        print("Single Segment:", r_single_seg.status_code, r_single_seg.json()["segment"]["segment_name"])
        assert r_single_seg.status_code == 200

        print("\n=== 4. Testing Recommendation Endpoints ===")
        r_rec = client.get("/api/recommendations/CUST001444?top_n=5")
        print("Recommendations:", r_rec.status_code, len(r_rec.json()["recommendations"]), "items recommended")
        assert r_rec.status_code == 200 and len(r_rec.json()["recommendations"]) == 5
        for i, item in enumerate(r_rec.json()["recommendations"], 1):
            print(f"  {i}. {item['product_name']} | Source: {item['source']} | Lift: {item['lift']} | Price: ₹{item['product_info']['price']}")

        # Verify previously purchased products are excluded
        rec_names = {item["product_name"] for item in r_rec.json()["recommendations"]}
        past_names = set(r_rec.json()["previously_purchased_products"])
        overlap = rec_names & past_names
        print(f"Overlap between recommended and past purchases: {len(overlap)} (Expected: 0)")
        assert len(overlap) == 0

        r_rec_err = client.get("/api/recommendations/FAKE_CUSTOMER")
        print("Recommendations 404 Verification:", r_rec_err.status_code)
        assert r_rec_err.status_code == 404

        r_custom = client.post("/api/recommendations/custom", json={"purchased_products": ["LEGO Superhero Toy 400"], "top_n": 3})
        print("Custom Basket Recs:", r_custom.status_code, len(r_custom.json()["recommendations"]), "items")
        assert r_custom.status_code == 200

        print("\nALL PHASE 3 API ENDPOINTS PASSED VERIFICATION PERFECTLY!")

if __name__ == "__main__":
    run_tests()
