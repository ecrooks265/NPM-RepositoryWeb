import json
import os
import tarfile
import tempfile
import subprocess
import requests
from tqdm import tqdm
from datetime import datetime

DEPENDENCY_AUDIT = "dependency_audit.json"
OUTPUT_FILE = "nodemedic_results.json"
DEBUG_LOG = "nm_debug.log"

DOCKER_IMAGE = "nodemedic-fine:latest"


# --------------------
# LOGGING UTILITIES
# --------------------
def log(msg):
    timestamp = datetime.utcnow().strftime("[%Y-%m-%d %H:%M:%S]")
    line = f"{timestamp} {msg}"
    print(line)
    with open(DEBUG_LOG, "a") as f:
        f.write(line + "\n")


# --------------------
# TAR SAFE EXTRACTION
# --------------------
def safe_extract_tar(path_to_tar, extract_to):
    with tarfile.open(path_to_tar, "r:gz") as tar:
        for m in tar.getmembers():
            member_path = os.path.join(extract_to, m.name)
            if not os.path.commonprefix([extract_to, member_path]) == extract_to:
                raise Exception(f"Unsafe tar path detected: {m.name}")
        tar.extractall(extract_to)


# --------------------
# DOWNLOAD TAR
# --------------------
def download_tarball(url, dest):
    try:
        r = requests.get(url, timeout=20)
        if r.status_code != 200:
            return False

        with open(dest, "wb") as f:
            f.write(r.content)

        log(f"Downloaded tarball {url} → {dest} ({len(r.content)} bytes)")
        return True

    except Exception as e:
        log(f"Download failed for {url}: {e}")
        return False


# --------------------
# RUN NODEMEDIC (Docker)
# --------------------
def run_nodemedic_docker(package_dir):
    output_file = os.path.join(package_dir, "nodemedic.json")

    cmd = [
        "docker", "run", "--rm",
        "-v", f"{package_dir}:/analysis",
        DOCKER_IMAGE,
        "--package-dir", "/analysis",
        "--output", "/analysis/nodemedic.json"
    ]

    log(f"Running NodeMedic: {' '.join(cmd)}")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300
        )
    except Exception as e:
        log(f"[FATAL] Docker run crashed: {e}")
        return {"error": f"Docker crash: {str(e)}"}

    log(f"NodeMedic stdout:\n{result.stdout}")
    log(f"NodeMedic stderr:\n{result.stderr}")

    if result.returncode != 0:
        log(f"NodeMedic failed with exit code {result.returncode}")
        return {"error": f"NodeMedic failed: {result.stderr}"}

    # read the output file
    if os.path.exists(output_file):
        log(f"NodeMedic output found for package: {package_dir}")
        try:
            with open(output_file) as f:
                return json.load(f)
        except Exception as e:
            return {"error": f"Failed reading NodeMedic output: {e}"}

    log("NodeMedic output missing!")
    return {"error": "NodeMedic output missing"}


# --------------------
# MAIN PIPELINE
# --------------------
def main():
    log("=== NodeMedic Batch Run Started ===")

    with open(DEPENDENCY_AUDIT) as f:
        audit = json.load(f)

    metadata = audit["metadata"]
    results = {}

    log(f"Processing {len(metadata)} packages")

    for pkg, meta in tqdm(metadata.items()):
        log(f"\n--- PACKAGE: {pkg} ---")

        latest = meta.get("dist-tags", {}).get("latest")
        if not latest:
            log("No latest version found, skipping")
            results[pkg] = {"error": "no_latest"}
            continue

        version_info = meta["versions"].get(latest, {})
        tarball = version_info.get("dist", {}).get("tarball")
        if not tarball:
            log("No tarball URL found, skipping")
            results[pkg] = {"error": "no_tarball"}
            continue

        with tempfile.TemporaryDirectory() as tmpdir:
            tar_path = os.path.join(tmpdir, "pkg.tgz")

            # DOWNLOAD
            if not download_tarball(tarball, tar_path):
                results[pkg] = {"error": "download_failed"}
                continue

            # EXTRACT
            try:
                safe_extract_tar(tar_path, tmpdir)
                log("Extraction successful")
            except Exception as e:
                log(f"Extraction error: {e}")
                results[pkg] = {"error": f"extract_failed: {e}"}
                continue

            pkg_dir = os.path.join(tmpdir, "package")
            if not os.path.isdir(pkg_dir):
                log("Extracted directory missing: expected /package")
                results[pkg] = {"error": "no_package_dir"}
                continue

            # RUN NODEMEDIC
            results[pkg] = run_nodemedic_docker(pkg_dir)

    # WRITE FINAL OUTPUT
    with open(OUTPUT_FILE, "w") as f:
        json.dump(results, f, indent=2)

    log("=== NodeMedic Batch Run Complete ===")
    log(f"Results saved → {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
