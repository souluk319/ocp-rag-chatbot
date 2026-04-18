# final_surface_legacy_catalog_retirement_20260418

- verified canonical grade normalization was already landed; remaining user-facing drift was legacy catalog exposure in PlaybookLibrary
- confirmed default surface still exposed `Gold Source Books` and `Derived Playbooks` cards, and retained dead `Full Source Catalog` popover routing
- removed legacy `known/manual/derived` metric popover paths from `PlaybookLibraryPage.tsx`
- removed `Gold Source Books` and `Derived Playbooks` cards from the default metrics grid
- tightened runtime UI test so old catalog labels and popover hooks cannot quietly return
- focused validation passed: `py_compile`, `pytest tests/test_app_runtime_ui.py -q`, `npm run build`
