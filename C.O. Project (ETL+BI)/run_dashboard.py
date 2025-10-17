#!/usr/bin/env python3
"""Launch Container Offices BI Dashboard."""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from dashboard.app_simple import app

if __name__ == '__main__':
    print("=" * 60)
    print("Container Offices BI Dashboard")
    print("=" * 60)
    print("\n✓ Loading data from warehouse...")
    print("✓ Starting dashboard server...")
    print("\n🌐 Open your browser to: http://127.0.0.1:8050")
    print("\n📊 Available views:")
    print("  - KPI Summary Cards")
    print("  - Revenue & Occupancy Trends")
    print("  - Building A vs B Comparison")
    print("  - Collection Rate Analysis")
    print("  - Suite Details Table (filterable)")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 60)
    print()

    app.run(debug=False, host='127.0.0.1', port=8050)
