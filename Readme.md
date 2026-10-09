# Retail Customer Analytics & Recommendation System

An end-to-end retail analytics and product recommendation project built using Python, PostgreSQL, SQL, and Machine Learning.

The project analyzes customer purchasing behavior, identifies customer segments, discovers relationships between products, and generates personalized product recommendations based on purchase history.

## 1. Project Objectives

The main objectives are to:

- Analyze customer purchasing behavior and spending patterns.
- Perform customer segmentation using RFM analysis and K-Means clustering.
- Discover products frequently purchased together using the FP-Growth algorithm.
- Generate product recommendations using association rules.
- Store and analyze relational retail data using PostgreSQL and SQL.

## 2. Technology Stack

- **Programming:** Python
- **Database:** PostgreSQL
- **Data Analysis:** Pandas, NumPy
- **Data Visualization:** Matplotlib, Seaborn
- **Machine Learning:** Scikit-learn
- **Recommendation System:** MLxtend, FP-Growth
- **Database Connectivity:** SQLAlchemy
- **Development Environment:** Jupyter Notebook

## 3. Dataset Description

The project uses four related datasets containing synthetic retail data.

| Dataset | Description |
|---|---|
| Customers | Customer demographics, location, occupation, income, and loyalty tier |
| Products | Product names, categories, brands, prices, costs, and inventory |
| Orders | Customer orders, dates, order status, payment methods, and sales channels |
| Order Items | Products purchased in each order, quantities, discounts, and item totals |

The datasets are connected through customer IDs, order IDs, and product IDs.

**Note:** The data is synthetic and intended for learning and demonstration. The discovered purchasing patterns should not be interpreted as verified real-world customer behavior.

## 4. Data Cleaning and PostgreSQL Integration

The raw datasets were cleaned and prepared before being loaded into PostgreSQL.

SQL was used to combine the tables, validate relationships, and perform customer-level and product-level analysis.

Key SQL concepts used include:

- INNER JOINs and other table joins
- Aggregate functions such as SUM, COUNT, and AVG
- Common Table Expressions (CTEs)
- CASE WHEN statements
- Window functions such as ROW_NUMBER(), RANK(), and LAG()

A customer-level analytical table named `customer_analytics` was created. It contains information such as total orders, total spending, average order value, first and last order dates, unique products purchased, favorite category, and customer value segment.

The table was loaded into Python using Pandas and SQLAlchemy.

## 5. Exploratory Data Analysis and Feature Engineering

Exploratory Data Analysis (EDA) was performed to understand customer demographics, spending patterns, missing values, feature distributions, skewness, and potential outliers.

Feature engineering included:

- One-hot encoding for categorical features such as gender, occupation, state, and preferred channel.
- Frequency encoding for city.
- Ordinal encoding for loyalty tiers.
- Creating a `has_purchase` feature to distinguish customers who have purchased from those who have not.

Customers with no purchase history were retained separately because meaningful RFM values could not be calculated for them.

## 6. Customer Segmentation

Customer segmentation was performed using **RFM analysis and K-Means clustering**.

### RFM Analysis

RFM represents three aspects of customer purchasing behavior:

- **Recency:** Number of days since the customer's last purchase.
- **Frequency:** Total number of orders placed.
- **Monetary:** Total amount spent by the customer.

Out of 5,000 customers, 4,400 customers with purchase history were used for RFM clustering. The remaining 600 customers were assigned a separate `No Purchase` segment.

### Data Transformation and Scaling

The RFM features were highly skewed, particularly monetary value. The Yeo-Johnson transformation was applied to reduce skewness, followed by StandardScaler to bring the features to comparable scales.

### Dimensionality Reduction

Principal Component Analysis (PCA) was used to reduce the three RFM features to two principal components while retaining approximately **96.60% of the total variance**.

### K-Means Clustering

K-Means was used to group customers based on their purchasing behavior. Four clusters were selected to provide useful and interpretable customer segments.

| Segment | Business Interpretation |
|---|---|
| Recent / Low-Value | Recently active customers with relatively low spending |
| At-Risk / Dormant | Customers who have not purchased recently and generally spend less |
| Regular / Mid-Value | Customers with regular purchasing activity and moderate spending |
| High-Value Loyal | Customers with frequent purchases and high spending |
| No Purchase | Customers without purchase history |

The cluster labels were interpreted using the original RFM values rather than the transformed PCA components.

