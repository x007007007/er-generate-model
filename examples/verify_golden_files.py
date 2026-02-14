#!/usr/bin/env python3
"""
Verify all golden files in the examples directory.

This script compares actual conversion output with the golden files to ensure
they match.
"""
import os
import subprocess
import sys
import tempfile
import filecmp
import difflib
from pathlib import Path
from typing import List, Tuple


class GoldenFileVerifier:
    """Verifies golden files by comparing with actual conversion output."""
    
    def __init__(self, examples_dir: Path):
        self.examples_dir = examples_dir
        self.successes: List[str] = []
        self.failures: List[Tuple[str, str]] = []
    
    def verify_all(self):
        """Verify all golden files."""
        print("=" * 80)
        print("Verifying Golden Files")
        print("=" * 80)
        print()
        
        # Verify toml-to-output examples
        self.verify_toml_to_output()
        
        # Print summary
        self.print_summary()
    
    def verify_toml_to_output(self):
        """Verify toml-to-output golden files."""
        print("Verifying toml-to-output examples...")
        print("-" * 80)
        
        toml_to_output = self.examples_dir / "toml-to-output"
        
        for platform in ["django", "sqlalchemy", "mermaid"]:
            platform_dir = toml_to_output / platform
            if not platform_dir.exists():
                continue
            
            for example_dir in sorted(platform_dir.iterdir()):
                if not example_dir.is_dir() or example_dir.name == "__pycache__":
                    continue
                
                input_file = example_dir / "input.toml"
                if not input_file.exists():
                    continue
                
                self.verify_example(platform, example_dir, input_file)
    
    def verify_example(self, platform: str, example_dir: Path, input_file: Path):
        """Verify a single example."""
        example_name = f"{platform}/{example_dir.name}"
        print(f"  Verifying {example_name}...")
        
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                if platform == "mermaid":
                    # Mermaid outputs to a single file
                    golden_file = example_dir / "output.mmd"
                    temp_output = temp_path / "output.mmd"
                    
                    cmd = [
                        "uv", "run", "er-convert", "convert",
                        str(input_file),
                        "-f", "mermaid",
                        "-o", str(temp_output)
                    ]
                    
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        cwd=self.examples_dir.parent
                    )
                    
                    if result.returncode != 0:
                        error_msg = result.stderr or result.stdout
                        self.failures.append((example_name, f"Conversion failed: {error_msg}"))
                        print(f"    ✗ Conversion failed")
                        return
                    
                    # Compare files
                    if not golden_file.exists():
                        self.failures.append((example_name, "Golden file not found"))
                        print(f"    ✗ Golden file not found")
                        return
                    
                    if not filecmp.cmp(golden_file, temp_output, shallow=False):
                        diff = self.get_file_diff(golden_file, temp_output)
                        self.failures.append((example_name, f"Files differ:\n{diff}"))
                        print(f"    ✗ Files differ")
                        return
                
                else:
                    # Django and SQLAlchemy output to a directory
                    golden_dir = example_dir / "output"
                    temp_output_dir = temp_path / "output"
                    temp_output_dir.mkdir()
                    
                    cmd = [
                        "uv", "run", "er-convert", "convert",
                        str(input_file),
                        "-f", platform,
                        "-d", str(temp_output_dir) + "/"
                    ]
                    
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        cwd=self.examples_dir.parent
                    )
                    
                    if result.returncode != 0:
                        error_msg = result.stderr or result.stdout
                        self.failures.append((example_name, f"Conversion failed: {error_msg}"))
                        print(f"    ✗ Conversion failed")
                        return
                    
                    # Compare directories
                    if not golden_dir.exists():
                        self.failures.append((example_name, "Golden directory not found"))
                        print(f"    ✗ Golden directory not found")
                        return
                    
                    diff_result = self.compare_directories(golden_dir, temp_output_dir)
                    if diff_result:
                        self.failures.append((example_name, diff_result))
                        print(f"    ✗ Directories differ")
                        return
                
                self.successes.append(example_name)
                print(f"    ✓ Verified")
        
        except Exception as e:
            self.failures.append((example_name, str(e)))
            print(f"    ✗ Exception: {e}")
    
    def compare_directories(self, dir1: Path, dir2: Path) -> str:
        """Compare two directories and return differences."""
        dcmp = filecmp.dircmp(dir1, dir2)
        
        differences = []
        
        if dcmp.left_only:
            differences.append(f"Only in golden: {dcmp.left_only}")
        
        if dcmp.right_only:
            differences.append(f"Only in actual: {dcmp.right_only}")
        
        if dcmp.diff_files:
            differences.append(f"Different files: {dcmp.diff_files}")
            for file in dcmp.diff_files:
                diff = self.get_file_diff(dir1 / file, dir2 / file)
                differences.append(f"Diff for {file}:\n{diff}")
        
        return "\n".join(differences) if differences else ""
    
    def get_file_diff(self, file1: Path, file2: Path) -> str:
        """Get unified diff between two files."""
        with open(file1, 'r') as f1, open(file2, 'r') as f2:
            diff = difflib.unified_diff(
                f1.readlines(),
                f2.readlines(),
                fromfile=str(file1),
                tofile=str(file2),
                lineterm=''
            )
            return '\n'.join(list(diff)[:50])  # Limit to first 50 lines
    
    def print_summary(self):
        """Print summary of verification results."""
        print()
        print("=" * 80)
        print("Summary")
        print("=" * 80)
        print(f"Total verified: {len(self.successes)}")
        print(f"Total failed: {len(self.failures)}")
        print()
        
        if self.successes:
            print("Verified examples:")
            for success in self.successes:
                print(f"  ✓ {success}")
            print()
        
        if self.failures:
            print("Failed verifications:")
            for example, error in self.failures:
                print(f"  ✗ {example}")
                print(f"    Error: {error[:500]}")
            print()
            sys.exit(1)


def main():
    """Main entry point."""
    script_dir = Path(__file__).parent
    verifier = GoldenFileVerifier(script_dir)
    verifier.verify_all()


if __name__ == "__main__":
    main()
