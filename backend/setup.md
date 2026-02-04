# Backend Setup

## Database Setup

Run the seed script to create tables and populate sample data:

```bash
.venv\Scripts\Activate
python -m scripts.seed_data
```

This will:
- Drop all existing tables
- Create new schema with all tables
- Seed businesses, categories, menu items, users, and FAQs from CSV files
