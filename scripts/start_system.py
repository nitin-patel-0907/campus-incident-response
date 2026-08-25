#!/usr/bin/env python3
"""
Simple startup script for the Campus Incident Response System
Runs the unified server on port 8080 with real incident processing
"""
import subprocess
import sys
import os
from pathlib import Path


def main():
    """Start the Campus Incident Response System"""
    print("🚀 Starting Campus Incident Response System")
    print("=" * 60)
    print("🎯 Real incident processing with evaluation reports")
    print("🌐 Server will run on: http://localhost:8080")
    print("=" * 60)

    # Resolve paths relative to the scripts/ directory
    scripts_dir = Path(__file__).resolve().parent
    project_root = scripts_dir.parent
    data_dir = project_root / "data"

    server_script = scripts_dir / "start_unified_server.py"
    if not server_script.exists():
        print("❌ Error: start_unified_server.py not found")
        print("   Please ensure the scripts/ directory is intact")
        return 1

    # Clean up any existing incident data to start fresh
    incidents_file = data_dir / "real_incidents.json"
    analytics_file = data_dir / "analytics_data.json"

    if incidents_file.exists():
        print("🧹 Cleaning up previous incident data...")
        os.remove(incidents_file)

    if analytics_file.exists():
        os.remove(analytics_file)

    print("✅ Starting unified server...")
    print("📱 Access the system at: http://localhost:8080")
    print("📊 Dashboard: http://localhost:8080")
    print("📝 Report Incident: http://localhost:8080 → Report Incident")
    print("📈 Analytics: http://localhost:8080 → AI Insights & Evaluation")
    print("📋 History: http://localhost:8080 → Incident History")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 60)

    try:
        # Start the unified server
        subprocess.run(
            [sys.executable, str(server_script)],
            cwd=str(project_root),
            check=True,
        )
    except KeyboardInterrupt:
        print("\n👋 System stopped by user")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Server error: {e}")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())