## 7. Product Recommendation System

The recommendation system identifies product relationships using historical order transactions.

### Transaction Preparation

The orders, order items, and products tables were joined to create transaction-level data.

Each order was treated as one transaction. A Boolean basket matrix was then created using `TransactionEncoder`.

- `True` indicates that a product appeared in an order.
- `False` indicates that it did not.

The complete basket matrix contained **30,033 transactions and 208 products**.

### FP-Growth Algorithm

FP-Growth was used to identify frequently occurring product combinations without generating candidate itemsets in the same way as the Apriori algorithm.

The minimum support threshold was adjusted to identify more product combinations.

### Association Rules

Association rules were generated from frequent itemsets to identify relationships between products.

For example:

`Product A → Product B`

This represents a pattern in which orders containing Product A are also associated with Product B.

Three metrics were used to understand these relationships:

- **Support:** The proportion of transactions containing the itemset.
- **Confidence:** How often the consequent appears when the antecedent appears.
- **Lift:** How much more frequently the products occur together compared with what would be expected if they were independent.

The candidate rules were filtered using these thresholds:

- Confidence ≥ 0.20
- Lift > 2
- Support ≥ 0.002

These thresholds were selected for experimentation and are not universal standards.

### Recommendation Logic

The recommendation function follows these steps:

1. Takes a customer's previously purchased products as input.
2. Finds association rules whose antecedents match the customer's purchase history.
3. Excludes products the customer has already purchased.
4. Ranks matching products using rule metrics.
5. Returns up to five recommendations.
6. Uses a popularity-based fallback when there are not enough rule-based recommendations.

The engine supports two recommendation sources:

- **Association Rule:** Recommendations based on discovered product relationships.
- **Popularity Fallback:** Frequently purchased products used when personalized recommendations are insufficient.

Customer purchase history is retrieved from PostgreSQL.

## 8. Recommendation Evaluation

A time-based evaluation was performed using delivered orders to test recommendations against later purchases.

The data was divided into training and testing periods to prevent future transactions from being used to generate the training rules.

| Metric | Result |
|---|---:|
| Training orders | 18,886 |
| Testing orders | 4,743 |
| Customers evaluated | 2,148 |
| Mean Precision@5 | 3.63% |
| Mean Recall@5 | 3.87% |
| Customers with at least one hit | 331 |
| Hit rate | 15.4% |

Precision@5 measures the proportion of the five recommended products that appeared in the customer's later purchases. Recall@5 measures the proportion of distinct products purchased later that were included in the recommendations.

These results provide a baseline for a learning project using synthetic data. They should not be treated as evidence of real-world recommendation performance.

## 9. Project Workflow

The overall pipeline is:

Raw Retail Data → Data Cleaning → PostgreSQL → SQL Analytics → EDA → Feature Engineering → RFM Analysis → PCA → K-Means Segmentation

For product recommendations:

Orders + Order Items + Products → Transaction Preparation → Basket Matrix → FP-Growth → Association Rules → Recommendation Engine → Evaluation

## 10. Current Project Status

Completed:

- Data generation and cleaning
- PostgreSQL database setup
- SQL joins and customer analytics
- Python–PostgreSQL integration
- Exploratory Data Analysis
- Feature engineering and categorical encoding
- RFM analysis and customer segmentation
- Yeo-Johnson transformation and feature scaling
- PCA dimensionality reduction
- K-Means clustering
- FP-Growth frequent itemset mining
- Association rule generation and filtering
- Product recommendation function
- Popularity-based fallback
- Time-based recommendation evaluation

**Next Step:** Integrate the completed analytics and recommendation logic into a web application using Next.js, FastAPI, SQLAlchemy, and PostgreSQL.

## 11. Key Learnings

This project demonstrates how SQL, data analysis, and machine learning can work together in a retail use case.

- SQL transforms relational data into useful analytical datasets.
- RFM analysis represents customer purchasing behavior.
- Yeo-Johnson transformation reduces skewness in numerical features.
- Standardization makes features comparable for distance-based algorithms.
- PCA reduces dimensionality while retaining important information.
- K-Means identifies groups of customers with similar purchasing behavior.
- FP-Growth discovers frequently occurring product combinations.
- Association rules and popularity fallback convert purchasing patterns into product recommendations.

The project provided practical experience in building a data pipeline, analyzing customer behavior, developing a recommendation engine, and evaluating its initial performance.