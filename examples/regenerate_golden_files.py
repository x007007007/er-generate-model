#!/usr/bin/env python3
"""
Regenerate all golden files in the examples directory.

This script traverses the examples directory and regenerates all output files
by executing the actual conversion commands.
"""
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple


class GoldenFileRegenerator:
    """Regenerates golden files by executing conversion commands."""
    
    def __init__(self, examples_dir: Path):
        self.examples_dir = examples_dir
        self.successes: List[str] = []
        self.failures: List[Tuple[str, str]] = []
    
    def regenerate_all(self):
        """Regenerate all golden files."""
        print("=" * 80)
        print("Regenerating Golden Files")
        print("=" * 80)
        print()
        
        # Regenerate toml-to-output examples
        self.regenerate_toml_to_output()
        
        # Regenerate input-to-toml examples (if conversion is supported)
        # Currently skipped as the tool may not support all conversions
        
        # Print summary
        self.print_summary()
    
    def regenerate_toml_to_output(self):
        """Regenerate toml-to-output golden files."""
        print("Regenerating toml-to-output examples...")
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
                
                self.regenerate_example(platform, example_dir, input_file)
    
    def regenerate_example(self, platform: str, example_dir: Path, input_file: Path):
        """Regenerate a single example."""
        example_name = f"{platform}/{example_dir.name}"
        print(f"  Processing {example_name}...")
        
        try:
            if platform == "mermaid":
                # Mermaid outputs to a single file
                output_file = example_dir / "output.mmd"
                cmd = [
                    "uv", "run", "er-convert", "convert",
                    str(input_file),
                    "-f", "mermaid",
                    "-o", str(output_file)
                ]
            else:
                # Django and SQLAlchemy output to a directory
                output_dir = example_dir / "output"
                output_dir.mkdir(exist_ok=True)
                cmd = [
                    "uv", "run", "er-convert", "convert",
                    str(input_file),
                    "-f", platform,
                    "-d", str(output_dir) + "/"
                ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.examples_dir.parent
            )
            
            if result.returncode == 0:
                self.successes.append(example_name)
                print(f"    ✓ Success")
            else:
                error_msg = result.stderr or result.stdout
                self.failures.append((example_name, error_msg))
                print(f"    ✗ Failed: {error_msg[:100]}")
        
        except Exception as e:
            self.failures.append((example_name, str(e)))
            print(f"    ✗ Exception: {e}")
    
    def print_summary(self):
        """Print summary of regeneration results."""
        print()
        print("=" * 80)
        print("Summary")
        print("=" * 80)
        print(f"Total successes: {len(self.successes)}")
        print(f"Total failures: {len(self.failures)}")
        print()
        
        if self.successes:
            print("Successful regenerations:")
            for success in self.successes:
                print(f"  ✓ {success}")
            print()
        
        if self.failures:
            print("Failed regenerations:")
            for example, error in self.failures:
                print(f"  ✗ {example}")
                print(f"    Error: {error[:200]}")
            print()
            sys.exit(1)


def main():
    """Main entry point."""
    script_dir = Path(__file__).parent
    regenerator = GoldenFileRegenerator(script_dir)
    regenerator.regenerate_all()


if __name__ == "__main__":
    main()
