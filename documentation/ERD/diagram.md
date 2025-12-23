erDiagram
  USER ||--|| ACTIVE_GOAL : has
  USER ||--o{ GOAL : sets
  USER ||--o{ MEAL : creates
  USER ||--o{ PURCHASE : logs
  STORE ||--o{ OFFER : publishes
  PRODUCT ||--o{ OFFER : priced_as
  MEAL ||--o{ MEAL_ITEM : contains
  PRODUCT ||--o{ MEAL_ITEM : used_in
  PRODUCT ||--o{ PURCHASE : bought
  STORE ||--o{ PURCHASE : at

  
  USER {
    string user_id
    string email
    string password_hash
    string display_name
    datetime created_at
  }

  ACTIVE_GOAL {
    string user_id
    string goal_id
    string period
    datetime assigned_at
  }

  GOAL {
    string goal_id
    string user_id
    string period
    date start_date
    date end_date
    int kcal
    int protein_g
    int carbs_g
    int fat_g
    int sugars_g
    int sodium_mg
    int fiber_g
    int sat_fat_g
    int unsat_fat_g
    int trans_fat_g
  }

  PRODUCT {
    string product_id
    string name
    string brand
    string category
    string barcode
    int serving_size_g_ml
    string serving_unit
    float kcal_per_100g
    float protein_per_100g
    float carbs_per_100g
    float fat_per_100g
    float sugars_per_100g
    float sodium_mg_per_100g
    float fiber_per_100g
    float sat_fat_per_100g
    float unsat_fat_per_100g
    float trans_fat_per_100g
  }

  STORE {
    string store_id
    string retailer
    string name
    string postcode
  }

  OFFER {
    string offer_id
    string product_id
    string store_id
    float price
    float price_per_gram
    date valid_from
    date valid_to
  }

  MEAL {
    string meal_id
    string user_id
    string name
    boolean locked_totals
    datetime created_at
  }

  MEAL_ITEM {
    string meal_item_id
    string meal_id
    string product_id
    float quantity
    string unit
  }

  PURCHASE {
    string purchase_id
    string user_id
    string product_id
    string store_id
    datetime purchased_at
    float quantity
    string unit
    float unit_price
  }
