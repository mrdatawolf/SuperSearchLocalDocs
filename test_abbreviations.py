"""
Test script for the abbreviation expansion system
Demonstrates how abbreviations are expanded to keywords
"""

from pathlib import Path
import sys

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import the abbreviations module
from company_abbreviations import CompanyAbbreviations

def test_abbreviations():
    """Test the abbreviation expansion functionality"""

    print("=" * 80)
    print("Testing Abbreviation Expansion System")
    print("=" * 80)
    print()

    # Create instance
    abbrev = CompanyAbbreviations()

    # Show loaded data
    print(f"Loaded {len(abbrev.abbrev_to_keywords)} abbreviations")
    print()

    if len(abbrev.abbrev_to_keywords) > 0:
        print("Sample abbreviations:")
        for i, (abbr, keywords) in enumerate(list(abbrev.abbrev_to_keywords.items())[:5]):
            print(f"  {abbr} -> {', '.join(keywords)}")
        print()

    # Test search alternatives
    test_queries = [
        "foo",           # Should expand to bar, alice, bob, etc.
        "API",           # Should expand to interface, endpoint, etc.
        "database",      # Should map back to DB
        "foo test",      # Multi-word with abbreviation
        "unknown",       # No expansion
    ]

    print("Testing search expansion:")
    print("-" * 80)

    for query in test_queries:
        alternatives = abbrev.get_search_alternatives(query)
        print(f"\nQuery: '{query}'")
        print(f"Alternatives ({len(alternatives)}):")
        for alt in alternatives:
            if alt != query:
                print(f"  - {alt}")
        if len(alternatives) == 1:
            print("  (no expansion)")

    print()
    print("=" * 80)
    print("Test Complete!")
    print("=" * 80)

if __name__ == '__main__':
    test_abbreviations()
