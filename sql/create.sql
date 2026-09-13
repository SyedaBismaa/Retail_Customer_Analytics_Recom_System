
-- DROP TABLE IF EXISTS order_items;
-- DROP TABLE IF EXISTS orders;
-- DROP TABLE IF EXISTS products;
-- DROP TABLE IF EXISTS customers;

CREATE TABLE customers (
    customer_id VARCHAR(12) PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    age NUMERIC(5,1),
    gender VARCHAR(20),
    city VARCHAR(100),
    state VARCHAR(100),
    customer_since DATE,
    occupation VARCHAR(100),
    income NUMERIC(12,2),
    marital_status VARCHAR(30),
    preferred_channel VARCHAR(30),
    loyalty_tier VARCHAR(30)
);


CREATE TABLE products (
    product_id VARCHAR(12) PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    subcategory VARCHAR(100),
    brand VARCHAR(100),
    price NUMERIC(12,2),
    cost NUMERIC(12,2),
    discount NUMERIC(5,2),
    stock_quantity INTEGER,
    product_rating NUMERIC(2,1)
);


CREATE TABLE orders (
    order_id VARCHAR(12) PRIMARY KEY,
    customer_id VARCHAR(12) NOT NULL,
    order_date DATE NOT NULL,
    order_status VARCHAR(30),
    sales_channel VARCHAR(30),
    payment_method VARCHAR(50),
    shipping_city VARCHAR(100),
    shipping_state VARCHAR(100),
    total_order_value NUMERIC(12,2),

    CONSTRAINT orders_customer_fk
        FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id)
);


CREATE TABLE order_items (
    order_item_id VARCHAR(14) PRIMARY KEY,
    order_id VARCHAR(12) NOT NULL,
    product_id VARCHAR(12) NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price NUMERIC(12,2),
    discount NUMERIC(5,2),
    item_total NUMERIC(12,2),

    CONSTRAINT order_items_order_fk
        FOREIGN KEY (order_id)
        REFERENCES orders(order_id),

    CONSTRAINT order_items_product_fk
        FOREIGN KEY (product_id)
        REFERENCES products(product_id)
);