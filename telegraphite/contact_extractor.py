"""Contact Extractor module for TeleGraphite.

This module provides functionality to extract contact information such as emails and phone numbers from text.
"""

import re

class ContactExtractor:
    def __init__(self, patterns_file: str = "contact_patterns.txt"):
        self.patterns_file = patterns_file
        self.email_pattern = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
        self.phone_pattern = re.compile(r"\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}")

    def extract_contacts(self, text: str) -> dict:
        emails = self.email_pattern.findall(text)
        phones = self.phone_pattern.findall(text)
        return {"emails": emails, "phones": phones, "links": []}