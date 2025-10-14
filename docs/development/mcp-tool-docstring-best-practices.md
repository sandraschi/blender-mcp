# MCP Tool Documentation Best Practices
## How to Make Tools "Claude-Proof"

*Problem: Claude flails when tool docstrings are inadequate, making users think Claude is a "dumbnik"*

---

## The Golden Rule
**Your docstring should let Claude succeed on the FIRST try, not after 5 failed attempts.**

---

## Required Elements

### 1. One-Line Summary
Clear, specific purpose statement.

❌ BAD: "Search bookmarks by title or URL."
✅ GOOD: "Search Firefox bookmarks by title/URL (requires Firefox closed)."

### 2. Prerequisites Section
What must be true BEFORE calling this tool?

```python
"""
Prerequisites:
    - Firefox must be completely closed (check system tray)
    - Profile path must exist and be readable
    - Database must not be locked by another process
"""
```

### 3. Parameters with Examples
Every parameter needs:
- Type (REQUIRED or OPTIONAL in caps)
- Purpose
- Format/constraints
- Concrete example with realistic values
- Default value if optional

```python
"""
Args:
    query (str, REQUIRED): 
        Search term for bookmark titles/URLs
        Examples: "plex", "immich", "python tutorial"
        
    profile_path (str, OPTIONAL): 
        Full path to Firefox profile directory
        Format: "C:\\Users\\{username}\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\{profile}"
        Example: "C:\\Users\\sandr\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\airiswdq.default-release"
        Default: Auto-detects default profile using profiles.ini
        
    limit (int, OPTIONAL):
        Maximum results to return
        Range: 1-100
        Default: 50
"""
```

### 4. Return Format
Show the ACTUAL structure, not abstract description.

❌ BAD: "Returns search results"
✅ GOOD:
```python
"""
Returns:
    dict: {
        "status": "success" | "error",
        "query": str,              # echoed search query
        "count": int,              # number of results found
        "results": [               # list of bookmark objects
            {
                "id": int,         # bookmark ID
                "title": str,      # bookmark title
                "url": str,        # full URL
                "dateAdded": int,  # Unix timestamp microseconds
                "parent": int      # parent folder ID
            }
        ]
    }
"""
```

### 5. Common Errors with Solutions
Don't just list errors - tell Claude how to FIX them!

```python
"""
Common Issues:
    1. "Failed to connect to database"
       → Firefox is still running. Close it completely (check system tray)
       → Alternative: Use export_bookmarks() if you need access while Firefox is open
       
    2. "Profile not found" 
       → Use get_firefox_profiles() to find the correct path
       → Check that path uses double backslashes on Windows
       
    3. "Permission denied"
       → Run as administrator if profile is in protected directory
       → Check that places.sqlite file exists and is readable
"""
```

### 6. Complete Working Examples
Show REAL calls that actually work, not placeholder examples.

❌ BAD:
```python
"""
Example:
    search_bookmarks("search_term")
"""
```

✅ GOOD:
```python
"""
Examples:
    # Basic search (auto-detect profile) - simplest case
    result = search_bookmarks(
        query="plex",
        limit=20
    )
    
    # Search specific profile - when multiple profiles exist
    result = search_bookmarks(
        query="immich",
        profile_path="C:\\Users\\sandr\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\airiswdq.default-release",
        limit=50
    )
    
    # Case-sensitive exact match - for finding specific titles
    result = search_bookmarks(
        query="Plex Media Server",
        limit=10
    )
"""
```

### 7. Platform-Specific Notes
Windows/Linux/Mac differences matter!

```python
"""
Platform Notes:
    Windows: 
        - Use double backslashes in paths: "C:\\Users\\..."
        - Profile location: %APPDATA%\\Mozilla\\Firefox\\Profiles
        - Check Task Manager for running Firefox processes
        
    Linux:
        - Profile location: ~/.mozilla/firefox/
        - Use forward slashes: "/home/user/.mozilla/..."
        
    macOS:
        - Profile location: ~/Library/Application Support/Firefox/Profiles/
        - Firefox may run in background - check Activity Monitor
"""
```

