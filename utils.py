import json
import datetime
import xml.etree.ElementTree as ET
import re

class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime.date):
            return o.isoformat()

        return super().default(o)

def get_domain_for_url(url: str) -> str:
    """Gets a domain name from a URL."""
    website_domain = url.split("//")[1].split("/")[0]
    return website_domain

def truncate(encoding, prompt, max_size) -> str:
    input_ids = encoding.encode(prompt, disallowed_special="all")
    truncated_ids = input_ids[:max_size]
    return encoding.decode(truncated_ids)

def count_tokens(encoding, text) -> int:
    return len(encoding.encode(text, disallowed_special="all"))


def parse_response_for_xml(response: str, tags: list[str]) -> dict[str, str]:
    """Parses a response from the API for the XML."""
    # Parse the XML string into an ElementTree object
    xml_string = f"<root>{response}</root>"
    root = ET.fromstring(xml_string)

    # Initialize an empty dictionary to store the results
    result = {}

    # Iterate over the provided tags
    for tag in tags:
        # Find the first element with this tag
        element = root.find(tag)

        # If an element with this tag is found, store its text in the result
        if element is not None:
            result[tag] = element.text
        else:
            result[tag] = None

    return result

def extract_text_within_parentheses(s: str) -> list[str]:
    # The pattern '\(.*?\)' matches anything within parentheses (non-greedy)
    # The '(?<=\').*?(?=\')' pattern matches anything within single quotes (non-greedy)
    # The '(?<=\").*?(?=\")' pattern matches anything within double quotes (non-greedy)
    pattern_single_quotes = r"(?<=\').*?(?=\')"
    pattern_double_quotes = r"(?<=\").*?(?=\")"

    # Find all occurrences of the patterns
    matches_single_quotes = re.findall(pattern_single_quotes, s)
    matches_double_quotes = re.findall(pattern_double_quotes, s)

    # Return the matches
    return matches_single_quotes + matches_double_quotes