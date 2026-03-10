-- =============================================================
-- Migration: Create marketplace_listings table
-- Database: Supabase PostgreSQL (kyjocmwdjvciwozfrjqh)
-- =============================================================
-- Run this SQL in the Supabase SQL Editor:
--   https://supabase.com/dashboard/project/kyjocmwdjvciwozfrjqh/sql
-- =============================================================

-- Enable UUID generation if not already enabled
create extension if not exists "pgcrypto";

-- ------------------------------------------------------------
-- marketplace_listings
-- ------------------------------------------------------------
create table if not exists public.marketplace_listings (
    id            uuid primary key default gen_random_uuid(),
    credit_id     uuid not null references public.credits(id) on delete cascade,
    seller_wallet text not null,
    price         numeric(18, 8) not null check (price > 0),
    status        text not null default 'active'
                      check (status in ('active', 'sold', 'cancelled')),
    created_at    timestamptz not null default now(),
    updated_at    timestamptz not null default now()
);

-- Auto-update updated_at on row change
create or replace function public.set_updated_at()
returns trigger language plpgsql as $$
begin
    new.updated_at = now();
    return new;
end;
$$;

drop trigger if exists trg_marketplace_listings_updated_at on public.marketplace_listings;
create trigger trg_marketplace_listings_updated_at
    before update on public.marketplace_listings
    for each row execute function public.set_updated_at();

-- Indexes for common query patterns
create index if not exists idx_marketplace_listings_status
    on public.marketplace_listings (status);

create index if not exists idx_marketplace_listings_seller_wallet
    on public.marketplace_listings (seller_wallet);

create index if not exists idx_marketplace_listings_credit_id
    on public.marketplace_listings (credit_id);

-- ------------------------------------------------------------
-- Row Level Security (optional — enable if using RLS)
-- ------------------------------------------------------------
-- alter table public.marketplace_listings enable row level security;

-- Allow authenticated users to read active listings
-- create policy "Anyone can view active listings"
--     on public.marketplace_listings
--     for select using (status = 'active');

-- Allow authenticated users to insert their own listings
-- create policy "Authenticated users can create listings"
--     on public.marketplace_listings
--     for insert with check (auth.role() = 'authenticated');

comment on table public.marketplace_listings is
    'Tracks environmental credits listed for sale on the marketplace.';
