"""Compatibility marker for the split Patch 15.1 parser test modules.

The point-binding parser contract is intentionally distributed across focused
``test_*`` modules in this package. Keeping this tiny module ensures archive
patch application replaces the former monolithic test file instead of leaving
duplicate tests behind.
"""