---

## Anti-Patterns (What NOT to Do)

### ❌ Vague Descriptions
"Search for items" - what items? where? how?

### ❌ Missing Parameter Types
Is it required? Optional? What's the default?

### ❌ No Examples
Claude shouldn't have to guess the format

### ❌ Abstract Return Types
"Returns results" - what structure? what fields?

### ❌ No Error Guidance
"May throw errors" - which ones? how to fix?

### ❌ Assuming Context
"Use the profile path" - from where? how do I get it?

---

## Template for New Tools

```python
def tool_name(param1: str, param2: Optional[int] = None) -> Dict:
    """[One-line summary with key constraint]
    
    [Longer description if needed - WHY use this tool vs alternatives]
    
    Prerequisites:
        - [What must be true before calling]
        - [External state requirements]
    
    Args:
        param1 (str, REQUIRED):
            [Purpose and meaning]
            Format: [constraints/pattern]
            Example: [realistic example]
            
        param2 (int, OPTIONAL):
            [Purpose and meaning]
            Range: [min-max if applicable]
            Default: [default value]
            Example: [realistic example]
    
    Returns:
        [type]: {
            "field1": type,  # description
            "field2": type,  # description
            ...
        }
    
    Raises/Errors:
        - [Error condition] → [How to fix it]
        - [Error condition] → [How to fix it]
    
    Examples:
        # [Use case 1 - simplest/most common]
        result = tool_name(
            param1="realistic_value"
        )
        
        # [Use case 2 - with optional params]
        result = tool_name(
            param1="realistic_value",
            param2=42
        )
        
        # [Use case 3 - advanced/edge case]
        result = tool_name(
            param1="special_case_value",
            param2=100
        )
    
    Platform Notes:
        Windows: [Windows-specific info]
        Linux: [Linux-specific info]
        macOS: [macOS-specific info]
    
    See Also:
        - [Related tool for alternative approach]
        - [Tool to get required parameters]
    """
```

---

## Checklist for Tool Authors

Before releasing a tool, verify:

- [ ] One-line summary is specific and mentions key constraints
- [ ] All prerequisites explicitly stated
- [ ] Every parameter has: type, REQUIRED/OPTIONAL, format, example, default
- [ ] Return structure shown with actual field names and types
- [ ] At least 3 realistic examples covering common use cases
- [ ] Common errors documented with solutions (not just error names)
- [ ] Platform-specific differences noted if applicable
- [ ] Related tools mentioned for discovery
- [ ] No jargon without explanation
- [ ] No assumptions about user's prior knowledge

---

## Impact Metrics

Good documentation should achieve:
- **First-call success rate > 90%** (Claude gets it right on first try)
- **Zero "how do I get X?" questions** (all inputs explained)
- **Self-service error resolution** (users can fix issues without asking)

Bad documentation symptoms:
- Claude tries multiple wrong approaches before success
- Users ask "how do I find the X parameter?"
- Repeated failed calls with slightly different arguments
- Claude apologizes multiple times in same conversation

---

## For MCP Server Developers

### Quick Wins
1. Add concrete examples to EVERY tool
2. Mark parameters as REQUIRED or OPTIONAL explicitly
3. Document return structure (not just type)
4. List common errors with fixes

### Medium Effort
5. Add platform-specific notes
6. Create "getting started" flow showing related tools
7. Add prerequisites section
8. Show realistic example values (not "foo", "bar", "baz")

### High Impact
9. Test documentation with actual Claude sessions
10. Measure first-call success rate
11. Add "See Also" sections for tool discovery
12. Create visual diagrams for complex tool chains

---

## Example: Before and After

### BEFORE (Typical Current State)
```python
def search_bookmarks(query, profile_path=None, limit=50):
    """Search bookmarks by title or URL."""
```

