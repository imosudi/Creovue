import os
import stat
import sys
import subprocess
from pathlib import Path

def setup_matplotlib_cache():
    cache_dir = Path('/tmp/mpl_cache')
    try:
        # Try to create directory
        cache_dir.mkdir(mode=0o755, exist_ok=True)
        
        # Try to set ownership (will only work if running as root)
        try:
            subprocess.run(['chown', 'www-data:www-data', str(cache_dir)], check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠️  Could not set ownership - run as root for proper setup")
            print("\n", "chmod +x ./setup_matplotlib_cache.sh", "\n", "sudo ./setup_matplotlib_cache.sh")
        
        # Verify permissions
        if not cache_dir.is_dir():
            raise RuntimeError("Cache directory creation failed")
            
        os.environ['MPLCONFIGDIR'] = str(cache_dir)
        return True
        
    except Exception as e:
        print(f"❌ Automatic setup failed: {str(e)}")
        print("\nPlease run manually as root:")
        print("  mkdir -p /tmp/mpl_cache")
        print("  chown www-data:www-data /tmp/mpl_cache")
        print("  chmod 755 /tmp/mpl_cache")
        return False

if not setup_matplotlib_cache():
    sys.exit(1)