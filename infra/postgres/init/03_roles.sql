-- =============================================================================
-- TransactCo · analytics_ro (the seal on the oracle)
--
-- `make land` connects as this role and no other. It can read public.* and it
-- cannot read _control.* -- not by convention, by permission.
--
-- This matters because of what happens in the Incident Exercise. The student points a capable
-- agent at this database and asks it to find what broke. If the answer key were
-- protected only by a landing script that declines to copy it, the agent could
-- simply query it and win the exercise without detecting anything. Postgres
-- refusing the SELECT is the only version of that promise that holds.
--
-- `make land` proves the seal on every run by attempting to read the answer key
-- as this role and showing you the permission error.
--
-- The password is a literal because this database is a local teaching fixture
-- that ships with its own credentials in .env.example. Nothing here is secret.
-- =============================================================================

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'analytics_ro') THEN
        CREATE ROLE analytics_ro LOGIN PASSWORD 'analytics_ro';
    END IF;

    EXECUTE format('GRANT CONNECT ON DATABASE %I TO analytics_ro', current_database());
END
$$;

GRANT USAGE ON SCHEMA public TO analytics_ro;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO analytics_ro;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO analytics_ro;

-- Explicit, though _control grants nothing to PUBLIC by default. Stated out
-- loud so the intent survives someone editing this file later.
REVOKE ALL ON SCHEMA _control FROM PUBLIC;
REVOKE ALL ON ALL TABLES IN SCHEMA _control FROM PUBLIC;
REVOKE ALL ON SCHEMA _control FROM analytics_ro;
REVOKE ALL ON ALL TABLES IN SCHEMA _control FROM analytics_ro;
