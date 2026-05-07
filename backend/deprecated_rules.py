DEPRECATED_RULES = [
    {
        "api_name": "urllib.urlopen",
        "language": "python",
        "pattern": r"\burllib\.urlopen\s*\(",
        "replace_pattern": r"urllib.request.urlopen(",
        "reason": "Deprecated since Python 2.6, removed in Python 3.",
        "replacement": "urllib.request.urlopen",
        "manual_steps": "1. Import urllib.request.\n2. Replace urllib.urlopen() calls with urllib.request.urlopen().",
        "effort": "low",
        "cost_per_occurrence": 10
    },
    {
        "api_name": "optparse",
        "language": "python",
        "pattern": r"^\s*import\s+optparse\b",
        "replace_pattern": r"import argparse",
        "reason": "Deprecated since Python 3.2.",
        "replacement": "argparse",
        "manual_steps": "1. Replace 'import optparse' with 'import argparse'.\n2. Update optparse.OptionParser() to argparse.ArgumentParser().\n3. Change add_option() calls to add_argument().",
        "effort": "medium",
        "cost_per_occurrence": 30
    },
    {
        "api_name": "distutils",
        "language": "python",
        "pattern": r"^\s*import\s+distutils\b",
        "replace_pattern": r"import setuptools",
        "reason": "Deprecated in Python 3.10 and removed in 3.12.",
        "replacement": "setuptools",
        "manual_steps": "1. Replace 'import distutils' with 'import setuptools'.\n2. Update any distutils.core.setup() calls to setuptools.setup().",
        "effort": "high",
        "cost_per_occurrence": 50
    },
    {
        "api_name": "cgi",
        "language": "python",
        "pattern": r"^\s*from\s+cgi\s+import\s+FieldStorage\b",
        "replace_pattern": r"# TODO: Replace cgi.FieldStorage with multipart or similar\n# from cgi import FieldStorage",
        "reason": "Deprecated in Python 3.11 and removed in 3.13.",
        "replacement": "html or urllib",
        "manual_steps": "1. Remove the 'cgi' module import.\n2. For form parsing, use the 'multipart' library or a web framework's request parser (like Flask or Django).\n3. For html escaping, use the 'html' module.",
        "effort": "medium",
        "cost_per_occurrence": 40
    },
    {
        "api_name": "imghdr",
        "language": "python",
        "pattern": r"^\s*import\s+imghdr\b",
        "replace_pattern": r"import filetype",
        "reason": "Deprecated in Python 3.11 and removed in 3.13.",
        "replacement": "filetype or puremagic",
        "manual_steps": "1. Install an alternative like 'filetype' (pip install filetype).\n2. Replace 'import imghdr' with 'import filetype'.\n3. Update imghdr.what() calls to filetype.guess().",
        "effort": "low",
        "cost_per_occurrence": 15
    },
    {
        "api_name": "String.prototype.substr()",
        "language": "javascript",
        "pattern": r"\.\s*substr\s*\(",
        "replace_pattern": r".substring(",
        "reason": "Considered a legacy function, not strictly deprecated but advised against.",
        "replacement": "String.prototype.substring() or String.prototype.slice()",
        "manual_steps": "1. Identify the .substr(start, length) call.\n2. Replace it with .substring(start, start + length) or .slice(start, start + length).",
        "effort": "low",
        "cost_per_occurrence": 5
    },
    {
        "api_name": "escape()",
        "language": "javascript",
        "pattern": r"\bescape\s*\(",
        "replace_pattern": r"encodeURIComponent(",
        "reason": "Deprecated since ECMAScript v3.",
        "replacement": "encodeURI() or encodeURIComponent()",
        "manual_steps": "1. Replace escape(str) with encodeURIComponent(str).\n2. Note that encodeURIComponent escapes more characters than escape() did, test accordingly.",
        "effort": "low",
        "cost_per_occurrence": 10
    },
    {
        "api_name": "unescape()",
        "language": "javascript",
        "pattern": r"\bunescape\s*\(",
        "replace_pattern": r"decodeURIComponent(",
        "reason": "Deprecated since ECMAScript v3.",
        "replacement": "decodeURI() or decodeURIComponent()",
        "manual_steps": "1. Replace unescape(str) with decodeURIComponent(str).",
        "effort": "low",
        "cost_per_occurrence": 10
    },
    {
        "api_name": "document.execCommand()",
        "language": "javascript",
        "pattern": r"\bdocument\.execCommand\s*\(",
        "replace_pattern": r"navigator.clipboard.writeText( /* TODO: Migrate document.execCommand */ ",
        "reason": "Obsolete and no longer recommended.",
        "replacement": "Clipboard API",
        "manual_steps": "1. Determine the command being executed (e.g., 'copy', 'cut').\n2. Rewrite the logic using the modern async Clipboard API (navigator.clipboard.writeText or readText).",
        "effort": "medium",
        "cost_per_occurrence": 25
    },
    {
        "api_name": "window.showModalDialog()",
        "language": "javascript",
        "pattern": r"\bwindow\.showModalDialog\s*\(",
        "replace_pattern": r"window.open( /* TODO: Replace showModalDialog */ ",
        "reason": "Removed from modern browsers.",
        "replacement": "<dialog> element or custom modal",
        "manual_steps": "1. Replace window.showModalDialog with the HTML <dialog> element or a custom UI modal component.\n2. Refactor the synchronous code to handle the asynchronous nature of modern modals (using callbacks or Promises).",
        "effort": "high",
        "cost_per_occurrence": 40
    },
    {
        "api_name": "openai.Completion.create",
        "language": "python",
        "pattern": r"\bopenai\.Completion\.create\s*\(",
        "replace_pattern": r"client.chat.completions.create(",
        "reason": "Deprecated in OpenAI v1.0.0.",
        "replacement": "client.chat.completions.create",
        "manual_steps": "1. Instantiate the OpenAI client: `from openai import OpenAI\nclient = OpenAI()`.\n2. Replace `openai.Completion.create` with `client.chat.completions.create`.\n3. Note that the response object has changed structure, access `.message.content` instead of `.text`.",
        "effort": "medium",
        "cost_per_occurrence": 20
    },
    {
        "api_name": "xrange()",
        "language": "python",
        "pattern": r"\bxrange\s*\(",
        "replace_pattern": r"range(",
        "reason": "Deprecated in Python 3; use range() instead.",
        "replacement": "range()",
        "manual_steps": "1. Replace all occurrences of xrange() with range(). In Python 3, range() behaves like Python 2's xrange().",
        "effort": "low",
        "cost_per_occurrence": 5
    },
    {
        "api_name": "raw_input()",
        "language": "python",
        "pattern": r"\braw_input\s*\(",
        "replace_pattern": r"input(",
        "reason": "Deprecated in Python 3; use input() instead.",
        "replacement": "input()",
        "manual_steps": "1. Replace all occurrences of raw_input() with input().",
        "effort": "low",
        "cost_per_occurrence": 5
    }
]
