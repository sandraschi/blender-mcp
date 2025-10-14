# MCP Tool Documentation Standards
## Making AI Assistants Succeed on the First Try

**Version**: 1.0  
**Last Updated**: 2025-10-10  
**Status**: Community Best Practices  
**Target Audience**: MCP Server Developers

---

## Executive Summary

**The Problem**: AI assistants like Claude frequently fail when using MCP tools because docstrings lack critical information. This leads to:
- Multiple failed attempts before success ("flailing")
- User frustration and lost trust
- Wasted API tokens and latency
- Poor user experience

**The Solution**: Comprehensive tool documentation that provides:
- Clear prerequisites and constraints
- Concrete examples with realistic values
- Error conditions with actionable solutions
- Complete parameter and return format specifications

**The Impact**: Well-documented tools achieve >90% first-call success rate vs <50% for poorly documented tools.

**Quick Win**: Adding 3 realistic examples to each tool can double the success rate.

---

## Table of Contents

1. [Why This Matters](#why-this-matters)
2. [The Golden Rule](#the-golden-rule)
3. [Required Documentation Elements](#required-documentation-elements)
4. [Complete Documentation Template](#complete-documentation-template)
5. [Real-World Example: Before and After](#real-world-example-before-and-after)
6. [Anti-Patterns to Avoid](#anti-patterns-to-avoid)
7. [Implementation Checklist](#implementation-checklist)
8. [Measuring Success](#measuring-success)
9. [Quick Reference Guide](#quick-reference-guide)
10. [Community Resources](#community-resources)

---

## Why This Matters

### The Real Cost of Poor Documentation

When an AI assistant encounters a poorly documented tool, here's what happens:

1. **First attempt fails** (wrong parameter format)
2. **Second attempt fails** (missing required parameter)
3. **Third attempt fails** (incorrect prerequisite state)
4. **Fourth attempt succeeds** (finally figured it out)

**User Experience**: "Why is Claude so dumb? It took 4 tries to do something simple!"

**Reality**: Claude isn't dumb - the tool documentation is inadequate.

### Success Metrics

| Documentation Quality | First-Call Success | User Satisfaction | Token Efficiency |
|----------------------|-------------------|-------------------|------------------|
| Poor (one-liner)     | 30-50%            | Low               | 3-5x waste       |
| Average (basic types)| 60-70%            | Medium            | 1.5-2x waste     |
| Good (this standard) | 90-95%            | High              | Optimal          |

### ROI Calculation

- **Time to write good docs**: 15-30 minutes per tool
- **Time saved per user**: 2-5 minutes per use
- **Break-even**: 10-15 tool calls
- **Typical tool usage**: 100s-1000s of calls

**Every hour spent on documentation saves 10-50 hours of user frustration.**

---

## The Golden Rule

> **Your docstring should enable the AI assistant to succeed on the FIRST try, not after multiple failed attempts.**

If you have to explain how to use your tool in chat more than once, your documentation is inadequate.

---

## Required Documentation Elements

Every MCP tool must include these 7 elements:

### 1. One-Line Summary (with Key Constraint)

State the purpose AND critical constraint in one line.

**❌ BAD**: "Search bookmarks by title or URL."  
**✅ GOOD**: "Search Firefox bookmarks by title/URL (requires Firefox closed)."

**Why it matters**: The AI needs to know upfront if there are blockers.

---

### 2. Prerequisites Section

List everything that must be true BEFORE calling the tool.

```python
"""
Prerequisites:
    - Firefox must be completely closed (check system tray)
    - Profile path must exist and be readable
    - places.sqlite database must not be locked
    - Minimum Firefox version: 57+ (uses SQLite FTS5)
"""
```

**Why it matters**: Prevents 90% of "database locked" errors.

---

### 3. Parameter Documentation (The Critical Part)

Every parameter needs **5 things**:

1. **Type**: `(str, REQUIRED)` or `(int, OPTIONAL)` in CAPS
2. **Purpose**: What it does in plain language
3. **Format/Constraints**: Pattern, range, or validation rules
4. **Concrete Example**: Real value, not placeholder
5. **Default**: For optional parameters

**❌ BAD**:
```python
"""
Args:
    query: Search term
    profile_path: Path to profile
"""
```

**✅ GOOD**:
```python
"""
Args:
    query (str, REQUIRED):
        Search term to find in bookmark titles or URLs
        Case-insensitive, supports partial matches
        Examples: "plex", "github.com", "machine learning tutorial"
        Min length: 1 character
        
    profile_path (str, OPTIONAL):
        Full absolute path to Firefox profile directory
        Format: "C:\\Users\\{username}\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\{profile_id}"
        Example: "C:\\Users\\sandr\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\airiswdq.default-release"
        Default: Auto-detects from profiles.ini (may fail with multiple profiles)
        Get path: Use get_firefox_profiles() tool first
        Platform: Windows requires double backslashes, Linux/Mac use forward slashes
        
    limit (int, OPTIONAL):
        Maximum number of bookmark results to return
        Range: 1-100 (values outside range will be clamped)
        Default: 50
        Performance: <20 is fast, 50-100 may take 1-2 seconds with large databases
"""
```

**Why it matters**: The AI knows exactly how to construct the call correctly.

---

### 4. Return Format (Show Structure, Not Just Type)

Don't just say "returns dict" - show the ACTUAL structure with field descriptions.

**❌ BAD**:
```python
"""
Returns:
    dict: Search results
"""
```

**✅ GOOD**:
```python
"""
Returns:
    dict: Search results with metadata
    
    Structure:
    {
        "status": str,              # "success" or "error"
        "query": str,               # Echo of search query
        "count": int,               # Number of results found
        "profile": str,             # Profile path used
        "results": [                # List of bookmark objects (may be empty)
            {
                "id": int,          # Unique bookmark ID (for other operations)
                "title": str,       # Bookmark title (may be empty)
                "url": str,         # Full URL including protocol
                "dateAdded": int,   # Unix timestamp in microseconds
                "lastModified": int,# Unix timestamp in microseconds  
                "parent": int,      # Parent folder ID (0 = root)
                "tags": [str]       # List of tags (may be empty)
            }
        ],
        "truncated": bool,          # True if results limited by 'limit' parameter
        "execution_time_ms": float  # Query execution time
    }
    
    On Error:
    {
        "status": "error",
        "error": str,               # Error message
        "error_code": str,          # Machine-readable error code
        "suggestion": str           # How to fix the error
    }
"""
```

**Why it matters**: The AI knows how to parse the response and handle errors.

---

### 5. Common Errors with Actionable Solutions

Don't just list errors - tell the AI (and user) HOW TO FIX THEM.

**❌ BAD**:
```python
"""
Raises:
    DatabaseError: Database connection failed
    ValueError: Invalid input
"""
```

**✅ GOOD**:
```python
"""
Common Issues & Solutions:

1. "Failed to connect to database" / "Database is locked"
   CAUSE: Firefox is still running
   FIX: Close Firefox completely
   - Windows: Check Task Manager for firefox.exe processes
   - Linux: killall firefox
   - macOS: Check Activity Monitor
   - Also check system tray for hidden Firefox instance
   WORKAROUND: Use export_bookmarks() tool instead (works while Firefox open)

2. "Profile not found" / "places.sqlite not found"
   CAUSE: Invalid profile path or profile doesn't exist
   FIX: Get correct path first
   - Call get_firefox_profiles() to list available profiles
   - Verify path exists: "C:\\Users\\...\\Profiles\\{profile_name}"
   - Check for typos (path is case-sensitive on Linux/Mac)
   
3. "No results found" (empty results array)
   CAUSE: Search term doesn't match any bookmarks
   FIX: Try different search strategies
   - Broaden search: "plex" instead of "plex media server"
   - Check spelling
   - Try URL domain: "github.com" instead of project name
   - Use list_bookmarks() to browse all bookmarks
   
4. "Permission denied"
   CAUSE: Insufficient file system permissions
   FIX: Check file permissions
   - Windows: Run as administrator or check file properties
   - Linux/Mac: Check places.sqlite permissions (should be 0600 or 0644)
   - Verify user owns the Firefox profile directory
"""
```

**Why it matters**: Self-service error resolution without needing to ask for help.

---

### 6. Complete Working Examples (The Most Important Part)

Provide **3+ realistic examples** covering common use cases.

**❌ BAD**:
```python
"""
Example:
    search_bookmarks("query")
"""
```

**✅ GOOD**:
```python
"""
Examples:

    # Example 1: Basic search with auto-detected profile (most common case)
    # Use when: You have only one Firefox profile and Firefox is closed
    result = search_bookmarks(
        query="plex"
    )
    # Returns: All bookmarks with "plex" in title or URL
    
    
    # Example 2: Search specific profile with limit (multiple profiles)
    # Use when: You have multiple Firefox profiles or need to specify which one
    result = search_bookmarks(
        query="immich",
        profile_path="C:\\Users\\sandr\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\airiswdq.default-release",
        limit=20
    )
    # Returns: Up to 20 bookmarks matching "immich"
    
    
    # Example 3: Search by domain name (finding all bookmarks from a site)
    # Use when: You want all bookmarks from a specific website
    result = search_bookmarks(
        query="github.com",
        limit=100
    )
    # Returns: All GitHub bookmarks (up to 100)
    
    
    # Example 4: Broad search with high limit (comprehensive search)
    # Use when: You want to find everything related to a topic
    result = search_bookmarks(
        query="AI",
        limit=100
    )
    # Returns: All bookmarks with "AI" in title or URL
    
    
    # Example 5: Error handling pattern (production code)
    # Use when: You need robust error handling
    try:
        result = search_bookmarks(
            query="machine learning",
            limit=50
        )
        
        if result["status"] == "success":
            print(f"Found {result['count']} bookmarks")
            for bookmark in result["results"]:
                print(f"- {bookmark['title']}: {bookmark['url']}")
        else:
            print(f"Error: {result['error']}")
            print(f"Suggestion: {result['suggestion']}")
            
    except Exception as e:
        print(f"Unexpected error: {e}")
        # Fallback: try export_bookmarks() instead
"""
```

**Why it matters**: The AI can copy-paste and adapt examples directly.

---

### 7. Platform-Specific Notes

Document Windows/Linux/Mac differences explicitly.

**✅ GOOD**:
```python
"""
Platform Notes:

    WINDOWS:
        - Profile location: %APPDATA%\\Mozilla\\Firefox\\Profiles\\
        - Path format: Use DOUBLE backslashes "C:\\Users\\..."
        - Check Firefox: Task Manager → Details tab → firefox.exe
        - Common issue: OneDrive may sync profile (causes locks)
        
    LINUX:
        - Profile location: ~/.mozilla/firefox/
        - Path format: /home/{user}/.mozilla/firefox/{profile}
        - Check Firefox: ps aux | grep firefox
        - Common issue: Snap Firefox uses different profile path
        
    MACOS:
        - Profile location: ~/Library/Application Support/Firefox/Profiles/
        - Path format: /Users/{user}/Library/Application Support/...
        - Check Firefox: Activity Monitor or ps aux | grep firefox
        - Common issue: Firefox may run in background (check menu bar)
        
    Cross-Platform:
        - places.sqlite is portable across platforms
        - Bookmark IDs are consistent across platforms
        - Timestamps are Unix microseconds (same everywhere)
"""
```

**Why it matters**: The AI knows platform-specific quirks upfront.

---

## Complete Documentation Template

Here's the complete template you can copy-paste:

```python
def tool_name(param1: str, param2: Optional[int] = None) -> Dict:
    """[One-line purpose with critical constraint]
    
    [2-3 sentences describing what this tool does and when to use it.
    Mention any important limitations or considerations.]
    
    Prerequisites:
        - [Requirement 1: specific condition that must be true]
        - [Requirement 2: external state needed]
        - [Requirement 3: permissions/access required]
    
    Args:
        param1 (str, REQUIRED):
            [What this parameter does in plain language]
            Format: [pattern/structure with curly braces for variables]
            Example: [concrete realistic value]
            Validation: [constraints, min/max, allowed values]
            
        param2 (int, OPTIONAL):
            [What this parameter does]
            Range: [min-max values]
            Default: [default value and why it's chosen]
            Example: [realistic value]
            Performance: [impact of different values if relevant]
    
    Returns:
        [type]: [Brief description]
        
        Structure (Success):
        {
            "field1": type,  # Description and valid values
            "field2": type,  # Description
            "nested": {      # Nested structure
                "subfield": type  # Description
            }
        }
        
        Structure (Error):
        {
            "status": "error",
            "error": str,        # Human-readable error
            "error_code": str,   # Machine-readable code
            "suggestion": str    # How to fix
        }
    
    Common Issues & Solutions:
        
        1. [Error message or condition]
           CAUSE: [Why this happens]
           FIX: [Step-by-step solution]
           - [Specific action 1]
           - [Specific action 2]
           WORKAROUND: [Alternative approach if fix isn't possible]
           
        2. [Another error or issue]
           CAUSE: [Root cause]
           FIX: [How to resolve]
           
        3. [Edge case or unexpected behavior]
           CAUSE: [Explanation]
           FIX: [Solution]
    
    Examples:
        
        # Example 1: [Most common use case - describe when to use]
        result = tool_name(
            param1="realistic_value"
        )
        # Returns: [What to expect]
        # Use when: [Scenario description]
        
        
        # Example 2: [Second common case - with optional param]
        result = tool_name(
            param1="another_realistic_value",
            param2=42
        )
        # Returns: [What to expect]
        # Use when: [Scenario description]
        
        
        # Example 3: [Advanced or edge case]
        result = tool_name(
            param1="special_case_value",
            param2=100
        )
        # Returns: [What to expect]
        # Use when: [Scenario description]
        
        
        # Example 4: [Error handling pattern]
        try:
            result = tool_name(param1="value")
            if result["status"] == "success":
                # Handle success
                pass
            else:
                # Handle error
                print(result["suggestion"])
        except Exception as e:
            # Handle unexpected error
            pass
    
    Platform Notes:
        
        WINDOWS:
            - [Windows-specific information]
            - [Common Windows issues]
            
        LINUX:
            - [Linux-specific information]
            - [Common Linux issues]
            
        MACOS:
            - [macOS-specific information]
            - [Common macOS issues]
            
        Cross-Platform:
            - [Things that work the same everywhere]
            - [Portable aspects]
    
    Performance:
        - Typical: [Expected performance for normal case]
        - Best case: [Fastest scenario]
        - Worst case: [Slowest scenario]
        - Optimization tips: [How to make it faster]
    
    See Also:
        - [related_tool_1()]: [When to use instead of this tool]
        - [related_tool_2()]: [Tool to get required parameters]
        - [related_tool_3()]: [Alternative approach for same goal]
    
    Version History:
        - v1.0: Initial release
        - v1.1: Added [feature]
        - v2.0: Breaking change - [what changed]
    """
```

---

## Real-World Example: Before and After

### BEFORE (Typical Current State)

This is what most MCP tools look like today:

```python
def search_bookmarks(query, profile_path=None, limit=50):
    """Search bookmarks by title or URL."""
```

**Problems**:
- No indication Firefox must be closed
- No parameter format/examples
- No return structure documented
- No error handling guidance
- No platform differences noted

**Result**: AI tries 3-5 times before success, users frustrated

---

### AFTER (Following This Standard)

```python
def search_bookmarks(query: str, profile_path: Optional[str] = None, limit: int = 50) -> Dict:
    """Search Firefox bookmarks by title/URL (requires Firefox closed).
    
    Performs case-insensitive search across bookmark titles and URLs using
    SQLite FTS5 full-text search. Efficient for large bookmark collections
    (tested with 10,000+ bookmarks). Returns results sorted by relevance.
    
    Prerequisites:
        - Firefox must be completely closed (database will be locked otherwise)
        - Profile must exist and contain places.sqlite database
        - Read permissions on Firefox profile directory
        - Firefox version 57+ (uses FTS5 features)
    
    Args:
        query (str, REQUIRED):
            Search term to find in bookmark titles or URLs
            Case-insensitive, supports partial matches
            Examples: "plex", "github.com", "machine learning tutorial"
            Min length: 1 character
            Special chars: Automatically escaped for SQLite FTS
            
        profile_path (str, OPTIONAL):
            Full absolute path to Firefox profile directory containing places.sqlite
            Format: "C:\\Users\\{username}\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\{profile_id}"
            Example: "C:\\Users\\sandr\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\airiswdq.default-release"
            Default: Auto-detects from profiles.ini (may fail with multiple profiles)
            Get path: Use get_firefox_profiles() tool first
            Platform: Windows requires double backslashes, Linux/Mac use forward slashes
            
        limit (int, OPTIONAL):
            Maximum number of bookmark results to return
            Range: 1-100 (values outside range will be clamped)
            Default: 50
            Performance: <20 is instant, 50-100 may take 1-2 seconds with large databases
    
    Returns:
        dict: Search results with metadata
        
        Structure (Success):
        {
            "status": "success",
            "query": str,               # Echo of search query
            "count": int,               # Number of results found (0 if no matches)
            "profile": str,             # Profile path used
            "results": [                # List of bookmark objects (empty if no matches)
                {
                    "id": int,          # Unique bookmark ID (for other operations)
                    "title": str,       # Bookmark title (may be empty string)
                    "url": str,         # Full URL including protocol
                    "dateAdded": int,   # Unix timestamp in microseconds
                    "lastModified": int,# Unix timestamp in microseconds  
                    "parent": int,      # Parent folder ID (0 = root)
                    "tags": [str]       # List of tags (may be empty)
                }
            ],
            "truncated": bool,          # True if results limited by 'limit' parameter
            "execution_time_ms": float  # Query execution time
        }
        
        Structure (Error):
        {
            "status": "error",
            "error": str,               # Human-readable error message
            "error_code": str,          # Machine-readable error code
            "suggestion": str,          # How to fix the error
            "profile": str              # Profile path attempted (if known)
        }
    
    Common Issues & Solutions:
        
        1. "Failed to connect to database" / "Database is locked"
           CAUSE: Firefox is still running (even in background)
           FIX: Close Firefox completely
           - Windows: Task Manager → Details → End all firefox.exe processes
           - Linux: killall firefox
           - macOS: Activity Monitor → Quit Firefox (check menu bar icon)
           - System tray: Check for hidden Firefox icon
           WORKAROUND: Use export_bookmarks() tool instead (works while Firefox is open)
           
        2. "Profile not found" / "places.sqlite not found"
           CAUSE: Invalid profile path or profile doesn't exist
           FIX: Get correct path first
           - Call get_firefox_profiles() to list available profiles
           - Verify path exists: Check "C:\\Users\\...\\Profiles\\{profile_name}"
           - Check for typos (path is case-sensitive on Linux/Mac)
           - Ensure you're using the correct profile (not "default" but "default-release")
           
        3. "No results found" (count: 0, empty results array)
           CAUSE: Search term doesn't match any bookmarks
           FIX: Try different search strategies
           - Broaden search: "plex" instead of "plex media server"
           - Check spelling and punctuation
           - Try URL domain: "github.com" instead of project name
           - Try partial words: "mach learn" instead of "machine learning"
           - Use list_bookmarks() to browse all bookmarks
           
        4. "Permission denied"
           CAUSE: Insufficient file system permissions
           FIX: Check file permissions
           - Windows: Run as administrator OR right-click places.sqlite → Properties → Security
           - Linux/Mac: chmod 644 places.sqlite OR run with sudo
           - Verify user owns the Firefox profile directory
           - Check OneDrive/Dropbox sync (may cause permission issues)
           
        5. "Timeout" / Slow performance
           CAUSE: Large database or complex search
           FIX: Optimize search
           - Reduce 'limit' parameter (try 20 instead of 100)
           - Use more specific search terms
           - Consider export_bookmarks() + local search for large datasets
    
    Examples:
        
        # Example 1: Basic search with auto-detected profile (most common case)
        # Use when: You have only one Firefox profile and Firefox is closed
        result = search_bookmarks(
            query="plex"
        )
        # Returns: All bookmarks with "plex" in title or URL (up to 50)
        # Use when: Quick search, single profile, Firefox closed
        
        
        # Example 2: Search specific profile with limit (multiple profiles)
        # Use when: You have multiple Firefox profiles or need to specify which one
        result = search_bookmarks(
            query="immich",
            profile_path="C:\\Users\\sandr\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\airiswdq.default-release",
            limit=20
        )
        # Returns: Up to 20 bookmarks matching "immich" from specified profile
        # Use when: Multiple profiles, need specific profile, or auto-detect fails
        
        
        # Example 3: Search by domain name (finding all bookmarks from a site)
        # Use when: You want all bookmarks from a specific website
        result = search_bookmarks(
            query="github.com",
            limit=100
        )
        # Returns: All GitHub bookmarks (up to 100)
        # Use when: Finding all links from a domain, organizing bookmarks
        
        
        # Example 4: Broad search with high limit (comprehensive search)
        # Use when: You want to find everything related to a topic
        result = search_bookmarks(
            query="AI",
            limit=100
        )
        # Returns: All bookmarks with "AI" in title or URL (up to 100)
        # Use when: Research, discovering connections, topic exploration
        
        
        # Example 5: Error handling pattern (production code)
        # Use when: You need robust error handling in production
        try:
            result = search_bookmarks(
                query="machine learning",
                limit=50
            )
            
            if result["status"] == "success":
                if result["count"] == 0:
                    print("No bookmarks found - try broader search terms")
                else:
                    print(f"Found {result['count']} bookmarks:")
                    for bookmark in result["results"]:
                        print(f"  - {bookmark['title']}: {bookmark['url']}")
                    
                    if result["truncated"]:
                        print(f"(showing first {limit}, increase limit for more)")
            else:
                print(f"Error: {result['error']}")
                print(f"Suggestion: {result['suggestion']}")
                
        except Exception as e:
            print(f"Unexpected error: {e}")
            print("Fallback: Try export_bookmarks() tool instead")
        
        
        # Example 6: Linux/Mac path format
        # Use when: Running on Linux or macOS
        result = search_bookmarks(
            query="python",
            profile_path="/home/user/.mozilla/firefox/abc123.default-release"
        )
        # Note: Forward slashes, no drive letter
    
    Platform Notes:
        
        WINDOWS:
            - Profile location: %APPDATA%\\Mozilla\\Firefox\\Profiles\\
            - Full path: C:\\Users\\{username}\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\{profile}
            - Path format: MUST use DOUBLE backslashes "C:\\Users\\..."
            - Check Firefox: Task Manager → Details tab → Look for firefox.exe
            - Common issue: OneDrive may sync profile causing database locks
            
        LINUX:
            - Profile location: ~/.mozilla/firefox/
            - Full path: /home/{user}/.mozilla/firefox/{profile}.{type}
            - Path format: Forward slashes /home/user/...
            - Check Firefox: ps aux | grep firefox
            - Common issue: Snap Firefox uses /home/{user}/snap/firefox/common/.mozilla/
            
        MACOS:
            - Profile location: ~/Library/Application Support/Firefox/Profiles/
            - Full path: /Users/{user}/Library/Application Support/Firefox/Profiles/{profile}
            - Path format: Forward slashes with spaces (use quotes)
            - Check Firefox: Activity Monitor or ps aux | grep firefox
            - Common issue: Firefox may run in background (check menu bar icon)
            
        Cross-Platform:
            - places.sqlite format is identical across platforms
            - Bookmark IDs are consistent across platforms
            - Timestamps are Unix microseconds (same everywhere)
            - Can copy places.sqlite between systems (paths may need adjustment)
    
    Performance:
        - Typical: 10-50ms for database with <1000 bookmarks
        - Large: 100-500ms for database with 10,000+ bookmarks
        - Best case: Instant for simple queries with low limit
        - Worst case: 1-2 seconds for complex queries on large databases
        - Optimization: Use specific search terms, lower limit, close background apps
        - Database size: places.sqlite grows 1MB per ~1000 bookmarks
    
    See Also:
        - get_firefox_profiles(): List available Firefox profiles (use this first)
        - list_bookmarks(): Browse all bookmarks without search (slower but comprehensive)
        - export_bookmarks(): Export to JSON/CSV (works while Firefox is open)
        - find_duplicates(): Find duplicate bookmark URLs
        - get_bookmark_stats(): Get overall bookmark statistics
        - add_bookmark(): Add new bookmarks programmatically
    
    Version History:
        - v1.0 (2024-01): Initial release with basic search
        - v1.1 (2024-03): Added FTS5 support for faster search
        - v1.2 (2024-06): Added tag support in results
        - v2.0 (2024-09): Breaking change - returns dict instead of list
    """
```

**Result**: AI succeeds on first try, users are happy, documentation is reference material

---

## Anti-Patterns to Avoid

### ❌ Don't: Use Placeholder Examples
```python
"""Example: tool(foo="bar", baz=123)"""
```
Nobody's parameter is actually called "foo" or "bar".

### ✅ Do: Use Realistic Examples
```python
"""Example: search_bookmarks(query="plex", limit=20)"""
```

---

### ❌ Don't: Say "Returns results"
```python
"""Returns: Search results"""
```
What structure? What fields?

### ✅ Do: Show the Actual Structure
```python
"""
Returns:
    dict: {
        "count": int,
        "results": [{"id": int, "title": str, "url": str}]
    }
"""
```

---

### ❌ Don't: List Errors Without Solutions
```python
"""
Raises:
    DatabaseError: Database error occurred
    ValueError: Invalid value
"""
```

### ✅ Do: Provide Actionable Solutions
```python
"""
Common Issues:
    1. "Database error" → Close Firefox completely
    2. "Invalid value" → Use get_firefox_profiles() to find valid path
"""
```

---

### ❌ Don't: Assume Users Know Your Tools
```python
"""Args:
    profile: Profile to use
"""
```
How do they get a profile? What format?

### ✅ Do: Guide Users to Prerequisites
```python
"""Args:
    profile_path (str): Full path to profile directory
        Get path: Use get_firefox_profiles() tool first
        Format: "C:\\Users\\{user}\\AppData\\..."
"""
```

---

### ❌ Don't: Use Technical Jargon Without Explanation
```python
"""Uses FTS5 for efficient querying of the places.sqlite relational store."""
```

### ✅ Do: Explain or Link to Resources
```python
"""
Uses Firefox's full-text search (FTS5) for fast searching.
Searches both bookmark titles and URLs efficiently, even
with 10,000+ bookmarks.
"""
```

---

### ❌ Don't: Forget Platform Differences
```python
"""Path: ~/.mozilla/firefox/profile"""
```
That's Linux-only!

### ✅ Do: Document All Platforms
```python
"""
Path:
    - Windows: %APPDATA%\\Mozilla\\Firefox\\Profiles\\
    - Linux: ~/.mozilla/firefox/
    - macOS: ~/Library/Application Support/Firefox/Profiles/
"""
```

---

### ❌ Don't: Write Documentation Once and Never Update
Documentation gets stale fast.

### ✅ Do: Version Your Documentation
```python
"""
Version History:
    - v2.0: Breaking change - returns dict instead of list
    - v1.1: Added tag support
"""
```

---

## Implementation Checklist

Use this checklist when writing or reviewing tool documentation:

### Basic Requirements (Must Have)
- [ ] One-line summary includes critical constraints
- [ ] Prerequisites section lists all requirements
- [ ] Every parameter has type (REQUIRED/OPTIONAL in CAPS)
- [ ] Every parameter has concrete example with realistic value
- [ ] Every optional parameter shows default value
- [ ] Return structure shown with actual field names and types
- [ ] At least 3 realistic examples covering common use cases
- [ ] Common errors documented with actionable solutions

### Good Documentation (Should Have)
- [ ] Parameter format/constraints specified
- [ ] Error responses structure documented
- [ ] Platform differences noted (Windows/Linux/Mac)
- [ ] Performance characteristics mentioned
- [ ] Related tools listed in "See Also"
- [ ] Examples include comments explaining when to use
- [ ] Validation rules for parameters stated

### Excellent Documentation (Nice to Have)
- [ ] Version history included
- [ ] Performance benchmarks provided
- [ ] Error handling example included
- [ ] Edge cases documented
- [ ] Cross-platform example provided
- [ ] Troubleshooting section with FAQs
- [ ] Links to external resources
- [ ] Migration guide for breaking changes

### Documentation Validation
- [ ] Ran tool with each example - all work correctly
- [ ] AI assistant succeeded on first try using only docs
- [ ] No ambiguous terms or unclear requirements
- [ ] No placeholders ("foo", "bar", "example", "test")
- [ ] Formatted consistently with rest of codebase
- [ ] Spell-checked and grammar-checked
- [ ] Reviewed by someone unfamiliar with the tool

---

## Measuring Success

### Key Performance Indicators (KPIs)

Track these metrics to measure documentation quality:

1. **First-Call Success Rate**: % of times AI gets it right on first attempt
   - Target: >90%
   - Measure: Log successful vs failed first attempts

2. **Average Attempts to Success**: How many tries before success
   - Target: <1.2 (20% need retry)
   - Measure: Count API calls per successful operation

3. **Documentation Issue Reports**: Users reporting "how do I...?"
   - Target: <1 per 1000 tool calls
   - Measure: Support tickets and forum questions

4. **Token Efficiency**: Tokens used vs optimal usage
   - Target: <1.5x optimal
   - Measure: Actual tokens / minimum required tokens

### Quick Self-Assessment

Answer these questions honestly:

1. Can an AI assistant use your tool successfully on the FIRST try using only the docstring?
2. Can you copy-paste an example from your docs and have it work immediately?
3. If there's an error, does your documentation tell the user exactly how to fix it?
4. Would you be comfortable having no other documentation than the docstring?
5. Could someone from a different platform (Windows/Linux/Mac) use your tool?

**If you answered "no" to any question, your documentation needs improvement.**

### A/B Testing Framework

Compare documentation quality experimentally:

```python
# Test Group A: Old documentation (one-liner)
# Test Group B: New documentation (this standard)

# Measure over 100 tool calls each:
# - First-call success rate
# - Average attempts to success  
# - User satisfaction rating
# - Support ticket volume

# Expected improvements with new docs:
# - First-call success: 50% → 90% (80% improvement)
# - Avg attempts: 2.5 → 1.1 (56% reduction)
# - User satisfaction: 3.2/5 → 4.5/5 (41% improvement)
# - Support tickets: 5/100 → 0.5/100 (90% reduction)
```

---

## Quick Reference Guide

### Minimum Viable Documentation (5 minutes)

If you only have 5 minutes, add these:

1. **Constraint in summary**: "Search bookmarks (Firefox must be closed)"
2. **Mark REQUIRED params**: `query (str, REQUIRED)`
3. **One realistic example**: `search_bookmarks(query="plex")`
4. **Top error with fix**: "Database locked → Close Firefox"
5. **Return structure basics**: `{"count": int, "results": [...]}`

**Impact**: ~50% → ~70% first-call success rate

---

### Standard Documentation (15 minutes)

For complete documentation, add:

1. Everything from "Minimum Viable" above
2. All parameters with format and examples
3. 3 realistic examples covering common cases
4. Top 3 errors with solutions
5. Complete return structure with field descriptions
6. Platform notes if applicable

**Impact**: ~70% → ~90% first-call success rate

---

### Gold Standard Documentation (30 minutes)

For best-in-class documentation, add:

1. Everything from "Standard" above
2. Prerequisites section
3. Performance characteristics
4. 5+ examples including error handling
5. All common errors with solutions
6. Platform-specific sections
7. See Also with related tools
8. Version history

**Impact**: ~90% → ~95% first-call success rate + happy users

---

## Community Resources

### For MCP Server Developers

- **FastMCP Documentation**: https://github.com/jlowin/fastmcp
- **MCP Protocol Spec**: https://modelcontextprotocol.io
- **Glama.ai MCP Servers**: https://glama.ai/mcp/servers
- **MCP Community Discord**: [Link to community]

### Templates and Tools

- **Documentation Template** (above): Copy-paste ready
- **Documentation Linter**: [Tool to validate docs against this standard]
- **Example MCP Servers**: [List of well-documented examples]

### Getting Help

- **Questions**: Post in MCP community forums
- **Suggestions**: Open issues on this document's repo
- **Contributions**: PRs welcome to improve this standard

---

## Call to Action

### For Tool Authors

1. **Audit your existing tools**: Which have inadequate docstrings?
2. **Start with high-traffic tools**: Fix the ones Claude uses most
3. **Measure improvement**: Track first-call success rate before/after
4. **Share your learnings**: Help other developers avoid the same mistakes

### For the MCP Community

1. **Adopt this standard**: Make it part of MCP best practices
2. **Create tooling**: Build linters and validators
3. **Reward good documentation**: Feature well-documented servers on Glama.ai
4. **Share examples**: Build a library of exemplary tool documentation

### For Framework Maintainers

1. **Integrate into FastMCP**: Make this template the default
2. **Add validation**: Lint docstrings at build time
3. **Generate from docs**: Auto-create OpenAPI/JSON schemas from docstrings
4. **Provide templates**: IDE snippets for quick documentation

---

## Conclusion

**The Bottom Line**: Good documentation is not optional - it's the difference between an AI assistant that looks brilliant and one that looks incompetent.

**The ROI**: 15-30 minutes per tool saves 10-50 hours of user frustration.

**The Standard**: If your tool documentation doesn't enable first-call success, it's not done.

**The Call**: Let's make all MCP tools as easy to use as they are powerful.

---

## Document History

- **v1.0** (2025-10-10): Initial publication
- **Author**: MCP Community
- **License**: CC0 (Public Domain)
- **Contributing**: PRs welcome at [repo link]

---

*"Documentation is a love letter that you write to your future self." - Damian Conway*

*"The best interface is no interface - but the second best is a well-documented one." - Adapted from Golden Krishna*
