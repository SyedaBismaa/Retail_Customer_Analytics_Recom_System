**Retail Customer Analytics & Recommendation System
An end-to-end retail analytics and recommendation system built using Python, PostgreSQL, SQL, and Machine Learning.
The project focuses on understanding customer purchasing behavior, segmenting customers based on their behavior, and eventually generating product recommendations using purchase patterns.
*Project Objective
The project aims to build a complete retail analytics pipeline:
Raw Retail Data
      ↓
Data Cleaning
      ↓
PostgreSQL + SQL
      ↓
Customer Analytics
      ↓
EDA + Feature Engineering
      ↓
RFM Analysis
      ↓
Customer Segmentation
      ↓
Product Association Rules
      ↓
Recommendation System
      ↓
Streamlit Dashboard

**Dataset
The project uses four relational datasets:
- Customers — customer demographics and loyalty information
- Products — product, category, brand, price and inventory information
- Orders — customer orders and transaction details
- Order Items — products purchased within each order
The datasets are stored in PostgreSQL and connected using:
Customer_ID
Order_ID
Product_ID

** SQL & PostgreSQL
The raw datasets were cleaned and prepared as SQL-ready datasets before loading them into PostgreSQL.
Main SQL work included:
- Joining customer, order, order-item and product tables
- Customer-level aggregations
- Revenue and spending analysis
- Customer order frequency
- Product/category analysis
- CASE WHEN for business segmentation
- CTEs for multi-step analysis
- Window functions such as ROW_NUMBER(), RANK() and LAG()
The main output of the SQL stage is:
customer_analytics
A single customer-level dataset containing metrics such as:
- Customer information
- Total orders
- Total spending
- Average order value
- First/last order dates
- Unique products purchased
- Total items purchased
- Favorite category
- Customer value segment
This table is then loaded directly from PostgreSQL into Python using SQLAlchemy + Pandas.
**Exploratory Data Analysis
EDA was performed on the customer-level dataset to understand:
- Distributions
- Missing values
- Numerical variables
- Categorical variables
- Spending and purchasing behavior
- Feature cardinality
- Potential skewness and outliers
Some missing dates were found for customers with zero orders and zero spending.
These were treated as meaningful missing values rather than randomly filling them.
A has_purchase feature was created:
1 → customer has purchased
0 → customer has never purchased

⚙️ Feature Engineering
Different encoding strategies were used depending on the feature.
One-Hot Encoding
Used for low/moderate-cardinality categorical features such as:
- Gender
- State
- Occupation
- Marital Status
- Preferred Channel
- Favorite Category
Frequency Encoding
City contained 33 categories, so instead of creating 33 dummy variables, frequency encoding was used.
city_frequency = df["city"].value_counts(normalize=True)df["city_frequency"] = df["city"].map(city_frequency)


Ordinal Encoding
Loyalty tiers have a natural order:
Bronze → Silver → Gold → Platinum

So they were mapped to:
1 → Bronze
2 → Silver
3 → Gold
4 → Platinum

Age was kept as a numerical feature rather than creating age groups.
💰 RFM Analysis
RFM was used to capture customer purchasing behavior.
R — Recency
How recently a customer purchased.
recency = reference_date - last_order_date


The reference date was the latest order date in the dataset.
Lower Recency = more recently active customer.
F — Frequency
How frequently the customer purchased.
Frequency = Total Orders

M — Monetary
How much the customer spent.
Monetary = Total Spending

Only customers with purchase history were used for RFM clustering.
5,000 total customers
        ↓
4,400 purchasing customers
        ↓
RFM segmentation

The ~600 customers with no purchases were kept separately because they don't have a meaningful Recency value.
📈 RFM Skewness
Initial skewness:
Recency      1.33
Frequency    2.12
Monetary     3.96

Monetary was particularly highly skewed because a small number of customers had very high spending.
Since K-Means is distance-based, extreme values can have a strong influence on clustering.

***Yeo-Johnson Transformation
log1p() was initially tested, but it over-corrected the distributions, especially Monetary.
Therefore, Yeo-Johnson transformation was used.
What is Yeo-Johnson?
Yeo-Johnson is a power transformation technique used to make highly skewed data more symmetric and suitable for statistical/ML models.
One advantage is that it can handle zero values, which makes it convenient for features such as Frequency and Monetary.
from sklearn.preprocessing import PowerTransformerpt = PowerTransformer(method="yeo-johnson")rfm_transformed = pt.fit_transform(    rfm[["recency", "frequency", "monetary"]])


After transformation:
Recency      -0.094
Frequency    -0.010
Monetary     -0.171

These values are close to zero, indicating that the extreme skewness was substantially reduced.
📏 Feature Scaling
After transformation, StandardScaler was applied.
from sklearn.preprocessing import StandardScalerscaler = StandardScaler()rfm_scaled = scaler.fit_transform(rfm_transformed)


The resulting features have approximately:
Mean ≈ 0
Standard Deviation ≈ 1

This is important because K-Means uses distance calculations.
📉 PCA
PCA (Principal Component Analysis) was used for dimensionality reduction.
Initially, all three RFM features were used.
Explained variance:
PC1 → 71.97%
PC2 → 24.63%
PC3 →  3.40%

The first two components retain:
71.97% + 24.63%
= 96.60%

of the total variance.
Therefore, two components were selected:
pca = PCA(n_components=2)rfm_pca = pca.fit_transform(rfm_scaled)


Final representation:
RFM (3 dimensions)
       ↓
      PCA
       ↓
PC1 + PC2
       ↓
96.6% variance retained

🚀 Current Status
Completed
- ✅ Data generation
- ✅ Data cleaning
- ✅ PostgreSQL database
- ✅ SQL joins and analytics
- ✅ customer_analytics table
- ✅ Python–PostgreSQL connection
- ✅ EDA
- ✅ Feature engineering
- ✅ Categorical encoding
- ✅ RFM analysis
- ✅ Skewness analysis
- ✅ Yeo-Johnson transformation
- ✅ Standardization
- ✅ PCA
- ✅ 96.6% variance retained with 2 components

**Key Learning
The important part of this project isn't just applying algorithms. The pipeline demonstrates why each technique was used:
SQL → create customer-level analytical data
RFM → represent customer purchasing behavior
Yeo-Johnson → reduce severe skewness
Scaling → make features comparable for distance-based algorithms
PCA → reduce dimensions while retaining 96.6% variance
K-Means → discover meaningful customer segments
FP-Growth → discover products frequently purchased together
Recommendation Engine → turn those patterns into actionable recommendations




“K=4 was selected using the Elbow Method and Silhouette Score, balancing cluster compactness with meaningful customer segmentation.”



| Cluster | Segment | Business Meaning |
|---|---|---|
| **0** | Recent / Low-Value | Recently purchased but low engagement |
| **1** | At-Risk / Dormant | Inactive and low spending |
| **2** | Regular / Mid-Value | Reasonably engaged customers |
| **3** | High-Value Loyal | Most valuable and engaged |


🧠 What are we doing with RFM?
Think about the problem from a retail company's perspective.
You have 5,000 customers.
The company doesn't want to treat all 5,000 customers the same.
For example:
Customer A bought something 20 days ago, has made 15 orders, and spent ₹20,000.

versus
Customer B bought something 400 days ago, made only 1 order, and spent ₹800.

Clearly, these are very different customers.
So we need a way to describe customer purchasing behavior.
That's where RFM comes in.