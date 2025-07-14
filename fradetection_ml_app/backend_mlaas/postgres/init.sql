CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    v1 FLOAT, v2 FLOAT, v3 FLOAT, v4 FLOAT, v5 FLOAT,
    v6 FLOAT, v7 FLOAT, v8 FLOAT, v9 FLOAT, v10 FLOAT,
    v11 FLOAT, v12 FLOAT, v13 FLOAT, v14 FLOAT, v15 FLOAT,
    v16 FLOAT, v17 FLOAT, v18 FLOAT, v19 FLOAT, v20 FLOAT,
    v21 FLOAT, v22 FLOAT, v23 FLOAT, v24 FLOAT, v25 FLOAT,
    v26 FLOAT, v27 FLOAT, v28 FLOAT,
    amount FLOAT,
    label INT,            -- 1 = fraud, 0 = legit (optional)
    scored BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS fraud_scores (
    id SERIAL PRIMARY KEY,
    transaction_id INT REFERENCES transactions(id),
    fraud_prob FLOAT,
    predicted_label INT,
    scored_at TIMESTAMP DEFAULT NOW()
);
