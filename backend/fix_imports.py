#!/usr/bin/env python3
"""
Script to fix common import issues in the backend
"""
import re
import os


def remove_unused_imports():
    """Remove commonly unused imports"""
    fixes = [
        # Remove unused numpy imports
        (r"^import numpy as np\n", ""),
        (r"^from typing import.*Optional.*\n", ""),
        (r"^from typing import.*Tuple.*\n", ""),
        (r"^import pandas as pd\n(?=.*\n.*def)", ""),
        (r"^from datetime import datetime\n(?=.*\n.*def)", ""),
        (r"^import os\n(?=.*\n.*def)", ""),
        (r"^import json\n(?=.*\n.*def)", ""),
    ]

    # Files that typically have these issues
    target_files = [
        "ai_server.py",
        "ai_server_fallback.py",
        "auth/auth_utils.py",
        "auth/firebase_auth.py",
        "blockchain.py",
        "comprehensive_ai_diagnosis.py",
        "continuous_learning.py",
        "medical_recommendations.py",
        "medichain_ai.py",
    ]

    for filename in target_files:
        filepath = os.path.join(".", filename)
        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()

                original_content = content

                # Apply fixes
                for pattern, replacement in fixes:
                    if "numpy" in pattern and "numpy" not in content.lower():
                        continue
                    content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

                # Only write if changed
                if content != original_content:
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(content)
                    print(f"Fixed imports in {filename}")
            except Exception as e:
                print(f"Error processing {filename}: {e}")


if __name__ == "__main__":
    remove_unused_imports()
