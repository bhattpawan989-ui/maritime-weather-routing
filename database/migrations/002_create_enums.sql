-- Enumerated types for voyage and prediction domains

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'voyage_status') THEN
        CREATE TYPE voyage_status AS ENUM (
            'draft',
            'planned',
            'active',
            'completed',
            'cancelled'
        );
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'risk_level') THEN
        CREATE TYPE risk_level AS ENUM (
            'safe',
            'moderate',
            'dangerous'
        );
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'recommendation_status') THEN
        CREATE TYPE recommendation_status AS ENUM (
            'pending',
            'accepted',
            'rejected',
            'superseded'
        );
    END IF;
END
$$;
