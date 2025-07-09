"""
Text Normalizer for Voice-to-Text Coding
Handles technical word replacements and programming-specific normalization
"""

import re
from typing import Dict, List, Tuple


class TextNormalizer:
    """Normalizes voice-to-text output for programming and technical use"""
    
    def __init__(self):
        self.enabled = True
        self.normalization_rules = self._build_normalization_rules()
        self.case_sensitive_rules = self._build_case_sensitive_rules()
        
    def _build_normalization_rules(self) -> Dict[str, str]:
        """Build case-insensitive normalization rules"""
        return {
            # Basic symbols
            "underscore": "_",
            "under score": "_",
            "dash": "-",
            "hyphen": "-",
            "equals": "=",
            "equal": "=",
            "plus": "+",
            "minus": "-",
            "star": "*",
            "asterisk": "*",
            "slash": "/",
            "backslash": "\\\\",
            "pipe": "|",
            "ampersand": "&",
            "at sign": "@",
            "hash": "#",
            "hashtag": "#",
            "pound": "#",
            "dollar": "$",
            "percent": "%",
            "caret": "^",
            "tilde": "~",
            "grave": "`",
            "backtick": "`",
            
            # Brackets and parentheses
            "open paren": "(",
            "close paren": ")",
            "left paren": "(",
            "right paren": ")",
            "open bracket": "[",
            "close bracket": "]",
            "left bracket": "[",
            "right bracket": "]",
            "open brace": "{",
            "close brace": "}",
            "left brace": "{",
            "right brace": "}",
            "open curly": "{",
            "close curly": "}",
            "left curly": "{",
            "right curly": "}",
            
            # Quotes
            "single quote": "'",
            "double quote": '"',
            "quote": '"',
            "tick": "'",
            
            # Comparison operators
            "less than": "<",
            "greater than": ">",
            "less than or equal": "<=",
            "greater than or equal": ">=",
            "not equal": "!=",
            "not equals": "!=",
            "double equals": "==",
            "triple equals": "===",
            
            # Logical operators
            "and and": "&&",
            "or or": "||",
            "not not": "!!",
            
            # Common punctuation
            "semicolon": ";",
            "colon": ":",
            "comma": ",",
            "period": ".",
            "dot": ".",
            "question mark": "?",
            "exclamation": "!",
            "exclamation mark": "!",
            
            # Numbers (spoken words to digits)
            "zero": "0",
            "one": "1",
            "two": "2",
            "three": "3",
            "four": "4",
            "five": "5",
            "six": "6",
            "seven": "7",
            "eight": "8",
            "nine": "9",
            "ten": "10",
            "eleven": "11",
            "twelve": "12",
            "thirteen": "13",
            "fourteen": "14",
            "fifteen": "15",
            "sixteen": "16",
            "seventeen": "17",
            "eighteen": "18",
            "nineteen": "19",
            "twenty": "20",
            "thirty": "30",
            "forty": "40",
            "fifty": "50",
            "sixty": "60",
            "seventy": "70",
            "eighty": "80",
            "ninety": "90",
            "hundred": "100",
            "thousand": "1000",
            
            # File extensions (common ones)
            "dot py": ".py",
            "dot js": ".js",
            "dot ts": ".ts",
            "dot html": ".html",
            "dot css": ".css",
            "dot json": ".json",
            "dot xml": ".xml",
            "dot txt": ".txt",
            "dot md": ".md",
            "dot yml": ".yml",
            "dot yaml": ".yaml",
            "dot sql": ".sql",
            "dot sh": ".sh",
            "dot bat": ".bat",
            "dot exe": ".exe",
            "dot dll": ".dll",
            "dot jar": ".jar",
            "dot cpp": ".cpp",
            "dot c": ".c",
            "dot h": ".h",
            "dot java": ".java",
            "dot php": ".php",
            "dot rb": ".rb",
            "dot go": ".go",
            "dot rs": ".rs",
            "dot swift": ".swift",
            "dot kt": ".kt",
            "dot scala": ".scala",
            "dot r": ".r",
            "dot m": ".m",
            "dot mm": ".mm",
            
            # Programming keywords and common terms
            "def": "def",
            "function": "function",
            "class": "class",
            "import": "import",
            "from": "from",
            "return": "return",
            "if": "if",
            "else": "else",
            "elif": "elif",
            "for": "for",
            "while": "while",
            "try": "try",
            "except": "except",
            "finally": "finally",
            "with": "with",
            "as": "as",
            "true": "true",
            "false": "false",
            "null": "null",
            "none": "None",
            "undefined": "undefined",
            "var": "var",
            "let": "let",
            "const": "const",
            "async": "async",
            "await": "await",
            
            # Common method names
            "get": "get",
            "set": "set",
            "post": "post",
            "put": "put",
            "delete": "delete",
            "update": "update",
            "create": "create",
            "read": "read",
            "write": "write",
            "open": "open",
            "close": "close",
            "save": "save",
            "load": "load",
            "init": "init",
            "main": "main",
            "test": "test",
            "run": "run",
            "start": "start",
            "stop": "stop",
            
            # Common variable patterns
            "camel case": "camelCase",
            "snake case": "snake_case",
            "kebab case": "kebab-case",
            "pascal case": "PascalCase",
            
            # Version control
            "git": "git",
            "commit": "commit",
            "push": "push",
            "pull": "pull",
            "merge": "merge",
            "branch": "branch",
            "checkout": "checkout",
            "clone": "clone",
            "status": "status",
            "log": "log",
            "diff": "diff",
            "add": "add",
            "remove": "remove",
            "rm": "rm",
            "mv": "mv",
            "cp": "cp",
            "ls": "ls",
            "cd": "cd",
            "pwd": "pwd",
            "mkdir": "mkdir",
            "rmdir": "rmdir",
            "chmod": "chmod",
            "chown": "chown",
            "grep": "grep",
            "find": "find",
            "sed": "sed",
            "awk": "awk",
            "sort": "sort",
            "uniq": "uniq",
            "head": "head",
            "tail": "tail",
            "cat": "cat",
            "less": "less",
            "more": "more",
            "nano": "nano",
            "vim": "vim",
            "emacs": "emacs",
        }
    
    def _build_case_sensitive_rules(self) -> Dict[str, str]:
        """Build case-sensitive normalization rules (applied after case-insensitive)"""
        return {
            # SQL keywords (uppercase)
            "select": "SELECT",
            "from": "FROM",
            "where": "WHERE",
            "order by": "ORDER BY",
            "group by": "GROUP BY",
            "having": "HAVING",
            "insert": "INSERT",
            "update": "UPDATE",
            "delete": "DELETE",
            "create": "CREATE",
            "drop": "DROP",
            "alter": "ALTER",
            "table": "TABLE",
            "database": "DATABASE",
            "index": "INDEX",
            "view": "VIEW",
            "procedure": "PROCEDURE",
            "function": "FUNCTION",
            
            # Common constants
            "true": "True",  # Python
            "false": "False",  # Python
            "null": "None",  # Python
            "this": "this",
            "self": "self",
            "super": "super",
            "static": "static",
            "final": "final",
            "abstract": "abstract",
            "public": "public",
            "private": "private",
            "protected": "protected",
            "virtual": "virtual",
            "override": "override",
            "interface": "interface",
            "enum": "enum",
            "struct": "struct",
            "union": "union",
            "typedef": "typedef",
            "namespace": "namespace",
            "using": "using",
            "template": "template",
            "typename": "typename",
            "operator": "operator",
            "sizeof": "sizeof",
            "typeof": "typeof",
            "instanceof": "instanceof",
            "new": "new",
            "delete": "delete",
            "malloc": "malloc",
            "free": "free",
            "printf": "printf",
            "scanf": "scanf",
            "cout": "cout",
            "cin": "cin",
            "endl": "endl",
            "std": "std",
            "iostream": "iostream",
            "vector": "vector",
            "string": "string",
            "array": "array",
            "list": "list",
            "dict": "dict",
            "set": "set",
            "tuple": "tuple",
            "map": "map",
            "pair": "pair",
            "queue": "queue",
            "stack": "stack",
            "deque": "deque",
            "priority_queue": "priority_queue",
            "unordered_map": "unordered_map",
            "unordered_set": "unordered_set",
        }
    
    def normalize_text(self, text: str) -> str:
        """Apply all normalization rules to the text"""
        if not self.enabled or not text:
            return text
            
        normalized = text
        
        try:
            # Apply case-insensitive rules first
            for phrase, replacement in self.normalization_rules.items():
                try:
                    # Use word boundaries to avoid partial matches
                    pattern = r'\b' + re.escape(phrase) + r'\b'
                    normalized = re.sub(pattern, replacement, normalized, flags=re.IGNORECASE)
                except Exception as e:
                    print(f"Error processing phrase '{phrase}': {e}")
                    continue
            
            # Apply case-sensitive rules
            for phrase, replacement in self.case_sensitive_rules.items():
                try:
                    pattern = r'\b' + re.escape(phrase) + r'\b'
                    normalized = re.sub(pattern, replacement, normalized)
                except Exception as e:
                    print(f"Error processing case-sensitive phrase '{phrase}': {e}")
                    continue
            
            # Apply post-processing rules
            normalized = self._apply_post_processing(normalized)
            
            return normalized
            
        except Exception as e:
            print(f"Text normalization error: {e}")
            return text
    
    def _apply_post_processing(self, text: str) -> str:
        """Apply minimal post-processing - NO automatic spacing"""
        
        try:
            # ONLY fix file extensions (remove spaces around dots)
            text = re.sub(r'\s*\.\s*([a-zA-Z]{1,4})\b', r'.\1', text)
            
            # Join consecutive single digits (e.g., "1 2 3" -> "123")
            text = re.sub(r'\b(\d)\s+(?=\d\b)', r'\1', text)
            
            # Remove any extra spaces but keep single spaces between words
            text = re.sub(r'\s{2,}', r' ', text)
            
            return text.strip()
            
        except Exception as e:
            print(f"Post-processing error: {e}")
            return text.strip()
    
    def add_custom_rule(self, phrase: str, replacement: str, case_sensitive: bool = False):
        """Add a custom normalization rule"""
        if case_sensitive:
            self.case_sensitive_rules[phrase] = replacement
        else:
            self.normalization_rules[phrase.lower()] = replacement
    
    def remove_custom_rule(self, phrase: str, case_sensitive: bool = False):
        """Remove a custom normalization rule"""
        if case_sensitive:
            self.case_sensitive_rules.pop(phrase, None)
        else:
            self.normalization_rules.pop(phrase.lower(), None)
    
    def enable(self):
        """Enable text normalization"""
        self.enabled = True
    
    def disable(self):
        """Disable text normalization"""
        self.enabled = False
    
    def is_enabled(self) -> bool:
        """Check if text normalization is enabled"""
        return self.enabled
    
    def get_rules_count(self) -> Tuple[int, int]:
        """Get the number of rules (case_insensitive, case_sensitive)"""
        return len(self.normalization_rules), len(self.case_sensitive_rules)
    
    def preview_normalization(self, text: str) -> Dict[str, str]:
        """Preview what changes would be made without applying them"""
        original = text
        normalized = self.normalize_text(text)
        
        changes = []
        if original != normalized:
            # Find specific changes (simplified)
            words_before = original.split()
            words_after = normalized.split()
            
            if len(words_before) == len(words_after):
                for i, (before, after) in enumerate(zip(words_before, words_after)):
                    if before != after:
                        changes.append(f"'{before}' → '{after}'")
            else:
                changes.append("Structure changed")
        
        return {
            "original": original,
            "normalized": normalized,
            "changes": changes,
            "has_changes": original != normalized
        }


# Global instance for easy access
text_normalizer = TextNormalizer()


def normalize_text(text: str) -> str:
    """Convenience function for text normalization"""
    return text_normalizer.normalize_text(text)


def add_normalization_rule(phrase: str, replacement: str, case_sensitive: bool = False):
    """Convenience function to add a custom rule"""
    text_normalizer.add_custom_rule(phrase, replacement, case_sensitive)


def preview_normalization(text: str) -> Dict[str, str]:
    """Convenience function to preview normalization changes"""
    return text_normalizer.preview_normalization(text) 