"""
Semantic versioning utilities for prompt management.
Follows MAJOR.MINOR.PATCH convention.
"""
from typing import Tuple
import re


class VersionError(Exception):
    """Raised when version string is invalid."""
    pass


class Version:
    """Semantic version parser and comparison."""
    
    def __init__(self, version_string: str):
        """
        Initialize version from string like '1.2.3'.
        
        Args:
            version_string: Version in MAJOR.MINOR.PATCH format
            
        Raises:
            VersionError: If version format is invalid
        """
        self.original = version_string
        self.major, self.minor, self.patch = self._parse(version_string)
    
    @staticmethod
    def _parse(version_string: str) -> Tuple[int, int, int]:
        """Parse semantic version string."""
        match = re.match(r'^(\d+)\.(\d+)\.(\d+)$', version_string.strip())
        if not match:
            raise VersionError(
                f"Invalid version format: '{version_string}'. "
                "Expected MAJOR.MINOR.PATCH (e.g., '1.0.0')"
            )
        return int(match.group(1)), int(match.group(2)), int(match.group(3))
    
    def __str__(self) -> str:
        """Return version string."""
        return f"{self.major}.{self.minor}.{self.patch}"
    
    def __eq__(self, other: 'Version') -> bool:
        """Check equality."""
        if isinstance(other, str):
            other = Version(other)
        return (self.major, self.minor, self.patch) == (other.major, other.minor, other.patch)
    
    def __lt__(self, other: 'Version') -> bool:
        """Check less than."""
        if isinstance(other, str):
            other = Version(other)
        return (self.major, self.minor, self.patch) < (other.major, other.minor, other.patch)
    
    def __le__(self, other: 'Version') -> bool:
        """Check less than or equal."""
        return self == other or self < other
    
    def __gt__(self, other: 'Version') -> bool:
        """Check greater than."""
        if isinstance(other, str):
            other = Version(other)
        return (self.major, self.minor, self.patch) > (other.major, other.minor, other.patch)
    
    def __ge__(self, other: 'Version') -> bool:
        """Check greater than or equal."""
        return self == other or self > other
    
    def __repr__(self) -> str:
        return f"Version('{self}')"
    
    def bump_major(self) -> 'Version':
        """Increment major version (1.0.0 -> 2.0.0)."""
        return Version(f"{self.major + 1}.0.0")
    
    def bump_minor(self) -> 'Version':
        """Increment minor version (1.0.0 -> 1.1.0)."""
        return Version(f"{self.major}.{self.minor + 1}.0")
    
    def bump_patch(self) -> 'Version':
        """Increment patch version (1.0.0 -> 1.0.1)."""
        return Version(f"{self.major}.{self.minor}.{self.patch + 1}")


def parse_version(version_string: str) -> Version:
    """Parse and validate a semantic version string."""
    return Version(version_string)


def get_next_version(
    current_version: str,
    bump_type: str = "patch"
) -> str:
    """
    Get the next version based on bump type.
    
    Args:
        current_version: Current version string
        bump_type: 'major', 'minor', or 'patch'
        
    Returns:
        Next version string
        
    Raises:
        ValueError: If bump_type is invalid
    """
    version = Version(current_version)
    
    if bump_type == "major":
        return str(version.bump_major())
    elif bump_type == "minor":
        return str(version.bump_minor())
    elif bump_type == "patch":
        return str(version.bump_patch())
    else:
        raise ValueError(f"Invalid bump_type: {bump_type}. Must be 'major', 'minor', or 'patch'")


def validate_version_sequence(versions: list) -> bool:
    """
    Validate that versions are in ascending order.
    
    Args:
        versions: List of version strings
        
    Returns:
        True if versions are in ascending order
    """
    parsed = [Version(v) for v in versions]
    for i in range(len(parsed) - 1):
        if parsed[i] >= parsed[i + 1]:
            return False
    return True
