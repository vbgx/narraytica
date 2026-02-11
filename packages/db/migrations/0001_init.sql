-- TODO: stub (generated template) — fill when implementing

-- Common trigger function used by multiple tables
CREATE OR REPLACE FUNCTION narralytica_set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Common trigger function used by multiple tables
