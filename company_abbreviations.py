"""Module to handle abbreviation and keyword mappings"""
import csv
from pathlib import Path
from config import DOCUMENT_PATH

class CompanyAbbreviations:
    def __init__(self):
        self.abbrev_to_keywords = {}  # Maps abbreviation to list of keywords
        self.keyword_to_abbrev = {}   # Maps each keyword to its abbreviation
        self.load_abbreviations()

    def load_abbreviations(self):
        """Load abbreviations and keywords from CSV file"""
        csv_file = Path(DOCUMENT_PATH) / "alternate_names.csv"

        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)

                # Skip header row if it exists
                first_row = next(reader, None)
                if first_row and first_row[0].lower() in ['abbreviation', 'abbrev', 'short']:
                    # This was a header row, continue to data
                    pass
                elif first_row:
                    # This was data, process it
                    self._process_row(first_row)

                # Process remaining rows
                for row in reader:
                    self._process_row(row)

            print(f"Loaded {len(self.abbrev_to_keywords)} abbreviations with keywords")

        except Exception as e:
            print(f"Warning: Could not load abbreviations: {e}")
            # Continue without abbreviations rather than failing

    def _process_row(self, row):
        """Process a single CSV row"""
        if len(row) < 2 or not row[0]:
            return  # Skip empty or invalid rows

        abbreviation = str(row[0]).strip().lower()
        keywords = []

        # Read up to 10 keywords from remaining columns
        for i in range(1, min(len(row), 11)):
            if row[i]:
                keyword = str(row[i]).strip().lower()
                if keyword:
                    keywords.append(keyword)
                    # Map keyword back to abbreviation
                    self.keyword_to_abbrev[keyword] = abbreviation

        # Store the abbreviation to keywords mapping
        if keywords:
            self.abbrev_to_keywords[abbreviation] = keywords

    def expand_query_terms(self, query):
        """
        Expand query to include both abbreviations and keywords

        Args:
            query: Original search query string

        Returns:
            List of expanded query terms
        """
        words = query.split()
        expanded_terms = []

        # Check each word in the query
        for word in words:
            word_lower = word.lower()

            # Check if this word is an abbreviation
            if word_lower in self.abbrev_to_keywords:
                keywords = self.abbrev_to_keywords[word_lower]
                # Add all keywords for this abbreviation
                for keyword in keywords:
                    expanded_terms.append({
                        'original': word,
                        'expansion': keyword,
                        'type': 'abbreviation'
                    })
            # Check if this word is a keyword
            elif word_lower in self.keyword_to_abbrev:
                abbrev = self.keyword_to_abbrev[word_lower]
                expanded_terms.append({
                    'original': word,
                    'expansion': abbrev,
                    'type': 'keyword'
                })

        return expanded_terms

    def get_search_alternatives(self, query):
        """
        Get alternative search terms for the query

        Returns a list of alternative queries to try, including:
        - The original query
        - Queries with abbreviations expanded to keywords
        - Queries with keywords converted to abbreviations
        """
        query_lower = query.lower().strip()
        alternatives = [query]  # Always include original query

        # Check if the entire query is an abbreviation
        if query_lower in self.abbrev_to_keywords:
            # Add each keyword as an alternative
            for keyword in self.abbrev_to_keywords[query_lower]:
                if keyword not in alternatives:
                    alternatives.append(keyword)

        # Check if the entire query is a keyword
        if query_lower in self.keyword_to_abbrev:
            abbrev = self.keyword_to_abbrev[query_lower]
            if abbrev not in alternatives:
                alternatives.append(abbrev)

        # Check for partial matches (words in the query)
        words = query.split()
        for word in words:
            word_lower = word.lower()

            # If this word is an abbreviation, expand to all keywords
            if word_lower in self.abbrev_to_keywords:
                for keyword in self.abbrev_to_keywords[word_lower]:
                    # Replace this word with each keyword
                    expanded = query.replace(word, keyword, 1)
                    if expanded not in alternatives:
                        alternatives.append(expanded)

            # If this word is a keyword, replace with abbreviation
            if word_lower in self.keyword_to_abbrev:
                abbrev = self.keyword_to_abbrev[word_lower]
                abbreviated = query.replace(word, abbrev, 1)
                if abbreviated not in alternatives:
                    alternatives.append(abbreviated)

        return alternatives


# Global instance to be used by the server
_company_abbrev_instance = None

def get_company_abbreviations():
    """Get or create the global CompanyAbbreviations instance"""
    global _company_abbrev_instance
    if _company_abbrev_instance is None:
        _company_abbrev_instance = CompanyAbbreviations()
    return _company_abbrev_instance
