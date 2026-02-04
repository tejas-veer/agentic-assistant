-- Migration script to add 'assigned' value to resourcestatus enum
-- Run this against your PostgreSQL database

-- Add 'assigned' to the resourcestatus enum type
ALTER TYPE resourcestatus ADD VALUE IF NOT EXISTS 'assigned';

-- If you need to remove 'occupied' (PostgreSQL doesn't allow removing enum values directly),
-- you would need to recreate the type. For now, the above should fix the immediate issue.