**Result**: Claude flails, tries wrong parameters, apologizes, tries again

### AFTER (Best Practice)
```python
def search_bookmarks(query: str, profile_path: Optional[str] = None, limit: int = 50):
    """Search Firefox bookmarks by title/URL (requires Firefox closed).
    
    Searches through Firefox bookmarks database for matching titles or URLs.
    Uses SQLite FTS for fast searching across large bookmark collections.
    
    Prerequisites:
        - Firefox must be completely closed (check system tray)
        - places.sqlite must be readable (not locked)
    
    Args:
        query (str, REQUIRED):
            Search term to find in bookmark titles/URLs
            Case-insensitive, matches partial strings
            Examples: "plex", "github.com", "machine learning"
            
        profile_path (str, OPTIONAL):
            Full path to Firefox profile directory containing places.sqlite
            Format: "C:\\Users\\{user}\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\{profile}"
            Example: "C:\\Users\\sandr\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\airiswdq.default-release"
            Default: Auto-detects from profiles.ini (may fail with multiple profiles)
            Get path using: get_firefox_profiles()
            
        limit (int, OPTIONAL):
            Maximum number of results to return
            Range: 1-100
            Default: 50
    
    Returns:
        dict: {
            "status": "success" | "error",
            "query": str,              # echoed search query
            "count": int,              # number of results found  
            "results": [               # list of bookmark objects
                {
                    "id": int,         # unique bookmark ID
                    "title": str,      # bookmark title
                    "url": str,        # full URL
                    "dateAdded": int,  # Unix timestamp (microseconds)
                    "lastModified": int, # Unix timestamp (microseconds)
                    "parent": int      # parent folder ID
                }
            ]
        }
    
    Common Issues:
        1. "Failed to connect to database"
           → Close Firefox completely (check system tray for running processes)
           → On Windows: Check Task Manager for firefox.exe
           → Alternative: export_bookmarks() works with Firefox open
           
        2. "Profile not found"
           → Use get_firefox_profiles() to find correct path
           → Ensure path uses double backslashes on Windows
           → Check that places.sqlite exists at that location
           
        3. No results found
           → Search is case-insensitive but requires partial match
           → Try broader search terms
           → Use list_bookmarks() to browse all bookmarks
    
    Examples:
        # Basic search - auto-detect profile (most common use case)
        result = search_bookmarks(
            query="plex",
            limit=20
        )
        
        # Specific profile - when multiple profiles exist
        result = search_bookmarks(
            query="immich",
            profile_path="C:\\Users\\sandr\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\airiswdq.default-release",
            limit=50
        )
        
        # Search by domain
        result = search_bookmarks(
            query="github.com",
            limit=100
        )
    
    Platform Notes:
        Windows:
            - Profile: %APPDATA%\\Mozilla\\Firefox\\Profiles\\
            - Use double backslashes in paths
            - Check Task Manager for firefox.exe
            
        Linux:
            - Profile: ~/.mozilla/firefox/
            - Use forward slashes in paths
            
        macOS:
            - Profile: ~/Library/Application Support/Firefox/Profiles/
            - Firefox may run in background (check Activity Monitor)
    
    See Also:
        - get_firefox_profiles(): Find available Firefox profiles
        - list_bookmarks(): Browse all bookmarks without search
        - export_bookmarks(): Export to JSON/CSV (works with Firefox open)
        - find_duplicates(): Find duplicate bookmark URLs
    """
```

**Result**: Claude gets it right on first try, users are happy

---

## Call to Action

If you're developing MCP servers:
1. **Audit your existing tools** - which have inadequate docstrings?
2. **Start with high-traffic tools** - fix the ones Claude uses most
3. **Measure improvement** - track first-call success rate
4. **Share your learnings** - help other developers avoid the same mistakes

**Remember**: Every hour spent on documentation saves 100 hours of user frustration.

---

*"Good documentation is like good code - it should be obvious, not clever."*
