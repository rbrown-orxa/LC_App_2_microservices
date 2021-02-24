

-- queries

CREATE TABLE
IF NOT EXISTS queries (
    id SERIAL PRIMARY KEY,
    started TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    success BOOLEAN NOT NULL DEFAULT FALSE,
    lat NUMERIC,
    lon NUMERIC,
    -- subscription_id UUID,
    -- plan_id TEXT,
    -- object_id UUID,
    completed TIMESTAMPTZ
    -- billed BOOLEAN NOT NULL DEFAULT FALSE,
    -- date_billed TIMESTAMPTZ 
);



-- subscriptiondetails

CREATE TABLE
    subscriptiondetails
    (
        id serial primary key,
        objectid uuid not null,
        subscriptionid uuid not null,
        subscriptionname text not null,
        offerid text not null,
        planid text not null,
        purchasertenantid uuid not null,
        subscriptionstatus text not null,
        created timestamptz not null default NOW(),
        unique(subscriptionid)
    );



-- lcappinputvalues

CREATE TABLE
IF NOT EXISTS lcappinputvalues (
    id SERIAL PRIMARY KEY,
    country TEXT,
    currency TEXT,
    import_cost_kwh numeric,
    export_price_kwh numeric,
    solarpv_installation_cost_kwp integer,
    storage_battery_system_cost_kwh integer,
    expected_life_solar_years integer,
    type TEXT,
    year integer,
    created_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    edischarge_cycles_battery integer
);


