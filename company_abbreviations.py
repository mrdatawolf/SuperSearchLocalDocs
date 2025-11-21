"""Module to handle company name and abbreviation mappings"""
import openpyxl
from pathlib import Path
from config import DOCUMENT_PATH

class CompanyAbbreviations:
    def __init__(self):
        self.abbrev_to_name = {}  # Maps abbreviation to full company name
        self.name_to_abbrev = {}  # Maps full company name to abbreviation
        self.load_companies()

    def load_companies(self):
        """Load company abbreviations from Excel file"""
        companies_file = Path(DOCUMENT_PATH) / "PBIData" / "Biztech" / "companies.xlsx"

        try:
            workbook = openpyxl.load_workbook(companies_file, read_only=True)
            sheet = workbook.active

            # Skip header row, read data rows
            for row in sheet.iter_rows(min_row=2, values_only=True):
                if len(row) >= 2 and row[0] and row[1]:
                    company_name = str(row[0]).strip()
                    abbreviation = str(row[1]).strip()

                    # Store both mappings
                    self.abbrev_to_name[abbreviation.lower()] = company_name
                    self.name_to_abbrev[company_name.lower()] = abbreviation

            workbook.close()
            print(f"Loaded {len(self.abbrev_to_name)} company abbreviations")

        except Exception as e:
            print(f"Warning: Could not load company abbreviations: {e}")
            # Continue without abbreviations rather than failing

    def expand_query_terms(self, query):
        """
        Expand query to include both abbreviations and full names

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
            if word_lower in self.abbrev_to_name:
                full_name = self.abbrev_to_name[word_lower]
                # Add both the abbreviation and the full name
                expanded_terms.append({
                    'original': word,
                    'expansion': full_name,
                    'type': 'abbreviation'
                })
            # Check if this word might be part of a company name
            elif word_lower in self.name_to_abbrev:
                abbrev = self.name_to_abbrev[word_lower]
                expanded_terms.append({
                    'original': word,
                    'expansion': abbrev,
                    'type': 'company_name'
                })

        return expanded_terms

    def get_search_alternatives(self, query):
        """
        Get alternative search terms for the query

        Returns a list of alternative queries to try, including:
        - The original query
        - Queries with abbreviations expanded
        - Queries with company names converted to abbreviations
        """
        query_lower = query.lower().strip()
        alternatives = [query]  # Always include original query

        # Check if the entire query is an abbreviation
        if query_lower in self.abbrev_to_name:
            alternatives.append(self.abbrev_to_name[query_lower])

        # Check if the entire query is a company name
        if query_lower in self.name_to_abbrev:
            alternatives.append(self.name_to_abbrev[query_lower])

        # Check for partial matches (words in the query)
        words = query.split()
        for word in words:
            word_lower = word.lower()

            if word_lower in self.abbrev_to_name:
                # Replace this word with the full company name
                full_name = self.abbrev_to_name[word_lower]
                expanded = query.replace(word, full_name, 1)
                if expanded not in alternatives:
                    alternatives.append(expanded)

            if word_lower in self.name_to_abbrev:
                # Replace with abbreviation
                abbrev = self.name_to_abbrev[word_lower]
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
