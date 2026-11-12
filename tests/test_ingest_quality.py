"""Ingest quality tests — schema, nulls, range, provenance."""

import json

import pandas as pd

from beie.ingest.cpi_mospi import CPIMoSPIImporter
from beie.ingest.crude_ppac import CrudePPACImporter
from beie.ingest.fuel_prices import FuelPricesImporter
from beie.ingest.io_table import IOTableImporter


def test_cpi_importer_loads_and_validates():
    imp = CPIMoSPIImporter()
    result = imp.run()
    df = result["data"]
    qr = result["quality_report"]
    assert isinstance(df, pd.DataFrame)
    assert len(df) >= 9
    assert "cpi_inflation" in df.columns
    assert qr["quality_status"] in ("verified", "warning")
    assert df["cpi_inflation"].isnull().sum() == 0


def test_crude_importer_loads_and_validates():
    imp = CrudePPACImporter()
    result = imp.run()
    df = result["data"]
    assert df["price_usd_bbl"].min() > 20
    assert df["price_usd_bbl"].max() < 200


def test_fuel_prices_importer():
    imp = FuelPricesImporter()
    result = imp.run()
    df = result["data"]
    assert "price_inr_per_litre" in df.columns
    assert df["price_inr_per_litre"].between(60, 200).all()


def test_io_table_importer():
    imp = IOTableImporter()
    result = imp.run()
    data = result["data"]
    assert data["n_sectors"] == 15
    assert len(data["crude_cost_share_ac"]) == 15


def test_cpi_provenance_sidecar_exists():
    from beie.ingest.base import RAW_DIR

    prov = RAW_DIR / "mospi_cpi_2026.provenance.json"
    assert prov.exists(), f"Provenance sidecar missing: {prov}"
    with open(prov) as f:
        p = json.load(f)
    assert "source_name" in p
    assert "retrieved_at" in p
    assert "licence_or_terms" in p
