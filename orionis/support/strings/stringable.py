from __future__ import annotations
import base64
import hashlib
import html
import json
import os
import re
import unicodedata
import urllib.parse
import uuid
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Union
from collections.abc import Iterable

class Stringable(str):

    def after(self, search: str) -> Stringable:
        """
        Return substring after first occurrence of a value.

        Searches for the first occurrence of the specified substring and returns
        everything that comes after it. If the substring is not found, returns
        the original string unchanged.

        Parameters
        ----------
        search : str
            Substring to search for within the current string.

        Returns
        -------
        Stringable
            New Stringable instance containing the substring after the first
            occurrence of the search string, or the original string if not found.
        """
        # Find the index of the first occurrence of the search string
        idx = self.find(search)
        # Return substring after the search string if found, else original string
        return Stringable(self[idx + len(search):]) if idx != -1 else Stringable(self)

    def afterLast(self, search: str) -> Stringable:
        """
        Return substring after the last occurrence of a value.

        Searches for the last occurrence of the specified substring and returns
        everything that comes after it. If the substring is not found, returns
        the original string unchanged.

        Parameters
        ----------
        search : str
            Substring to search for within the current string.

        Returns
        -------
        Stringable
            New Stringable instance containing the substring after the last
            occurrence of the search string, or the original string if not found.
        """
        # Find the index of the last occurrence of the search string
        idx = self.rfind(search)
        # Return substring after the search string if found, else original string
        return Stringable(self[idx + len(search):]) if idx != -1 else Stringable(self)

    def append(self, *values: str) -> Stringable:
        """
        Append one or more values to the end of the string.

        Parameters
        ----------
        values : str
            One or more string values to append.

        Returns
        -------
        Stringable
            A new Stringable instance with all provided values appended.
        """
        # Concatenate all provided values to the current string
        return Stringable(self + "".join(values))

    def newLine(self, count: int = 1) -> Stringable:
        """
        Append newline characters to the string.

        Appends the specified number of newline characters to the end of the string.

        Parameters
        ----------
        count : int, optional
            Number of newline characters to append. Default is 1.

        Returns
        -------
        Stringable
            A new Stringable instance with the specified number of newline
            characters appended.
        """
        # Append the specified number of newline characters to the string
        return Stringable(str(self) + "\n" * count)

    def before(self, search: str) -> "Stringable":
        """
        Return the substring before the first occurrence of a value.

        Parameters
        ----------
        search : str
            Substring to search for within the current string.

        Returns
        -------
        Stringable
            New Stringable instance containing the substring before the first
            occurrence of the search string, or the original string if not found.
        """
        # Find the index of the first occurrence of the search string
        idx = self.find(search)
        # Return substring before the search string if found, else original string
        return Stringable(self[:idx]) if idx != -1 else Stringable(self)

    def beforeLast(self, search: str) -> Stringable:
        """
        Return substring before the last occurrence of a value.

        Searches for the last occurrence of the specified substring and returns
        everything before it. If the substring is not found, returns the original
        string unchanged.

        Parameters
        ----------
        search : str
            Substring to search for within the current string.

        Returns
        -------
        Stringable
            New Stringable instance containing the substring before the last
            occurrence of the search string, or the original string if not found.
        """
        # Find the index of the last occurrence of the search string
        idx = self.rfind(search)
        # Return substring before the search string if found, else original string
        return Stringable(self[:idx]) if idx != -1 else Stringable(self)

    def contains(
        self,
        needles: str | Iterable[str],
        ignore_case: bool = False
    ) -> bool:
        """
        Check if the string contains any of the given values.

        Parameters
        ----------
        needles : str or Iterable[str]
            Value or values to search for within the string.
        ignore_case : bool, default False
            If True, perform case-insensitive search.

        Returns
        -------
        bool
            True if the string contains any of the needle values, False otherwise.
        """
        # Normalize needles to a list for consistent processing
        if isinstance(needles, str):
            needles = [needles]
        # Convert to lowercase for case-insensitive comparison if requested
        s = str(self).lower() if ignore_case else str(self)
        # Check if any needle is found in the string
        return any(
            (needle.lower() if ignore_case else needle) in s for needle in needles
        )

    def endsWith(self, needles: str | Iterable[str]) -> bool:
        """
        Check if the string ends with any of the given substrings.

        Parameters
        ----------
        needles : str or Iterable[str]
            Substring or substrings to check at the end of the string.

        Returns
        -------
        bool
            True if the string ends with any of the needle values, False otherwise.
        """
        # Convert needles to a list for consistent processing
        if isinstance(needles, str):
            needles = [needles]
        # Return True if the string ends with any of the provided needles
        return any(str(self).endswith(needle) for needle in needles)

    def exactly(self, value: Any) -> bool:
        """
        Compare the string for exact equality with a given value.

        Parameters
        ----------
        value : Any
            The value to compare against the current string.

        Returns
        -------
        bool
            True if the string exactly matches the given value, False otherwise.
        """
        # Compare string representations for strict equality
        return str(self) == str(value)

    def isEmpty(self) -> bool:
        """
        Return True if the string is empty.

        Returns
        -------
        bool
            True if the string has zero length, otherwise False.
        """
        # Check if the string has zero length
        return len(self) == 0

    def isNotEmpty(self) -> bool:
        """
        Determine if the string is not empty.

        Returns
        -------
        bool
            True if the string contains one or more characters, otherwise False.
        """
        # Return True if the string has one or more characters
        return not self.isEmpty()

    def lower(self) -> "Stringable":
        """
        Convert the string to lowercase.

        Parameters
        ----------
        None

        Returns
        -------
        Stringable
            A new Stringable instance with all characters in lowercase.
        """
        # Use the built-in lower method to convert all characters to lowercase
        return Stringable(super().lower())

    def upper(self) -> "Stringable":
        """
        Convert to uppercase.

        Returns
        -------
        Stringable
            A new Stringable instance with all characters in uppercase.
        """
        # Convert all characters to uppercase using the built-in method
        return Stringable(super().upper())

    def reverse(self) -> "Stringable":
        """
        Reverse the string.

        Returns
        -------
        Stringable
            A new Stringable instance with characters in reverse order.
        """
        # Return the reversed string using slicing
        return Stringable(self[::-1])

    def repeat(self, times: int) -> Stringable:
        """
        Repeat the string a specified number of times.

        Parameters
        ----------
        times : int
            Number of times to repeat the string.

        Returns
        -------
        Stringable
            A new Stringable instance with the string repeated the specified
            number of times.
        """
        # Repeat the string using multiplication
        return Stringable(self * times)

    def replace(
        self,
        search: str | Iterable[str],
        replace: str | Iterable[str],
        case_sensitive: bool = True,
    ) -> "Stringable":
        """
        Replace occurrences of specified substrings with replacements.

        Parameters
        ----------
        search : str or Iterable[str]
            Substring(s) to search for in the string.
        replace : str or Iterable[str]
            Replacement string(s) for each search substring.
        case_sensitive : bool, optional
            If True, perform case-sensitive replacement. Default is True.

        Returns
        -------
        Stringable
            New Stringable instance with the specified replacements applied.
        """
        # Convert search and replace to lists for consistent processing
        s = self
        if isinstance(search, str):
            search = [search]
        if isinstance(replace, str):
            replace = [replace] * len(search)

        # Iterate through each search-replace pair and apply replacement
        for src, rep in zip(search, replace):
            if case_sensitive:
                # Case-sensitive replacement using str.replace
                s = str(s).replace(src, rep)
            else:
                # Case-insensitive replacement using re.sub with IGNORECASE
                s = re.sub(re.escape(src), rep, str(s), flags=re.IGNORECASE)

        return Stringable(s)

    def stripTags(self, allowed_tags: str | None = None) -> Stringable:
        """
        Remove HTML and PHP tags from the string.

        Parameters
        ----------
        allowed_tags : str or None, optional
            Tags that should not be stripped. Default is None.

        Returns
        -------
        Stringable
            A new Stringable instance with tags removed.
        """
        # If allowed_tags is specified, unescape HTML entities only.
        if allowed_tags:
            return Stringable(html.unescape(str(self)))
        # Remove all tags using a regular expression.
        return Stringable(re.sub(r"<[^>]*>", "", str(self)))

    def toBase64(self) -> "Stringable":
        """
        Encode the string as Base64.

        Returns
        -------
        Stringable
            A new Stringable instance containing the Base64 encoded content.
        """
        # Encode the string to Base64 and decode to string
        return Stringable(base64.b64encode(str(self).encode()).decode())

    def fromBase64(self, strict: bool = False) -> "Stringable":
        """
        Decode the string from Base64.

        Parameters
        ----------
        strict : bool, optional
            If True, raise an exception on decode errors. Default is False.

        Returns
        -------
        Stringable
            A new Stringable with Base64-decoded content, or an empty string if
            decoding fails and strict is False.
        """
        # Attempt to decode the string from Base64
        try:
            return Stringable(base64.b64decode(str(self).encode()).decode())
        except Exception as exc:
            if strict:
                error_msg = str(exc)
                raise Exception(error_msg)
            # Return empty string if decoding fails and strict is False
            return Stringable("")

    def md5(self) -> str:
        """
        Generate an MD5 hash of the string.

        Returns
        -------
        str
            The MD5 hash of the string as a hexadecimal string.
        """
        # Compute the MD5 hash using hashlib and return as hex string
        return hashlib.md5(str(self).encode()).hexdigest()

    def sha1(self) -> str:
        """
        Generate a SHA1 hash of the string.

        Returns
        -------
        str
            The SHA1 hash of the string as a hexadecimal string.
        """
        # Compute the SHA1 hash using hashlib and return as hex string
        return hashlib.sha1(str(self).encode()).hexdigest()

    def sha256(self) -> str:
        """
        Generate a SHA256 hash of the string.

        Returns
        -------
        str
            The SHA256 hash of the string as a hexadecimal string.
        """
        # Compute the SHA256 hash using hashlib and return as hex string
        return hashlib.sha256(str(self).encode()).hexdigest()

    def length(self) -> int:
        """
        Return the number of characters in the string.

        Returns
        -------
        int
            The number of characters in the string.
        """
        # Return the length of the string
        return len(self)

    def value(self) -> str:
        """
        Return the string value.

        Returns
        -------
        str
            The string representation of the current instance.
        """
        # Return the string representation of this object
        return str(self)

    def toString(self) -> str:
        """
        Return the string representation of the instance.

        Returns
        -------
        str
            The string representation of the current instance.
        """
        # Return the string representation of this object
        return str(self)

    def toInteger(self, base: int = 10) -> int:
        """
        Convert to an integer using the specified base.

        Parameters
        ----------
        base : int, optional
            The base for conversion. Default is 10.

        Returns
        -------
        int
            The integer representation of the string.
        """
        # Convert the string to integer using the specified base
        return int(self, base)

    def toFloat(self) -> float:
        """
        Convert the string to a float.

        Returns
        -------
        float
            The float representation of the string.
        """
        # Convert the string to float using built-in float()
        return float(self)

    def toBoolean(self) -> bool:
        """
        Convert the string to a boolean value.

        The string is considered True if it matches common truthy values such as
        "1", "true", "on", or "yes" (case-insensitive).

        Returns
        -------
        bool
            True if the string represents a truthy value, otherwise False.
        """
        # Check for common truthy values after stripping and lowering the string
        return str(self).strip().lower() in ("1", "true", "on", "yes")

    def __getitem__(self, key: int | slice) -> "Stringable":
        """
        Return a substring or character by index or slice.

        Parameters
        ----------
        key : int or slice
            Index or slice to retrieve.

        Returns
        -------
        Stringable
            New Stringable instance for the selected item(s).
        """
        # Return a Stringable for the selected item(s)
        return Stringable(super().__getitem__(key))

    def __str__(self) -> str:
        """
        Return the string representation.

        Returns
        -------
        str
            The string representation of the object.
        """
        # Return the string representation using the parent class
        return super().__str__()

    def isAlnum(self) -> bool:
        """
        Check if all characters are alphanumeric.

        Returns
        -------
        bool
            True if all characters are alphanumeric, False otherwise.
        """
        # Use str.isalnum() to check for alphanumeric characters
        return str(self).isalnum()

    def isAlpha(self) -> bool:
        """
        Return True if all characters in the string are alphabetic.

        Returns
        -------
        bool
            True if all characters are alphabetic, otherwise False.
        """
        # Use str.isalpha() to check for alphabetic characters
        return str(self).isalpha()

    def isDecimal(self) -> bool:
        """
        Return True if all characters in the string are decimal characters.

        Returns
        -------
        bool
            True if all characters are decimal, otherwise False.
        """
        # Use str.isdecimal() to check for decimal characters
        return str(self).isdecimal()

    def isDigit(self) -> bool:
        """
        Check if all characters are digits.

        Returns
        -------
        bool
            True if all characters in the string are digits, otherwise False.
        """
        # Use str.isdigit() to check for digit characters
        return str(self).isdigit()

    def isIdentifier(self) -> bool:
        """
        Determine if the string is a valid Python identifier.

        Returns
        -------
        bool
            True if the string is a valid identifier, otherwise False.
        """
        # Use str.isidentifier() to check for valid Python identifier
        return str(self).isidentifier()

    def isLower(self) -> bool:
        """
        Return True if all cased characters in the string are lowercase.

        Returns
        -------
        bool
            True if all cased characters are lowercase, otherwise False.
        """
        # Use str.islower() to check for lowercase characters
        return str(self).islower()

    def isNumeric(self) -> bool:
        """
        Return True if all characters in the string are numeric.

        Returns
        -------
        bool
            True if all characters are numeric, otherwise False.
        """
        # Use str.isnumeric() to check for numeric characters
        return str(self).isnumeric()

    def isPrintable(self) -> bool:
        """
        Return True if all characters in the string are printable.

        Returns
        -------
        bool
            True if all characters are printable, otherwise False.
        """
        # Use str.isprintable() to check for printable characters
        return str(self).isprintable()

    def isSpace(self) -> bool:
        """
        Check if the string contains only whitespace characters.

        Returns
        -------
        bool
            True if the string contains only whitespace characters, False otherwise.
        """
        # Use str.isspace() to check for whitespace-only string
        return str(self).isspace()

    def isTitle(self) -> bool:
        """
        Return True if the string is titlecased.

        Returns
        -------
        bool
            True if the string is titlecased, otherwise False.
        """
        # Use str.istitle() to check for titlecase
        return str(self).istitle()

    def isUpper(self) -> bool:
        """
        Return True if all cased characters in the string are uppercase.

        Returns
        -------
        bool
            True if all cased characters are uppercase, otherwise False.
        """
        # Use str.isupper() to check for uppercase characters
        return str(self).isupper()

    def lStrip(self, chars: str | None = None) -> Stringable:
        """
        Remove leading characters from the string.

        Parameters
        ----------
        chars : str or None, optional
            Characters to remove from the beginning. If None, removes whitespace.

        Returns
        -------
        Stringable
            A new Stringable instance with leading characters removed.
        """
        # Remove leading characters using Python's built-in lstrip
        return Stringable(str(self).lstrip(chars))

    def rStrip(self, chars: str | None = None) -> Stringable:
        """
        Remove trailing characters from the string.

        Removes trailing characters from the right side of the string. If no characters
        are specified, whitespace characters are removed by default.

        Parameters
        ----------
        chars : str or None, optional
            Characters to remove from the end. If None, removes whitespace.

        Returns
        -------
        Stringable
            A new Stringable instance with trailing characters removed.
        """
        # Remove trailing characters using Python's built-in rstrip
        return Stringable(str(self).rstrip(chars))

    def swapCase(self) -> "Stringable":
        """
        Swap the case of each character in the string.

        Converts uppercase characters to lowercase and lowercase characters to
        uppercase, leaving other characters unchanged.

        Returns
        -------
        Stringable
            A new Stringable instance with all character cases swapped.
        """
        # Use built-in swapcase to invert the case of all characters
        return Stringable(str(self).swapcase())

    def zFill(self, width: int) -> Stringable:
        """
        Pad the string with leading zeros to the specified width.

        Parameters
        ----------
        width : int
            Total width of the resulting string.

        Returns
        -------
        Stringable
            Stringable instance padded with leading zeros to the specified width.
        """
        # Pad with zeros, preserving sign if present
        return Stringable(str(self).zfill(width))

    def ascii(self) -> "Stringable":
        """
        Transliterate a UTF-8 string to ASCII.

        Uses Unicode normalization to remove accents and non-ASCII characters.

        Returns
        -------
        Stringable
            A new Stringable instance containing only ASCII characters.
        """
        # Normalize and filter out non-ASCII characters
        normalized = unicodedata.normalize("NFKD", self)
        ascii_str = "".join(c for c in normalized if ord(c) < 128)
        return Stringable(ascii_str)

    def camel(self) -> "Stringable":
        """
        Convert the string to camel case.

        Returns
        -------
        Stringable
            A new Stringable instance in camelCase.
        """
        # Split the string by common separators and normalize to words
        words = re.sub(r"[_\-\s]+", " ", str(self)).split()
        if not words:
            return Stringable("")
        # Lowercase the first word, capitalize the rest, and join
        camel_str = words[0].lower() + "".join(word.capitalize() for word in words[1:])
        return Stringable(camel_str)

    def kebab(self) -> Stringable:
        """
        Convert to kebab case.

        Returns
        -------
        Stringable
            A new Stringable instance in kebab-case.
        """
        # Insert dash between lowercase/number and uppercase letters
        s = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", str(self))
        # Replace spaces and underscores with dash, collapse multiple dashes
        s = re.sub(r"[_\s]+", "-", s)
        s = re.sub(r"-+", "-", s)
        return Stringable(s.lower().strip("-"))

    def snake(self, delimiter: str = "_") -> "Stringable":
        """
        Convert to snake case.

        Parameters
        ----------
        delimiter : str, optional
            Delimiter to use for separation, by default "_".

        Returns
        -------
        Stringable
            New Stringable instance in snake_case.
        """
        # Insert delimiter between lowercase/number and uppercase letters
        s = re.sub(r"([a-z0-9])([A-Z])", rf"\1{delimiter}\2", str(self))
        # Replace spaces and dashes with delimiter
        s = re.sub(r"[\s\-]+", delimiter, s)
        # Collapse multiple delimiters into one
        s = re.sub(rf"{re.escape(delimiter)}+", delimiter, s)
        return Stringable(s.lower().strip(delimiter))

    def studly(self) -> Stringable:
        """
        Convert the string to StudlyCase (PascalCase).

        Returns
        -------
        Stringable
            A new Stringable instance in StudlyCase.
        """
        # Replace common separators with spaces, split into words, capitalize each
        words = re.sub(r"[_\-\s]+", " ", str(self)).split()
        studly_str = "".join(word.capitalize() for word in words)
        return Stringable(studly_str)

    def pascal(self) -> Stringable:
        """
        Convert to PascalCase.

        Returns
        -------
        Stringable
            A new Stringable instance in PascalCase.
        """
        # Use studly() to convert to PascalCase (StudlyCase).
        return self.studly()

    def slug(
        self,
        separator: str = "-",
        dictionary: dict[str, str] | None = None,
    ) -> "Stringable":
        """
        Generate a URL-friendly slug from the string.

        Parameters
        ----------
        separator : str, optional
            Separator to use in the slug. Default is "-".
        dictionary : dict[str, str] or None, optional
            Dictionary for character replacements. Default is {"@": "at"}.

        Returns
        -------
        Stringable
            A new Stringable instance containing the URL-friendly slug.
        """
        # Set default dictionary if not provided
        if dictionary is None:
            dictionary = {"@": "at"}

        s = str(self)

        # Replace characters using the dictionary
        for key, value in dictionary.items():
            s = s.replace(key, value)

        # Convert to ASCII
        s = self.__class__(s).ascii().value()

        # Remove non-alphanumeric characters except spaces and separators
        s = re.sub(r"[^\w\s-]", "", s)

        # Replace spaces and underscores with the separator
        s = re.sub(r"[\s_]+", separator, s)

        # Collapse multiple separators into one
        s = re.sub(rf"{re.escape(separator)}+", separator, s)

        # Return the slug in lowercase, stripped of leading/trailing separators
        return Stringable(s.lower().strip(separator))

    def title(self) -> Stringable:
        """
        Convert the string to title case.

        Returns
        -------
        Stringable
            A new Stringable instance in title case.
        """
        # Use the built-in title method to capitalize each word
        return Stringable(str(self).title())

    def headline(self) -> "Stringable":
        """
        Convert the string to headline case.

        Splits the string into words and capitalizes the first letter of each word.

        Returns
        -------
        Stringable
            A new Stringable instance with each word capitalized.
        """
        # Split the string into words using word boundaries
        words = re.findall(r"\b\w+\b", str(self))
        # Capitalize the first letter of each word and join them with spaces
        headline_str = " ".join(word.capitalize() for word in words)
        return Stringable(headline_str)

    def apa(self) -> "Stringable":
        """
        Convert to APA-style title case.

        Parameters
        ----------
        None

        Returns
        -------
        Stringable
            New Stringable in APA title case.
        """
        # Set of words not capitalized in APA style except at start or end
        lowercase_words = {
            "a", "an", "and", "as", "at", "but", "by", "for", "if", "in",
            "nor", "of", "on", "or", "so", "the", "to", "up", "yet",
        }
        words = str(self).split()
        apa_words = []
        for i, word in enumerate(words):
            # Capitalize first, last, words >= 4 chars, or not in lowercase_words
            if (
                i == 0
                or i == len(words) - 1
                or len(word) >= 4
                or word.lower() not in lowercase_words
            ):
                apa_words.append(word.capitalize())
            else:
                apa_words.append(word.lower())
        return Stringable(" ".join(apa_words))

    def ucfirst(self) -> "Stringable":
        """
        Capitalize the first character of the string.

        Returns
        -------
        Stringable
            A new Stringable instance with the first character in uppercase.
        """
        # Return self if string is empty, else capitalize first character
        if not self:
            return Stringable(self)
        return Stringable(self[0].upper() + self[1:])

    def lcfirst(self) -> "Stringable":
        """
        Convert the first character of the string to lowercase.

        Returns
        -------
        Stringable
            A new Stringable instance with the first character in lowercase.
        """
        # Return self if string is empty, else lowercase first character
        if not self:
            return Stringable(self)
        return Stringable(self[0].lower() + self[1:])

    def isAscii(self) -> bool:
        """
        Check if the string contains only 7-bit ASCII characters.

        Returns
        -------
        bool
            True if the string is ASCII, otherwise False.
        """
        # Attempt to encode the string as ASCII; fail if non-ASCII chars exist
        try:
            self.encode("ascii")
            return True
        except UnicodeEncodeError:
            return False

    def isJson(self) -> bool:
        """
        Check if the string is valid JSON.

        Returns
        -------
        bool
            True if the string is valid JSON, otherwise False.
        """
        try:
            # Try to parse the string as JSON
            json.loads(str(self))
            return True
        except (json.JSONDecodeError, TypeError):
            return False

    def isUrl(self, protocols: list[str] | None = None) -> bool:
        """
        Check if the string is a valid URL.

        Parameters
        ----------
        protocols : list of str or None, optional
            List of valid protocols. Defaults to ['http', 'https'].

        Returns
        -------
        bool
            True if the string is a valid URL with an allowed protocol,
            otherwise False.
        """
        if protocols is None:
            protocols = ["http", "https"]

        try:
            # Parse the string as a URL and check scheme and netloc
            result = urllib.parse.urlparse(str(self))
            return (
                all([result.scheme, result.netloc]) and
                result.scheme in protocols
            )
        except Exception:
            return False

    def isUuid(self, version: int | str | None = None) -> bool:
        """
        Determine if the string is a valid UUID.

        Parameters
        ----------
        version : int | str | None, optional
            UUID version to validate (1-8), or "max" for any version up to 8.
            If None, any valid UUID version is accepted.

        Returns
        -------
        bool
            True if the string is a valid UUID (and version, if specified),
            otherwise False.
        """
        try:
            # Attempt to create a UUID object from the string
            uuid_obj = uuid.UUID(str(self))
            if version is not None:
                if version == "max":
                    # Accept any version up to 8
                    return uuid_obj.version <= 8
                return uuid_obj.version == int(version)
            return True
        except (ValueError, TypeError):
            # Return False if the string is not a valid UUID
            return False

    def isUlid(self) -> bool:
        """
        Determine if the string is a valid ULID.

        Returns
        -------
        bool
            True if the string is a valid ULID, otherwise False.
        """
        # ULID must be 26 characters, Crockford's Base32 (no I, L, O, U)
        ulid_pattern = r"^[0123456789ABCDEFGHJKMNPQRSTVWXYZ]{26}$"
        return bool(re.match(ulid_pattern, str(self).upper()))

    def chopStart(self, needle: str | list[str]) -> Stringable:
        """
        Remove the given string if it exists at the start of the current string.

        Parameters
        ----------
        needle : str or list of str
            String(s) to remove from the start.

        Returns
        -------
        Stringable
            New Stringable with the needle removed from the start if present.
        """
        s = str(self)
        # Normalize needle to a list for consistent processing
        if isinstance(needle, str):
            needle = [needle]
        # Remove the first matching needle from the start
        for n in needle:
            if s.startswith(n):
                s = s[len(n):]
                break
        return Stringable(s)

    def chopEnd(self, needle: str | list[str]) -> Stringable:
        """
        Remove the given string(s) from the end if present.

        Parameters
        ----------
        needle : str or list of str
            String(s) to remove from the end.

        Returns
        -------
        Stringable
            New Stringable with the needle removed from the end if present.
        """
        s = str(self)
        # Normalize needle to a list for consistent processing
        if isinstance(needle, str):
            needle = [needle]
        # Remove the first matching needle from the end
        for n in needle:
            if s.endswith(n):
                s = s[:-len(n)]
                break
        return Stringable(s)

    def deduplicate(self, character: str = " ") -> Stringable:
        """
        Replace consecutive occurrences of a character with a single instance.

        Parameters
        ----------
        character : str, optional
            Character to deduplicate. Default is a space.

        Returns
        -------
        Stringable
            Stringable with consecutive characters replaced by a single instance.
        """
        # Build regex pattern for consecutive occurrences of the character
        pattern = re.escape(character) + "+"
        # Replace with a single instance of the character
        return Stringable(re.sub(pattern, character, str(self)))

    def mask(
        self,
        character: str,
        index: int,
        length: int | None = None
    ) -> Stringable:
        """
        Mask a portion of the string with a repeated character.

        Parameters
        ----------
        character : str
            Character to use for masking.
        index : int
            Starting index for masking.
        length : int | None, optional
            Number of characters to mask. If None, mask to end of string.

        Returns
        -------
        Stringable
            New Stringable with the specified portion masked.
        """
        s = str(self)
        # Adjust negative index to count from end of string
        if index < 0:
            index = max(0, len(s) + index)
        # Determine length to mask
        if length is None:
            length = len(s) - index
        elif length < 0:
            length = max(0, len(s) + length - index)
        end_index = min(len(s), index + length)
        mask_str = character * (end_index - index)
        # Return string with masked portion
        return Stringable(s[:index] + mask_str + s[end_index:])

    def limit(
        self,
        limit: int = 100,
        end: str = "...",
        preserve_words: bool = False,
    ) -> Stringable:
        """
        Limit the string to a maximum number of characters.

        Parameters
        ----------
        limit : int, default=100
            Maximum number of characters allowed.
        end : str, default="..."
            String to append if truncation occurs.
        preserve_words : bool, default=False
            If True, do not cut off words in the middle.

        Returns
        -------
        Stringable
            New Stringable instance with limited length.
        """
        s = str(self)
        # Return original string if within limit
        if len(s) <= limit:
            return Stringable(s)
        if preserve_words:
            # Find last space before limit to avoid breaking words
            truncated = s[:limit]
            last_space = truncated.rfind(" ")
            if last_space > 0:
                truncated = truncated[:last_space]
        else:
            truncated = s[:limit]
        return Stringable(truncated + end)

    def padBoth(self, length: int, pad: str = " ") -> "Stringable":
        """
        Pad both sides of the string to a specified total length.

        Parameters
        ----------
        length : int
            The total desired length of the resulting string.
        pad : str, optional
            The string to use for padding, by default a single space.

        Returns
        -------
        Stringable
            A new Stringable instance with padding added to both sides.
        """
        s = str(self)
        # Return original string if already at or above desired length
        if len(s) >= length:
            return Stringable(s)
        # Calculate padding needed on each side
        total_padding = length - len(s)
        left_padding = total_padding // 2
        right_padding = total_padding - left_padding
        # Build left and right padding strings
        left_pad = (pad * ((left_padding // len(pad)) + 1))[:left_padding]
        right_pad = (pad * ((right_padding // len(pad)) + 1))[:right_padding]
        return Stringable(left_pad + s + right_pad)

    def padLeft(self, length: int, pad: str = " ") -> Stringable:
        """
        Pad the left side of the string to a specified total length.

        Parameters
        ----------
        length : int
            Total desired length of the resulting string.
        pad : str, optional
            String to use for padding, by default a single space.

        Returns
        -------
        Stringable
            New Stringable instance with left padding added.
        """
        s = str(self)
        # Return original string if already at or above desired length
        if len(s) >= length:
            return Stringable(s)
        # Calculate and apply left padding
        padding_needed = length - len(s)
        left_pad = (pad * ((padding_needed // len(pad)) + 1))[:padding_needed]
        return Stringable(left_pad + s)

    def padRight(self, length: int, pad: str = " ") -> Stringable:
        """
        Pad the right side of the string to a specified total length.

        Parameters
        ----------
        length : int
            The total desired length of the resulting string.
        pad : str, optional
            The string to use for padding, by default a single space.

        Returns
        -------
        Stringable
            A new Stringable instance with right padding added.
        """
        s = str(self)
        # Return original string if already at or above desired length
        if len(s) >= length:
            return Stringable(s)
        # Calculate and apply right padding
        padding_needed = length - len(s)
        right_pad = (pad * ((padding_needed // len(pad)) + 1))[:padding_needed]
        return Stringable(s + right_pad)

    def trim(self, characters: str | None = None) -> Stringable:
        """
        Trim the string of the specified characters.

        Parameters
        ----------
        characters : str or None, optional
            Characters to trim from both ends. If None, trims whitespace.

        Returns
        -------
        Stringable
            A new Stringable instance with specified characters trimmed.
        """
        # Strip specified characters (or whitespace) from both ends of the string
        return Stringable(str(self).strip(characters))

    def ltrim(self, characters: str | None = None) -> Stringable:
        """
        Remove leading characters from the string.

        Parameters
        ----------
        characters : str or None, optional
            Characters to remove from the start. If None, whitespace is removed.

        Returns
        -------
        Stringable
            A new Stringable instance with leading characters removed.
        """
        # Remove leading characters using lstrip
        return Stringable(str(self).lstrip(characters))

    def rtrim(self, characters: str | None = None) -> Stringable:
        """
        Right trim the string of the given characters.

        Parameters
        ----------
        characters : str or None, optional
            Characters to trim from the end. If None, trims whitespace.

        Returns
        -------
        Stringable
            A new Stringable instance with trailing characters removed.
        """
        # Remove trailing characters using Python's built-in rstrip
        return Stringable(str(self).rstrip(characters))

    def charAt(self, index: int) -> str | bool:
        """
        Return the character at the specified index.

        Parameters
        ----------
        index : int
            Index of the character to retrieve.

        Returns
        -------
        str or bool
            Character at the given index, or False if index is out of bounds.
        """
        try:
            # Attempt to access the character at the specified index
            return str(self)[index]
        except IndexError:
            return False

    def position(
        self, needle: str, offset: int = 0, encoding: str | None = None
    ) -> int | bool:
        """
        Find the position of the first occurrence of a substring.

        Parameters
        ----------
        needle : str
            Substring to search for.
        offset : int, optional
            Starting index for the search, by default 0.
        encoding : str | None, optional
            String encoding for compatibility, by default None.

        Returns
        -------
        int | bool
            Index of the first occurrence of the substring, or False if not found.
        """
        # Use str.find to locate the substring, return False if not found
        try:
            pos = str(self).find(needle, offset)
            return pos if pos != -1 else False
        except Exception:
            return False

    def match(self, pattern: str) -> Stringable:
        """
        Return the first substring matching the given regular expression pattern.

        Parameters
        ----------
        pattern : str
            Regular expression pattern to search for.

        Returns
        -------
        Stringable
            A new Stringable containing the first match, or an empty Stringable
            if no match is found.
        """
        # Search for the first match of the pattern in the string
        match = re.search(pattern, str(self))
        return Stringable(match.group(0) if match else "")

    def matchAll(self, pattern: str) -> list[str]:
        """
        Return all substrings matching the given regular expression pattern.

        Parameters
        ----------
        pattern : str
            Regular expression pattern to search for.

        Returns
        -------
        list[str]
            List of all matching substrings.
        """
        # Find all non-overlapping matches of the pattern in the string
        return re.findall(pattern, str(self))

    def isMatch(self, pattern: str | list[str]) -> bool:
        """
        Determine if the string matches any of the given regular expression patterns.

        Parameters
        ----------
        pattern : str or list of str
            Regular expression pattern(s) to match.

        Returns
        -------
        bool
            True if the string matches any pattern, otherwise False.
        """
        # Normalize pattern to a list for consistent processing
        if isinstance(pattern, str):
            pattern = [pattern]
        s = str(self)
        # Check if any pattern matches the string
        return any(re.search(p, s) is not None for p in pattern)

    def test(self, pattern: str) -> bool:
        """
        Test if the string matches the given regular expression pattern.

        Parameters
        ----------
        pattern : str
            Regular expression pattern to match.

        Returns
        -------
        bool
            True if the string matches the pattern, otherwise False.
        """
        # Use isMatch to check if the pattern matches the string
        return self.isMatch(pattern)

    def numbers(self) -> "Stringable":
        """
        Remove all non-numeric characters from the string.

        Returns
        -------
        Stringable
            A new Stringable instance containing only numeric characters.
        """
        # Substitute all non-digit characters with an empty string
        return Stringable(re.sub(r"\D", "", str(self)))

    def excerpt(
        self,
        phrase: str = "",
        options: dict | None = None
    ) -> str | None:
        """
        Extract an excerpt containing the first occurrence of a phrase.

        Parameters
        ----------
        phrase : str, optional
            Phrase to search for in the string, by default "".
        options : dict | None, optional
            Options for excerpt extraction. Supported keys:
            - "radius": int, number of characters around the phrase (default 100).
            - "omission": str, string to indicate omitted text (default "...").

        Returns
        -------
        str | None
            Excerpt containing the phrase and surrounding context, or None if not found.
        """
        # Set default options if not provided
        if options is None:
            options = {}

        radius = options.get("radius", 100)
        omission = options.get("omission", "...")

        s = str(self)
        # If no phrase, return the first radius*2 characters with omission if needed
        if not phrase:
            return s[: radius * 2] + (omission if len(s) > radius * 2 else "")

        # Find the position of the phrase (case-insensitive)
        pos = s.lower().find(phrase.lower())
        if pos == -1:
            return None

        # Calculate excerpt boundaries
        start = max(0, pos - radius)
        end = min(len(s), pos + len(phrase) + radius)
        excerpt = s[start:end]

        # Add omission at the start or end if excerpt is truncated
        if start > 0:
            excerpt = omission + excerpt
        if end < len(s):
            excerpt = excerpt + omission

        return excerpt

    def basename(self, suffix: str = "") -> Stringable:
        """
        Return the trailing name component of the path.

        Parameters
        ----------
        suffix : str, optional
            Suffix to remove from the basename. Default is "".

        Returns
        -------
        Stringable
            A new Stringable instance containing the basename with the suffix
            removed if present.
        """
        # Get the basename and remove the suffix if provided
        return Stringable(os.path.basename(str(self)).removesuffix(suffix))

    def dirname(self, levels: int = 1) -> Stringable:
        """
        Return the parent directory path.

        Parameters
        ----------
        levels : int, optional
            Number of directory levels to ascend. Defaults to 1.

        Returns
        -------
        Stringable
            Stringable instance containing the parent directory path.
        """
        path = str(self)
        # Ascend the directory tree by the specified number of levels
        for _ in range(levels):
            path = os.path.dirname(path)
        return Stringable(path)

    def between(self, from_str: str, to_str: str) -> Stringable:
        """
        Return the substring between two given delimiters.

        Parameters
        ----------
        from_str : str
            The starting delimiter.
        to_str : str
            The ending delimiter.

        Returns
        -------
        Stringable
            A new Stringable containing the text between the delimiters, or an
            empty Stringable if delimiters are not found.
        """
        s = str(self)
        # Find the start delimiter
        start = s.find(from_str)
        if start == -1:
            return Stringable("")
        start += len(from_str)
        # Find the end delimiter after the start
        end = s.find(to_str, start)
        if end == -1:
            return Stringable("")
        return Stringable(s[start:end])

    def betweenFirst(self, from_str: str, to_str: str) -> Stringable:
        """
        Return the smallest substring between two delimiters.

        Parameters
        ----------
        from_str : str
            Starting delimiter.
        to_str : str
            Ending delimiter.

        Returns
        -------
        Stringable
            New Stringable containing the text between the first pair of
            delimiters, or an empty Stringable if not found.
        """
        s = str(self)
        # Find the first occurrence of the starting delimiter
        start = s.find(from_str)
        if start == -1:
            return Stringable("")
        start += len(from_str)
        # Find the first occurrence of the ending delimiter after the start
        end = s.find(to_str, start)
        if end == -1:
            return Stringable("")
        return Stringable(s[start:end])

    def finish(self, cap: str) -> Stringable:
        """
        Ensure the string ends with a single instance of the given value.

        Parameters
        ----------
        cap : str
            String to append as a cap if not already present.

        Returns
        -------
        Stringable
            New Stringable instance ending with the specified cap.
        """
        s = str(self)
        # Append cap if not already present at the end
        if not s.endswith(cap):
            s += cap
        return Stringable(s)

    def start(self, prefix: str) -> Stringable:
        """
        Ensure the string starts with a single instance of the given prefix.

        Parameters
        ----------
        prefix : str
            Prefix to ensure at the start of the string.

        Returns
        -------
        Stringable
            New Stringable instance starting with the specified prefix.
        """
        s = str(self)
        # Prepend prefix if not already present at the start
        if not s.startswith(prefix):
            s = prefix + s
        return Stringable(s)

    def explode(self, delimiter: str, limit: int = -1) -> list[str]:
        """
        Split the string into a list using a delimiter.

        Parameters
        ----------
        delimiter : str
            Delimiter to split the string on.
        limit : int, optional
            Maximum number of elements to return. If -1, no limit is applied.

        Returns
        -------
        list of str
            List of substrings after splitting by the delimiter.
        """
        # Split the string by the delimiter, respecting the limit if provided
        if limit == -1:
            return str(self).split(delimiter)
        return str(self).split(delimiter, limit - 1)

    def split(
        self,
        pattern: str | int,
        limit: int = -1,
        flags: int = 0
    ) -> list[str]:
        """
        Split the string by a regular expression or by length.

        Parameters
        ----------
        pattern : str or int
            Regular expression pattern or length for splitting.
        limit : int, optional
            Maximum number of splits. Default is -1 (no limit).
        flags : int, optional
            Regular expression flags. Default is 0.

        Returns
        -------
        list of str
            List of string segments after splitting.
        """
        if isinstance(pattern, int):
            # Split the string into chunks of the given length.
            s = str(self)
            return [s[i : i + pattern] for i in range(0, len(s), pattern)]
        # Split the string using the provided regular expression pattern.
        # In re.split, maxsplit=0 means no limit, -1 means no splits.
        maxsplit = 0 if limit == -1 else limit
        segments = re.split(pattern, str(self), maxsplit=maxsplit, flags=flags)
        return segments if segments else []

    def ucsplit(self) -> list[str]:
        """
        Split the string by uppercase characters.

        Returns
        -------
        list of str
            List of words split by uppercase characters.
        """
        # Use regex to split on uppercase letters, keeping them with the word.
        parts = re.findall(r"[A-Z][a-z]*|[a-z]+|\d+", str(self))
        return parts if parts else [str(self)]

    def squish(self) -> Stringable:
        """
        Normalize whitespace in the string.

        Replace consecutive whitespace characters with a single space and trim
        leading and trailing whitespace.

        Returns
        -------
        Stringable
            A new Stringable instance with normalized whitespace.
        """
        # Replace multiple whitespace characters with a single space, then trim.
        return Stringable(re.sub(r"\s+", " ", str(self)).strip())

    def words(self, words: int = 100, end: str = "...") -> "Stringable":
        """
        Limit the number of words in the string.

        Parameters
        ----------
        words : int, optional
            Maximum number of words to include. Default is 100.
        end : str, optional
            String to append if truncation occurs. Default is '...'.

        Returns
        -------
        Stringable
            A new Stringable instance containing at most the specified number of
            words, with the end string appended if truncation occurs.
        """
        # Split the string into words
        word_list = str(self).split()
        # Return original string if within word limit
        if len(word_list) <= words:
            return Stringable(str(self))
        # Join the limited number of words and append the end string
        truncated = " ".join(word_list[:words])
        return Stringable(truncated + end)

    def wordCount(self, characters: str | None = None) -> int:
        """
        Count the number of words in the string.

        Parameters
        ----------
        characters : str | None, optional
            Additional characters to treat as word separators. Default is None.

        Returns
        -------
        int
            The number of words in the string.
        """
        s = str(self).strip()
        if not s:
            return 0
        # Replace additional separator characters with spaces if provided
        if characters:
            for char in characters:
                s = s.replace(char, " ")
        # Split by whitespace and count non-empty segments
        return len([word for word in s.split() if word])

    def wordWrap(
        self,
        characters: int = 75,
        break_str: str = "\n",
        cut_long_words: bool = False,
    ) -> Stringable:
        """
        Wrap the string to a specified line width.

        Parameters
        ----------
        characters : int, optional
            Maximum line width. Default is 75.
        break_str : str, optional
            String to insert at line breaks. Default is "\\n".
        cut_long_words : bool, optional
            If True, break long words. Default is False.

        Returns
        -------
        Stringable
            A new Stringable instance with wrapped text.
        """
        import textwrap

        # Use textwrap to wrap the string according to the specified options
        if cut_long_words:
            wrapped = textwrap.fill(
                str(self),
                width=characters,
                break_long_words=True,
                break_on_hyphens=True,
                expand_tabs=False,
            )
        else:
            wrapped = textwrap.fill(
                str(self),
                width=characters,
                break_long_words=False,
                break_on_hyphens=True,
                expand_tabs=False,
            )

        # Replace default line breaks with the specified break string
        return Stringable(wrapped.replace("\n", break_str))

    def wrap(self, before: str, after: str | None = None) -> Stringable:
        """
        Wrap the string with the specified prefix and suffix.

        Parameters
        ----------
        before : str
            String to prepend to the start of the string.
        after : str or None, optional
            String to append to the end of the string. If None, uses `before`.

        Returns
        -------
        Stringable
            A new Stringable instance with the string wrapped.
        """
        # Use `before` as both prefix and suffix if `after` is not provided
        if after is None:
            after = before
        return Stringable(before + str(self) + after)

    def unwrap(self, before: str, after: str | None = None) -> Stringable:
        """
        Remove the specified prefix and suffix from the string.

        Parameters
        ----------
        before : str
            Prefix string to remove from the start.
        after : str | None, optional
            Suffix string to remove from the end. If None, uses `before`.

        Returns
        -------
        Stringable
            New Stringable instance with the specified prefix and suffix removed.
        """
        # Use the same string for suffix if not provided
        if after is None:
            after = before

        s = str(self)
        # Remove prefix and suffix if present
        s = s.removeprefix(before)
        s = s.removesuffix(after)

        return Stringable(s)

    def replaceArray(
        self, search: str, replace: list[str]
    ) -> "Stringable":
        """
        Replace a value in the string sequentially with elements from a list.

        Parameters
        ----------
        search : str
            Substring to search for and replace.
        replace : list of str
            List of replacement strings to use sequentially.

        Returns
        -------
        Stringable
            New Stringable with sequential replacements applied.
        """
        s = str(self)
        replace_idx = 0
        # Replace each occurrence of search with the next item in replace
        while search in s and replace_idx < len(replace):
            s = s.replace(search, str(replace[replace_idx]), 1)
            replace_idx += 1
        return Stringable(s)

    def replaceFirst(self, search: str, replace: str) -> Stringable:
        """
        Replace the first occurrence of a substring with a replacement.

        Parameters
        ----------
        search : str
            Substring to search for in the string.
        replace : str
            Replacement string.

        Returns
        -------
        Stringable
            New Stringable instance with the first occurrence replaced.
        """
        # Replace only the first occurrence of the search substring
        return Stringable(str(self).replace(search, replace, 1))

    def replaceLast(self, search: str, replace: str) -> Stringable:
        """
        Replace the last occurrence of a substring with a replacement.

        Parameters
        ----------
        search : str
            Substring to search for in the string.
        replace : str
            Replacement string.

        Returns
        -------
        Stringable
            New Stringable instance with the last occurrence replaced.
        """
        s = str(self)
        # Find the last occurrence of the search substring
        idx = s.rfind(search)
        # Replace the last occurrence if found
        if idx != -1:
            s = s[:idx] + replace + s[idx + len(search):]
        return Stringable(s)

    def replaceStart(self, search: str, replace: str) -> Stringable:
        """
        Replace the first occurrence of a value at the start of the string.

        Parameters
        ----------
        search : str
            String to search for at the start.
        replace : str
            Replacement string.

        Returns
        -------
        Stringable
            New Stringable with the start replaced if the search string is found.
        """
        s = str(self)
        # Replace the start if it matches the search string
        if s.startswith(search):
            s = replace + s[len(search):]
        return Stringable(s)

    def replaceEnd(self, search: str, replace: str) -> Stringable:
        """
        Replace the last occurrence of a value at the end of the string.

        Parameters
        ----------
        search : str
            String to search for at the end.
        replace : str
            Replacement string.

        Returns
        -------
        Stringable
            New Stringable instance with the end replaced if the search string is found.
        """
        s = str(self)
        # Replace the end if it matches the search string
        if s.endswith(search):
            s = s[:-len(search)] + replace
        return Stringable(s)

    def replaceMatches(
        self,
        pattern: str | list[str],
        replace: str | Callable,
        limit: int = -1,
    ) -> Stringable:
        """
        Replace pattern matches in the string using a regular expression.

        Parameters
        ----------
        pattern : str or list of str
            Regular expression pattern(s) to search for.
        replace : str or Callable
            Replacement string or callback function.
        limit : int, optional
            Maximum number of replacements. Default is -1 (no limit).

        Returns
        -------
        Stringable
            A new Stringable instance with pattern matches replaced.
        """
        s = str(self)
        # Normalize patterns to a list for consistent processing
        patterns = [pattern] if isinstance(pattern, str) else pattern
        for pat in patterns:
            # Use callable or string replacement as appropriate
            count = 0 if limit == -1 else limit
            s = re.sub(pat, replace, s, count=count) if callable(replace) else re.sub(
                pat, str(replace), s, count=count
            )
        return Stringable(s)

    def remove(
        self,
        search: str | list[str],
        case_sensitive: bool = True
    ) -> Stringable:
        """
        Remove all occurrences of the specified substring(s) from the string.

        Parameters
        ----------
        search : str or list of str
            Substring(s) to remove from the string.
        case_sensitive : bool, default True
            Whether the removal is case sensitive.

        Returns
        -------
        Stringable
            A new Stringable instance with the specified substrings removed.
        """
        s = str(self)
        # Normalize search to a list for consistent processing
        if isinstance(search, str):
            search = [search]
        # Remove each occurrence of the search string(s)
        for needle in search:
            if case_sensitive:
                s = s.replace(needle, "")
            else:
                s = re.sub(re.escape(needle), "", s, flags=re.IGNORECASE)
        return Stringable(s)

    # Pluralization and singularization methods
    def plural(self, count: Union[int, List, Any] = 2, prepend_count: bool = False) -> Stringable:
        """
        Get the plural form of an English word.

        Parameters
        ----------
        count : int, list or any, optional
            Count to determine if plural is needed, by default 2
        prepend_count : bool, optional
            Whether to prepend the count, by default False

        Returns
        -------
        Stringable
            A new Stringable with plural form
        """
        # Simple pluralization rules
        word = str(self).lower()

        # Determine if we need plural
        if hasattr(count, "__len__"):
            actual_count = len(count)
        elif isinstance(count, (int, float)):
            actual_count = count
        else:
            actual_count = 1

        if actual_count == 1:
            result = str(self)
        else:
            # Simple pluralization rules
            if word.endswith(("s", "sh", "ch", "x", "z")):
                plural_word = str(self) + "es"
            elif word.endswith("y") and len(word) > 1 and word[-2] not in "aeiou":
                plural_word = str(self)[:-1] + "ies"
            elif word.endswith("f"):
                plural_word = str(self)[:-1] + "ves"
            elif word.endswith("fe"):
                plural_word = str(self)[:-2] + "ves"
            else:
                plural_word = str(self) + "s"

            result = plural_word

        if prepend_count:
            result = f"{actual_count} {result}"

        return Stringable(result)

    def pluralStudly(self, count: Union[int, List, Any] = 2) -> Stringable:
        """
        Pluralize the last word of an English, studly caps case string.

        Parameters
        ----------
        count : int, list or any, optional
            Count to determine if plural is needed, by default 2

        Returns
        -------
        Stringable
            A new Stringable with pluralized last word in StudlyCase
        """
        s = str(self)
        # Find the last word boundary
        parts = re.findall(r"[A-Z][a-z]*|[a-z]+", s)
        if parts:
            last_word = parts[-1]
            pluralized_last = Stringable(last_word).plural(count).studly().value()
            parts[-1] = pluralized_last
            return Stringable("".join(parts))

        return self.plural(count).studly()

    def pluralPascal(self, count: Union[int, List, Any] = 2) -> Stringable:
        """
        Pluralize the last word of an English, Pascal caps case string.

        Parameters
        ----------
        count : int, list or any, optional
            Count to determine if plural is needed, by default 2

        Returns
        -------
        Stringable
            A new Stringable with pluralized last word in PascalCase
        """
        # PascalCase is the same as StudlyCase
        s = str(self)
        if len(s) == 0:
            return Stringable(s)

        # Split by uppercase letters to find words
        words = re.findall(r"[A-Z][a-z]*|[a-z]+", s)
        if not words:
            return Stringable(s)

        # Determine if we need plural
        if isinstance(count, (list, tuple)):
            need_plural = len(count) != 1
        else:
            need_plural = count != 1

        if need_plural:
            # Pluralize the last word
            last_word = words[-1]
            pluralized = Stringable(last_word).plural(count)
            words[-1] = pluralized.studly().value()

        return Stringable("".join(words))

    def singular(self) -> Stringable:
        """
        Get the singular form of an English word.

        Returns
        -------
        Stringable
            A new Stringable with singular form
        """
        word = str(self).lower()
        s = str(self)

        # Simple singularization rules
        if word.endswith("ies") and len(word) > 3:
            result = s[:-3] + "y"
        elif word.endswith("ves"):
            if word.endswith("ives"):
                result = s[:-3] + "e"
            else:
                result = s[:-3] + "f"
        elif word.endswith("es"):
            if word.endswith(("ches", "shes", "xes", "zes")) or word.endswith("ses"):
                result = s[:-2]
            else:
                result = s[:-1]
        elif word.endswith("s") and not word.endswith("ss"):
            result = s[:-1]
        else:
            result = s

        return Stringable(result)

    def parseCallback(self, default: Optional[str] = None) -> List[Optional[str]]:
        """
        Parse a Class@method style callback into class and method.

        Parameters
        ----------
        default : str, optional
            Default method name if not specified, by default None

        Returns
        -------
        list
            List containing [class_name, method_name]
        """
        callback_str = str(self)

        if "@" in callback_str:
            parts = callback_str.split("@", 1)
            return [parts[0], parts[1]]
        return [callback_str, default]

    def when(self, condition: Union[bool, Callable], callback: Callable, default: Optional[Callable] = None) -> Stringable:
        """
        Execute the given callback if condition is true.

        Parameters
        ----------
        condition : bool or callable
            The condition to evaluate
        callback : callable
            The callback to execute if condition is true
        default : callable, optional
            The callback to execute if condition is false, by default None

        Returns
        -------
        Stringable
            Result of callback execution or self
        """
        if callable(condition):
            condition_result = condition(self)
        else:
            condition_result = condition

        if condition_result:
            result = callback(self)
            return Stringable(result) if not isinstance(result, Stringable) else result
        if default:
            result = default(self)
            return Stringable(result) if not isinstance(result, Stringable) else result
        return self

    def whenContains(self, needles: Union[str, List[str]], callback: Callable, default: Optional[Callable] = None) -> Stringable:
        """
        Execute the given callback if the string contains a given substring.

        Parameters
        ----------
        needles : str or list
            The substring(s) to search for
        callback : callable
            The callback to execute if condition is true
        default : callable, optional
            The callback to execute if condition is false, by default None

        Returns
        -------
        Stringable
            Result of callback execution or self
        """
        return self.when(self.contains(needles), callback, default)

    def whenContainsAll(self, needles: List[str], callback: Callable, default: Optional[Callable] = None) -> Stringable:
        """
        Execute the given callback if the string contains all array values.

        Parameters
        ----------
        needles : list
            The substrings to search for
        callback : callable
            The callback to execute if condition is true
        default : callable, optional
            The callback to execute if condition is false, by default None

        Returns
        -------
        Stringable
            Result of callback execution or self
        """
        contains_all = all(needle in str(self) for needle in needles)
        return self.when(contains_all, callback, default)

    def whenEmpty(self, callback: Callable, default: Optional[Callable] = None) -> Stringable:
        """
        Execute the given callback if the string is empty.

        Parameters
        ----------
        callback : callable
            The callback to execute if condition is true
        default : callable, optional
            The callback to execute if condition is false, by default None

        Returns
        -------
        Stringable
            Result of callback execution or self
        """
        return self.when(self.isEmpty(), callback, default)

    def whenNotEmpty(self, callback: Callable, default: Optional[Callable] = None) -> Stringable:
        """
        Execute the given callback if the string is not empty.

        Parameters
        ----------
        callback : callable
            The callback to execute if condition is true
        default : callable, optional
            The callback to execute if condition is false, by default None

        Returns
        -------
        Stringable
            Result of callback execution or self
        """
        return self.when(self.isNotEmpty(), callback, default)

    def whenEndsWith(self, needles: Union[str, List[str]], callback: Callable, default: Optional[Callable] = None) -> Stringable:
        """
        Execute the given callback if the string ends with a given substring.

        Parameters
        ----------
        needles : str or list
            The substring(s) to check
        callback : callable
            The callback to execute if condition is true
        default : callable, optional
            The callback to execute if condition is false, by default None

        Returns
        -------
        Stringable
            Result of callback execution or self
        """
        return self.when(self.endsWith(needles), callback, default)

    def whenDoesntEndWith(self, needles: Union[str, List[str]], callback: Callable, default: Optional[Callable] = None) -> Stringable:
        """
        Execute the given callback if the string doesn't end with a given substring.

        Parameters
        ----------
        needles : str or list
            The substring(s) to check
        callback : callable
            The callback to execute if condition is true
        default : callable, optional
            The callback to execute if condition is false, by default None

        Returns
        -------
        Stringable
            Result of callback execution or self
        """
        return self.when(not self.endsWith(needles), callback, default)

    def whenExactly(self, value: str, callback: Callable, default: Optional[Callable] = None) -> Stringable:
        """
        Execute the given callback if the string is an exact match with the given value.

        Parameters
        ----------
        value : str
            The value to compare exactly
        callback : callable
            The callback to execute if condition is true
        default : callable, optional
            The callback to execute if condition is false, by default None

        Returns
        -------
        Stringable
            Result of callback execution or self
        """
        return self.when(self.exactly(value), callback, default)

    def whenNotExactly(self, value: str, callback: Callable, default: Optional[Callable] = None) -> Stringable:
        """
        Execute the given callback if the string is not an exact match with the given value.

        Parameters
        ----------
        value : str
            The value to compare exactly
        callback : callable
            The callback to execute if condition is true
        default : callable, optional
            The callback to execute if condition is false, by default None

        Returns
        -------
        Stringable
            Result of callback execution or self
        """
        return self.when(not self.exactly(value), callback, default)

    def whenStartsWith(self, needles: Union[str, List[str]], callback: Callable, default: Optional[Callable] = None) -> Stringable:
        """
        Execute the given callback if the string starts with a given substring.

        Parameters
        ----------
        needles : str or list
            The substring(s) to check
        callback : callable
            The callback to execute if condition is true
        default : callable, optional
            The callback to execute if condition is false, by default None

        Returns
        -------
        Stringable
            Result of callback execution or self
        """
        if isinstance(needles, str):
            needles = [needles]
        starts_with = any(str(self).startswith(needle) for needle in needles)
        return self.when(starts_with, callback, default)

    def whenDoesntStartWith(self, needles: Union[str, List[str]], callback: Callable, default: Optional[Callable] = None) -> Stringable:
        """
        Execute the given callback if the string doesn't start with a given substring.

        Parameters
        ----------
        needles : str or list
            The substring(s) to check
        callback : callable
            The callback to execute if condition is true
        default : callable, optional
            The callback to execute if condition is false, by default None

        Returns
        -------
        Stringable
            Result of callback execution or self
        """
        if isinstance(needles, str):
            needles = [needles]
        starts_with = any(str(self).startswith(needle) for needle in needles)
        return self.when(not starts_with, callback, default)

    def whenTest(self, pattern: str, callback: Callable, default: Optional[Callable] = None) -> Stringable:
        """
        Execute the given callback if the string matches the given pattern.

        Parameters
        ----------
        pattern : str
            Regular expression pattern
        callback : callable
            The callback to execute if condition is true
        default : callable, optional
            The callback to execute if condition is false, by default None

        Returns
        -------
        Stringable
            Result of callback execution or self
        """
        return self.when(self.test(pattern), callback, default)

    def convertCase(self, mode: int = None) -> Stringable:
        """
        Convert the case of a string.

        Parameters
        ----------
        mode : int, optional
            Case conversion mode:
            0 or None - MB_CASE_FOLD (casefold)
            1 - MB_CASE_UPPER (upper)
            2 - MB_CASE_LOWER (lower)
            3 - MB_CASE_TITLE (title)
            by default None (MB_CASE_FOLD)

        Returns
        -------
        Stringable
            A new Stringable with converted case
        """
        s = str(self)

        # Python doesn't have exact MB_CASE constants, so we'll use simple mappings
        if mode is None or mode == 0:  # MB_CASE_FOLD equivalent
            return Stringable(s.casefold())
        if mode == 1:  # MB_CASE_UPPER equivalent
            return Stringable(s.upper())
        if mode == 2:  # MB_CASE_LOWER equivalent
            return Stringable(s.lower())
        if mode == 3:  # MB_CASE_TITLE equivalent
            return Stringable(s.title())
        return Stringable(s.casefold())

    def transliterate(self, unknown: str = "?", strict: bool = False) -> Stringable:
        """
        Transliterate a string to its closest ASCII representation.

        Parameters
        ----------
        unknown : str, optional
            Character to use for unknown characters, by default '?'
        strict : bool, optional
            Whether to be strict about transliteration, by default False

        Returns
        -------
        Stringable
            A new Stringable with transliterated text
        """
        s = str(self)

        # Use unicodedata to normalize and transliterate
        normalized = unicodedata.normalize("NFKD", s)

        if strict:
            # Only keep ASCII characters
            ascii_chars = []
            for char in normalized:
                if ord(char) < 128:
                    ascii_chars.append(char)
                else:
                    ascii_chars.append(unknown)
            return Stringable("".join(ascii_chars))
        # More lenient transliteration
        ascii_str = "".join(char for char in normalized if ord(char) < 128)
        return Stringable(ascii_str)

    def hash(self, algorithm: str) -> Stringable:
        """
        Hash the string using the given algorithm.

        Parameters
        ----------
        algorithm : str
            Hash algorithm (md5, sha1, sha256, etc.)

        Returns
        -------
        Stringable
            A new Stringable with the hash
        """
        hash_obj = hashlib.new(algorithm)
        hash_obj.update(str(self).encode("utf-8"))
        return Stringable(hash_obj.hexdigest())

    def pipe(self, callback: Callable) -> Stringable:
        """
        Call the given callback and return a new string.

        Parameters
        ----------
        callback : callable
            The callback function to apply

        Returns
        -------
        Stringable
            A new Stringable with the result of the callback
        """
        result = callback(self)
        return Stringable(result) if not isinstance(result, Stringable) else result

    def take(self, limit: int) -> Stringable:
        """
        Take the first or last {limit} characters.

        Parameters
        ----------
        limit : int
            Number of characters to take (negative for from end)

        Returns
        -------
        Stringable
            A new Stringable with the taken characters
        """
        if limit < 0:
            return Stringable(str(self)[limit:])
        return Stringable(str(self)[:limit])

    def swap(self, map_dict: Dict[str, str]) -> Stringable:
        """
        Swap multiple keywords in a string with other keywords.

        Parameters
        ----------
        map_dict : dict
            Dictionary mapping old values to new values

        Returns
        -------
        Stringable
            A new Stringable with swapped values
        """
        s = str(self)
        for old, new in map_dict.items():
            s = s.replace(old, new)
        return Stringable(s)

    def substrCount(self, needle: str, offset: int = 0, length: Optional[int] = None) -> int:
        """
        Returns the number of substring occurrences.

        Parameters
        ----------
        needle : str
            The substring to count
        offset : int, optional
            Starting offset, by default 0
        length : int, optional
            Length to search within, by default None

        Returns
        -------
        int
            Number of occurrences
        """
        s = str(self)

        if length is not None:
            s = s[offset:offset + length]
        else:
            s = s[offset:]

        return s.count(needle)

    def substrReplace(self, replace: Union[str, List[str]], offset: Union[int, List[int]] = 0,
                     length: Optional[Union[int, List[int]]] = None) -> Stringable:
        """
        Replace text within a portion of a string.

        Parameters
        ----------
        replace : str or list
            Replacement string(s)
        offset : int or list, optional
            Starting position(s), by default 0
        length : int, list or None, optional
            Length(s) to replace, by default None

        Returns
        -------
        Stringable
            A new Stringable with replaced text
        """
        s = str(self)

        if isinstance(replace, str):
            replace = [replace]
        if isinstance(offset, int):
            offset = [offset]
        if length is not None and isinstance(length, int):
            length = [length]

        # Process replacements
        result = s
        for i, repl in enumerate(replace):
            off = offset[i] if i < len(offset) else offset[-1]
            if length and i < len(length):
                leng = length[i]
                result = result[:off] + repl + result[off + leng:]
            else:
                result = result[:off] + repl + result[off:]

        return Stringable(result)

    def scan(self, format_str: str) -> List[str]:
        """
        Parse input from a string to a list, according to a format.

        Parameters
        ----------
        format_str : str
            Format string (simplified sscanf-like)

        Returns
        -------
        list
            List of parsed values
        """
        # Simplified implementation - convert format to regex
        # This is a basic implementation, not as full-featured as PHP's sscanf
        pattern = format_str.replace("%s", r"(\S+)").replace("%d", r"(\d+)").replace("%f", r"([\d.]+)")
        matches = re.findall(pattern, str(self))
        return list(matches[0]) if matches else []

    def prepend(self, *values: str) -> Stringable:
        """
        Prepend the given values to the string.

        Parameters
        ----------
        values : str
            Values to prepend

        Returns
        -------
        Stringable
            A new Stringable with prepended values
        """
        return Stringable("".join(values) + str(self))

    def substr(self, start: int, length: Optional[int] = None) -> Stringable:
        """
        Returns the portion of the string specified by the start and length parameters.

        Parameters
        ----------
        start : int
            Starting position
        length : int, optional
            Length to extract, by default None

        Returns
        -------
        Stringable
            A new Stringable with the substring
        """
        s = str(self)
        if length is None:
            return Stringable(s[start:])
        return Stringable(s[start:start + length])

    def doesntContain(self, needles: Union[str, List[str]], ignore_case: bool = False) -> bool:
        """
        Determine if a given string doesn't contain a given substring.

        Parameters
        ----------
        needles : str or list
            The substring(s) to search for
        ignore_case : bool, optional
            Whether to ignore case, by default False

        Returns
        -------
        bool
            True if string doesn't contain any needle, False otherwise
        """
        return not self.contains(needles, ignore_case)

    def doesntStartWith(self, needles: Union[str, List[str]]) -> bool:
        """
        Determine if a given string doesn't start with a given substring.

        Parameters
        ----------
        needles : str or list
            The substring(s) to check

        Returns
        -------
        bool
            True if string doesn't start with any needle, False otherwise
        """
        if isinstance(needles, str):
            needles = [needles]
        return not any(str(self).startswith(needle) for needle in needles)

    def doesntEndWith(self, needles: Union[str, List[str]]) -> bool:
        """
        Determine if a given string doesn't end with a given substring.

        Parameters
        ----------
        needles : str or list
            The substring(s) to check

        Returns
        -------
        bool
            True if string doesn't end with any needle, False otherwise
        """
        return not self.endsWith(needles)

    def startsWith(self, needles: Union[str, List[str]]) -> bool:
        """
        Determine if a given string starts with a given substring.

        Parameters
        ----------
        needles : str or list
            The substring(s) to check

        Returns
        -------
        bool
            True if string starts with any needle, False otherwise
        """
        if isinstance(needles, str):
            needles = [needles]
        return any(str(self).startswith(needle) for needle in needles)

    def jsonSerialize(self) -> str:
        """
        Convert the object to a string when JSON encoded.

        Returns
        -------
        str
            The string representation for JSON serialization
        """
        return str(self)

    def offsetExists(self, offset: int) -> bool:
        """
        Determine if the given offset exists.

        Parameters
        ----------
        offset : int
            The offset to check

        Returns
        -------
        bool
            True if offset exists, False otherwise
        """
        try:
            str(self)[offset]
            return True
        except IndexError:
            return False

    def offsetGet(self, offset: int) -> str:
        """
        Get the value at the given offset.

        Parameters
        ----------
        offset : int
            The offset to get

        Returns
        -------
        str
            The character at the offset
        """
        return str(self)[offset]

    def isPattern(self, pattern: Union[str, List[str]], ignore_case: bool = False) -> bool:
        """
        Determine if a given string matches a given pattern.

        This method checks if the string matches any of the given patterns,
        which can include wildcards (* and ?). The matching can be case-sensitive
        or case-insensitive based on the ignore_case parameter.

        Parameters
        ----------
        pattern : str or List[str]
            Pattern(s) to match (supports wildcards * and ?).
        ignore_case : bool, optional
            Whether to ignore case, by default False.

        Returns
        -------
        bool
            True if string matches any of the patterns, False otherwise.
        """
        import fnmatch

        # Normalize pattern to list for consistent processing
        if isinstance(pattern, str):
            patterns = [pattern]
        else:
            patterns = pattern

        # Get string representation
        s = str(self)

        # Apply case-insensitive matching if requested
        if ignore_case:
            s = s.lower()
            patterns = [p.lower() for p in patterns]

        # Check if string matches any of the patterns
        return any(fnmatch.fnmatch(s, p) for p in patterns)

    def containsAll(self, needles: List[str], ignore_case: bool = False) -> bool:
        """
        Determine if a given string contains all array values.

        Parameters
        ----------
        needles : list
            List of substrings to search for
        ignore_case : bool, optional
            Whether to ignore case, by default False

        Returns
        -------
        bool
            True if string contains all needles, False otherwise
        """
        s = str(self)
        if ignore_case:
            s = s.lower()
            needles = [needle.lower() for needle in needles]

        return all(needle in s for needle in needles)

    def whenIs(self, pattern: Union[str, List[str]], callback: Callable, default: Optional[Callable] = None) -> Stringable:
        """
        Execute the given callback if the string matches a given pattern.

        Parameters
        ----------
        pattern : str or list
            Pattern(s) to match against
        callback : callable
            The callback to execute if condition is true
        default : callable, optional
            The callback to execute if condition is false, by default None

        Returns
        -------
        Stringable
            Result of callback execution or self
        """
        return self.when(self.isPattern(pattern), callback, default)

    def whenIsAscii(self, callback: Callable, default: Optional[Callable] = None) -> Stringable:
        """
        Execute the given callback if the string is 7 bit ASCII.

        Parameters
        ----------
        callback : callable
            The callback to execute if condition is true
        default : callable, optional
            The callback to execute if condition is false, by default None

        Returns
        -------
        Stringable
            Result of callback execution or self
        """
        return self.when(self.isAscii(), callback, default)

    def whenIsUuid(self, callback: Callable, default: Optional[Callable] = None) -> Stringable:
        """
        Execute the given callback if the string is a valid UUID.

        Parameters
        ----------
        callback : callable
            The callback to execute if condition is true
        default : callable, optional
            The callback to execute if condition is false, by default None

        Returns
        -------
        Stringable
            Result of callback execution or self
        """
        return self.when(self.isUuid(), callback, default)

    def whenIsUlid(self, callback: Callable, default: Optional[Callable] = None) -> Stringable:
        """
        Execute the given callback if the string is a valid ULID.

        Parameters
        ----------
        callback : callable
            The callback to execute if condition is true
        default : callable, optional
            The callback to execute if condition is false, by default None

        Returns
        -------
        Stringable
            Result of callback execution or self
        """
        return self.when(self.isUlid(), callback, default)

    def toDate(self, format_str: Optional[str] = None) -> Optional[datetime]:
        """
        Convert the string to a datetime object.

        Parameters
        ----------
        format_str : str, optional
            Format string for parsing, by default None (auto-detect)

        Returns
        -------
        datetime or None
            Parsed datetime object or None if parsing fails
        """
        s = str(self)

        if format_str:
            try:
                return datetime.strptime(s, format_str)
            except ValueError:
                return None

        # Try common date formats
        common_formats = [
            "%Y-%m-%d",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M",
            "%d/%m/%Y",
            "%m/%d/%Y",
            "%d-%m-%Y",
            "%m-%d-%Y",
        ]

        for fmt in common_formats:
            try:
                return datetime.strptime(s, fmt)
            except ValueError:
                continue

        return None

    def encrypt(self) -> Stringable:
        """
        Encrypt the string (placeholder implementation).

        Note: This is a placeholder. In a real implementation, you would use
        a proper encryption library like cryptography.

        Parameters
        ----------
        None

        Returns
        -------
        Stringable
            Encrypted string (base64 encoded for this placeholder)
        """
        return self.toBase64()

    def decrypt(self) -> Stringable:
        """
        Decrypt the string (placeholder implementation).

        Note: This is a placeholder. In a real implementation, you would use
        a proper decryption library like cryptography.

        Parameters
        ----------
        None

        Returns
        -------
        Stringable
            Decrypted string
        """
        return self.fromBase64()

    def toHtmlString(self) -> Stringable:
        """
        Escape HTML entities in the string.

        Parameters
        ----------
        None

        Returns
        -------
        Stringable
            HTML-safe string with entities escaped.
        """
        # Escape HTML entities for safe HTML output
        return Stringable(html.escape(str(self)))

    def tap(self, callback: Callable[[Stringable], Any]) -> Stringable:
        """
        Call the callback with the string and return the string.

        Parameters
        ----------
        callback : Callable[[Stringable], Any]
            Function to execute with the string.

        Returns
        -------
        Stringable
            The same Stringable instance.
        """
        # Invoke the callback with self, but do not alter the string.
        callback(self)
        return self
