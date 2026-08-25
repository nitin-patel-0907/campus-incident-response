#!/usr/bin/env python3
"""
Quick Start Demo on Port 8080
Builds frontend and starts unified server with analytics
"""
import subprocess
import sys
import os
from pathlib import Path


def main():
    """Start the complete demo"""
    print("🚀 STARTING CAMPUS INCIDENT RESPONSE DEMO")
    print("=" * 50)

    # Resolve paths relative to the scripts/ directory
    scripts_dir = Path(__file__).resolve().parent
    project_root = scripts_dir.parent
    data_dir = project_root / "data"
    frontend_dir = project_root / "frontend"

    # Check if demo data exists
    analytics_file = data_dir / "analytics_data.json"
    if not analytics_file.exists():
        print("📊 No demo data found. Generating...")
        data_gen = scripts_dir / "generate_performance_data.py"
        if data_gen.exists():
            try:
                result = subprocess.run(
                    [sys.executable, str(data_gen)],
                    cwd=str(project_root),
                    capture_output=True,
                    text=True,
                )
                if result.returncode == 0:
                    print("✅ Demo data generated successfully")
                else:
                    print(f"⚠️  Demo data generation had issues: {result.stderr}")
            except Exception as e:
                print(f"⚠️  Could not generate demo data: {e}")
        else:
            print("⚠️  Data generator script not found, skipping")
    else:
        print("✅ Demo data already exists")

    # Build frontend
    if frontend_dir.exists():
        print("\n📦 Building frontend...")
        try:
            # Install dependencies if needed
            if not (frontend_dir / "node_modules").exists():
                print("   Installing dependencies...")
                subprocess.run(
                    ["npm", "install"],
                    cwd=str(frontend_dir),
                    check=True,
                )

            # Build the frontend
            print("   Building React app...")
            subprocess.run(
                ["npm", "run", "build"],
                cwd=str(frontend_dir),
                check=True,
            )
            print("✅ Frontend built successfully")

        except subprocess.CalledProcessError as e:
            print(f"❌ Frontend build failed: {e}")
            print("⚠️  Continuing with API-only mode...")
        except Exception as e:
            print(f"❌ Frontend build error: {e}")
            print("⚠️  Continuing with API-only mode...")
    else:
        print("⚠️  Frontend directory not found - API only mode")

    # Start the unified server
    server_script = scripts_dir / "start_unified_server.py"
    print("\n🌐 Starting unified server on port 8080...")
    try:
        subprocess.run(
            [sys.executable, str(server_script)],
            cwd=str(project_root),
        )
    except KeyboardInterrupt:
        print("\n👋 Demo stopped")
    except Exception as e:
        print(f"❌ Server error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())