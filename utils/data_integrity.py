import os
import json
import hashlib
import argparse
from pathlib import Path

DATA_DIR = "data/de"
LOCK_FILE = "data.lock"

def calculate_file_hash(filepath: str) -> str:
    """Calculates SHA256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def generate_lockfile():
    """Scans data directory and creates a lock file with hashes."""
    print(f"Generating lockfile from {DATA_DIR}...")
    manifest = {}
    
    if not os.path.exists(DATA_DIR):
        print(f"Error: Directory {DATA_DIR} not found.")
        return

    files = sorted(Path(DATA_DIR).glob("*.json"))
    for file_path in files:
        filename = file_path.name
        file_hash = calculate_file_hash(str(file_path))
        manifest[filename] = file_hash
    
    with open(LOCK_FILE, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, sort_keys=True)
        
    print(f"✅ Generated {LOCK_FILE} with {len(manifest)} entries.")

def verify_data():
    """Verifies local data against the lock file."""
    if not os.path.exists(LOCK_FILE):
        print(f"Error: {LOCK_FILE} not found. Run 'lock' first.")
        return

    print(f"Verifying data integrity against {LOCK_FILE}...")
    with open(LOCK_FILE, "r", encoding="utf-8") as f:
        manifest = json.load(f)
        
    missing_files = []
    mismatch_files = []
    passed_count = 0
    
    for filename, expected_hash in manifest.items():
        file_path = os.path.join(DATA_DIR, filename)
        
        if not os.path.exists(file_path):
            missing_files.append(filename)
            continue
            
        current_hash = calculate_file_hash(file_path)
        if current_hash != expected_hash:
            mismatch_files.append(filename)
        else:
            passed_count += 1
            
    # Report results
    print(f"\n=== Integrity Report ===")
    print(f"✅ Verified: {passed_count}")
    
    if missing_files:
        print(f"❌ Missing: {len(missing_files)} files")
        # print(missing_files[:5]) # Print first 5 to avoid spam
    
    if mismatch_files:
        print(f"⚠️ Changed/Corrupted: {len(mismatch_files)} files")
        # print(mismatch_files[:5])

    if not missing_files and not mismatch_files:
        print("\n✨ Data Integrity: PERFECT Match")
    else:
        print("\n⚠️ Data Integrity: ISSUES FOUND")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Data Integrity Tool")
    parser.add_argument("action", choices=["lock", "check"], help="Action to perform")
    args = parser.parse_args()
    
    if args.action == "lock":
        generate_lockfile()
    elif args.action == "check":
        verify_data()
