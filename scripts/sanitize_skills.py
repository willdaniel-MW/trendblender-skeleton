#!/usr/bin/env python3
"""
Sanitize skill SKILL.md files for packaging.
Fixes known issues that would cause plugin validation errors.
"""

import os
import re
import sys
from pathlib import Path

def sanitize_yaml_frontmatter(skill_md_path):
    """
    Fix known issues in SKILL.md frontmatter:
    1. Replace <x> with {x} in description field (XML tag issue)
    2. Validate YAML structure

    Returns True if file was modified, False otherwise.
    """
    with open(skill_md_path, 'r') as f:
        content = f.read()

    if not content.startswith('---'):
        raise ValueError(f"{skill_md_path}: No frontmatter found (must start with ---)")

    # Extract frontmatter block
    parts = content.split('---', 2)
    if len(parts) < 3:
        raise ValueError(f"{skill_md_path}: Malformed frontmatter (no closing ---)")

    frontmatter = parts[1]
    body = parts[2]

    # Fix XML tags: <x> → {x}
    original_fm = frontmatter
    frontmatter = re.sub(r'<([a-zA-Z0-9\-_]+)>', r'{\1}', frontmatter)

    modified = (frontmatter != original_fm)

    # Validate by trying to parse as YAML
    import yaml
    try:
        yaml.safe_load(frontmatter)
    except yaml.YAMLError as e:
        raise ValueError(f"{skill_md_path}: Invalid YAML in frontmatter: {e}")

    if modified:
        with open(skill_md_path, 'w') as f:
            f.write('---' + frontmatter + '---' + body)

    return modified

def main():
    """Scan and sanitize all skills in a skeleton directory."""

    # Find all SKILL.md files
    skills_dir = Path(__file__).parent.parent / 'skills'

    if not skills_dir.exists():
        print(f"Error: {skills_dir} not found")
        sys.exit(1)

    skill_files = list(skills_dir.glob('*/SKILL.md'))

    if not skill_files:
        print(f"Warning: No SKILL.md files found in {skills_dir}")
        return

    modified_files = []
    errors = []

    for skill_file in sorted(skill_files):
        try:
            if sanitize_yaml_frontmatter(skill_file):
                modified_files.append(skill_file)
                print(f"✓ Fixed: {skill_file.relative_to(skills_dir.parent)}")
        except ValueError as e:
            errors.append(str(e))
            print(f"✗ Error: {e}")

    if errors:
        print(f"\n{len(errors)} skill(s) have unrecoverable errors. Fix them manually.")
        sys.exit(1)

    if modified_files:
        print(f"\n✓ Sanitized {len(modified_files)} skill(s)")
    else:
        print(f"✓ All {len(skill_files)} skill(s) are already clean")

if __name__ == '__main__':
    main()
