# MCP Prompt Templates vs Docstrings
## Managing Duplication in MCPB Packages

**Problem**: When you package an MCP server with `mcpb pack`, you can include prompt templates that duplicate your docstrings, creating maintenance burden.

**Solution**: Strategic approach to minimize duplication while maximizing Claude's success rate.

---

## The Duplication Challenge

### What You Have to Maintain

1. **Python Docstring** (in your code)
   ```python
   def search_bookmarks(query: str, profile_path: Optional[str] = None):
       """Search Firefox bookmarks by title/URL (requires Firefox closed).
       
       Args:
           query (str, REQUIRED): Search term...
           profile_path (str, OPTIONAL): Full path...
       ...
       """
   ```

2. **Prompt Template** (in mcpb package)
   ```
   # prompts/search_bookmarks.md
   When using the search_bookmarks tool:
   - Always close Firefox first
   - Use get_firefox_profiles() to find the path
   - Examples: search_bookmarks(query="plex", limit=20)
   ```

**Duplication Risk**: Change docstring but forget prompt template = inconsistent behavior

---

## Three Approaches to This Problem

### Approach 1: Docstring Only (Minimal Duplication)

**When to use**: Simple tools, low token budget, minimal confusion risk

**Strategy**:
- Write comprehensive docstrings (following the standard)
- No separate prompt template
- MCP framework shows docstring to Claude

**Pros**:
- ✅ Single source of truth
- ✅ No sync issues
- ✅ Less maintenance

**Cons**:
- ❌ Docstrings optimized for humans, not LLMs
- ❌ May include dev-specific details Claude doesn't need
- ❌ Can't optimize token usage

**Example Package Structure**:
```
my-mcp-server/
├── src/
│   └── tools.py  # Comprehensive docstrings
├── mcp.json      # No prompt templates
└── README.md
```

---

### Approach 2: Prompt Template + Minimal Docstring (LLM-First)

**When to use**: Complex tools, high token budget, Claude is primary consumer

**Strategy**:
- Minimal docstring (for IDE/developers)
- Comprehensive prompt template (for Claude)
- Prompt template is the primary documentation

**Pros**:
- ✅ Optimized for LLM consumption
- ✅ Can be more conversational
- ✅ Token-optimized
- ✅ Can include LLM-specific guidance

**Cons**:
- ❌ Developers get less help in IDE
- ❌ Prompt template not visible in code
- ❌ Still duplication (but reversed priority)

**Example Package Structure**:
```
my-mcp-server/
├── src/
│   └── tools.py        # Minimal docstrings
├── prompts/
│   ├── search_bookmarks.md
│   └── list_bookmarks.md
├── mcp.json            # References prompts/
└── README.md
```

---

### Approach 3: Hybrid with Generation (Best of Both Worlds)

**When to use**: Professional MCP servers, automation-friendly workflow

**Strategy**:
- Write ONE comprehensive source (markdown or JSON)
- Auto-generate BOTH docstring and prompt template
- Build script keeps them in sync

**Pros**:
- ✅ Single source of truth
- ✅ Optimized for both humans and LLMs
- ✅ No sync issues
- ✅ Can optimize each output format

**Cons**:
- ❌ Requires build tooling
- ❌ More complex workflow
- ❌ Initial setup overhead

**Example Package Structure**:
```
my-mcp-server/
├── docs/
│   └── tools.yaml           # Single source of truth
├── src/
│   └── tools.py             # GENERATED docstrings
├── prompts/
│   └── search_bookmarks.md  # GENERATED from docs/
├── scripts/
│   └── generate_docs.py     # Generation script
├── mcp.json
└── README.md
```

---

## Recommended: Approach 3 with YAML Source

### Single Source of Truth Format

```yaml
# docs/tools/search_bookmarks.yaml
name: search_bookmarks
category: firefox
summary: Search Firefox bookmarks by title/URL (requires Firefox closed)

prerequisites:
  - Firefox must be completely closed
  - Profile must exist with places.sqlite
  - Read permissions on profile directory

parameters:
  - name: query
    type: string
    required: true
    description: Search term to find in titles/URLs
    format: Case-insensitive partial match
    examples:
      - "plex"
      - "github.com"
      - "machine learning"
    
  - name: profile_path
    type: string
    required: false
    default: Auto-detect from profiles.ini
    description: Full path to Firefox profile directory
    format: "C:\\Users\\{user}\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\{profile}"
    examples:
      - "C:\\Users\\sandr\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\airiswdq.default-release"
    get_value_from: get_firefox_profiles()
    
  - name: limit
    type: integer
    required: false
    default: 50
    range: [1, 100]
    description: Maximum results to return

returns:
  success:
    status: success
    query: str
    count: int
    results:
      - id: int
        title: str
        url: str
        dateAdded: int
        parent: int
  error:
    status: error
    error: str
    suggestion: str

errors:
  - condition: "Database is locked"
    cause: Firefox is running
    fix: Close Firefox completely (check Task Manager)
    workaround: Use export_bookmarks() instead
    
  - condition: "Profile not found"
    cause: Invalid path or doesn't exist
    fix: Use get_firefox_profiles() to find path
    check: Verify places.sqlite exists

examples:
  - name: Basic search (most common)
    when: Single profile, Firefox closed
    code: |
      search_bookmarks(query="plex")
    returns: Up to 50 bookmarks matching "plex"
    
  - name: Specific profile
    when: Multiple profiles or auto-detect fails
    code: |
      search_bookmarks(
          query="immich",
          profile_path="C:\\Users\\sandr\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\airiswdq.default-release",
          limit=20
      )
    returns: Up to 20 bookmarks from specified profile

platforms:
  windows:
    location: "%APPDATA%\\Mozilla\\Firefox\\Profiles\\"
    format: Double backslashes "C:\\Users\\..."
    check_process: Task Manager → firefox.exe
    
  linux:
    location: "~/.mozilla/firefox/"
    format: Forward slashes "/home/user/..."
    check_process: ps aux | grep firefox
    
  macos:
    location: "~/Library/Application Support/Firefox/Profiles/"
    format: Forward slashes (with spaces)
    check_process: Activity Monitor

see_also:
  - get_firefox_profiles: Find available profiles (use first)
  - list_bookmarks: Browse all bookmarks
  - export_bookmarks: Export while Firefox open
```

---

### Generation Script

```python
# scripts/generate_docs.py
import yaml
from pathlib import Path
from jinja2 import Template

def generate_docstring(tool_spec):
    """Generate Python docstring from YAML spec"""
    template = Template('''"""{{ summary }}
    
    {{ description }}
    
    Prerequisites:
    {% for prereq in prerequisites %}    - {{ prereq }}
    {% endfor %}
    
    Args:
    {% for param in parameters %}    {{ param.name }} ({{ param.type }}, {{ 'REQUIRED' if param.required else 'OPTIONAL' }}):
            {{ param.description }}
            {% if param.format %}Format: {{ param.format }}{% endif %}
            {% if param.examples %}Examples: {{ param.examples|join(', ') }}{% endif %}
            {% if not param.required %}Default: {{ param.default }}{% endif %}
            {% if param.get_value_from %}Get value: {{ param.get_value_from }}{% endif %}
            
    {% endfor %}
    Returns:
        dict: {{ returns.success.status }}
        
        Structure (Success):
        {{ returns.success|format_structure }}
        
        Structure (Error):
        {{ returns.error|format_structure }}
    
    Common Issues:
    {% for error in errors %}    {{ loop.index }}. "{{ error.condition }}"
           CAUSE: {{ error.cause }}
           FIX: {{ error.fix }}
           {% if error.workaround %}WORKAROUND: {{ error.workaround }}{% endif %}
           
    {% endfor %}
    Examples:
    {% for example in examples %}    # {{ example.name }}
        # Use when: {{ example.when }}
        {{ example.code }}
        # Returns: {{ example.returns }}
        
    {% endfor %}
    Platform Notes:
    {% for platform, details in platforms.items %}    {{ platform.upper() }}:
            - Location: {{ details.location }}
            - Format: {{ details.format }}
            - Check: {{ details.check_process }}
            
    {% endfor %}
    See Also:
    {% for tool, desc in see_also.items %}    - {{ tool }}(): {{ desc }}
    {% endfor %}"""''')
    
    return template.render(**tool_spec)

def generate_prompt_template(tool_spec):
    """Generate Claude prompt template from YAML spec"""
    template = Template('''# {{ name }} Tool Guide

## Quick Summary
{{ summary }}

**CRITICAL**: {% for prereq in prerequisites %}{{ prereq }}{% if not loop.last %}, {% endif %}{% endfor %}

## How to Use

### Parameters
{% for param in parameters %}
**{{ param.name }}** ({{ 'REQUIRED' if param.required else 'OPTIONAL' }})
- What: {{ param.description }}
- {% if param.examples %}Example: `{{ param.examples[0] }}`{% endif %}
- {% if not param.required %}Default: {{ param.default }}{% endif %}
{% if param.get_value_from %}- Get from: {{ param.get_value_from }}{% endif %}

{% endfor %}

### Common Patterns

{% for example in examples %}
**{{ example.name }}**
```python
{{ example.code }}
```
Use when: {{ example.when }}

{% endfor %}

### When Things Go Wrong

{% for error in errors %}
**Problem**: {{ error.condition }}
- Why: {{ error.cause }}
- Fix: {{ error.fix }}
{% if error.workaround %}- Alternative: {{ error.workaround }}{% endif %}

{% endfor %}

### Platform Differences

{% for platform, details in platforms.items %}
**{{ platform.title() }}**: {{ details.location }}
- Check if closed: {{ details.check_process }}
{% endfor %}

### Related Tools
{% for tool, desc in see_also.items %}
- `{{ tool }}()` - {{ desc }}
{% endfor %}
''')
    
    return template.render(**tool_spec)

def generate_all():
    """Generate all documentation from YAML sources"""
    docs_dir = Path("docs/tools")
    
    for yaml_file in docs_dir.glob("*.yaml"):
        with open(yaml_file) as f:
            spec = yaml.safe_load(f)
        
        # Generate docstring (for insertion into Python code)
        docstring = generate_docstring(spec)
        output_file = Path("generated/docstrings") / f"{spec['name']}.txt"
        output_file.parent.mkdir(exist_ok=True)
        output_file.write_text(docstring)
        
        # Generate prompt template (for mcpb package)
        prompt = generate_prompt_template(spec)
        prompt_file = Path("prompts") / f"{spec['name']}.md"
        prompt_file.parent.mkdir(exist_ok=True)
        prompt_file.write_text(prompt)
        
        print(f"✅ Generated docs for {spec['name']}")

if __name__ == "__main__":
    generate_all()
```

---

### Workflow Integration

```toml
# pyproject.toml
[tool.mcp]
generate_docs = "scripts/generate_docs.py"

[tool.mcp.build]
pre_build = ["python scripts/generate_docs.py"]
```

```bash
# Build workflow
python scripts/generate_docs.py  # Generate docstrings + prompt templates
mcpb validate                     # Validate package
mcpb pack                        # Package with generated prompts
```

---

## Prompt Template Best Practices

### What to Include in Prompt Templates (That Docstrings Don't Need)

1. **Conversational Tone**
   ```markdown
   # search_bookmarks Tool
   
   This tool helps you find bookmarks in Firefox. Before using it,
   **make sure Firefox is completely closed** - otherwise the database
   will be locked and the search will fail.
   ```

2. **Common User Mistakes**
   ```markdown
   ## Common Mistakes to Avoid
   
   ❌ Don't use this while Firefox is running
   ❌ Don't use relative paths for profile_path
   ❌ Don't forget to call get_firefox_profiles() first
   
   ✅ Close Firefox completely
   ✅ Use full absolute paths
   ✅ Get profile path from get_firefox_profiles()
   ```

3. **Decision Trees**
   ```markdown
   ## When to Use This Tool
   
   Use search_bookmarks() when:
   - You know what you're looking for (have search term)
   - Firefox is closed
   - You want fast, targeted results
   
   Use list_bookmarks() instead when:
   - You want to browse all bookmarks
   - You don't know what you're searching for
   - You want folder structure
   ```

4. **LLM-Specific Guidance**
   ```markdown
   ## For AI Assistants
   
   Before calling this tool:
   1. Check if Firefox is mentioned as running in conversation
   2. If user has multiple profiles, call get_firefox_profiles() first
   3. If this fails with "locked", suggest export_bookmarks() alternative
   
   After calling:
   - If count is 0, suggest broader search terms
   - If count is high, offer to filter results
   - Always show at least title and URL for each result
   ```

---

## Token Optimization

### Docstring vs Prompt Template Token Usage

**Full Docstring** (comprehensive): ~500-1000 tokens per tool
**Prompt Template** (optimized): ~200-400 tokens per tool

### Optimization Strategies

1. **Use References Instead of Repetition**
   ```markdown
   # Instead of repeating full structure:
   Returns the same structure as list_bookmarks() but filtered by query.
   See list_bookmarks documentation for full return structure.
   ```

2. **Common Errors Document**
   ```markdown
   # Create shared errors.md
   All Firefox tools may encounter these errors: [see errors.md]
   
   Tool-specific errors:
   - "No results found" → Try broader search terms
   ```

3. **Platform Notes Once**
   ```markdown
   # Share platform.md across all Firefox tools
   Firefox Profile Locations: [see platform.md]
   ```

4. **Conditional Inclusion**
   ```json
   // mcp.json
   {
     "prompts": {
       "search_bookmarks": {
         "file": "prompts/search_bookmarks.md",
         "include_shared": ["firefox_common", "platform_notes"]
       }
     }
   }
   ```

---

## Recommended Structure for MCP Packages

```
my-firefox-mcp/
├── src/
│   └── tools.py                # Minimal docstrings
├── docs/
│   ├── tools/
│   │   ├── search_bookmarks.yaml
│   │   ├── list_bookmarks.yaml
│   │   └── get_firefox_profiles.yaml
│   └── shared/
│       ├── firefox_common.md   # Shared concepts
│       ├── platform.md         # Platform differences
│       └── errors.md           # Common errors
├── prompts/                    # GENERATED
│   ├── search_bookmarks.md
│   └── list_bookmarks.md
├── generated/                  # GENERATED
│   └── docstrings/
│       └── search_bookmarks.txt
├── scripts/
│   └── generate_docs.py
├── mcp.json
└── README.md
```

---

## Practical Example: Your dbops Server

### Current State (Duplication Hell)
```python
# In Python code
def search_bookmarks(query, profile_path=None, limit=50):
    """Search bookmarks by title or URL."""  # ❌ Inadequate
```

```markdown
# In prompts/search_bookmarks.md (if it existed)
When searching Firefox bookmarks:
- Close Firefox first
- Use get_firefox_profiles() to find path
- Example: search_bookmarks(query="plex")
```

**Problem**: Two places to update, easily get out of sync

---

### Recommended Approach

```yaml
# docs/tools/search_bookmarks.yaml (SINGLE SOURCE)
name: search_bookmarks
category: firefox
summary: Search Firefox bookmarks (requires Firefox closed)
# ... full spec as shown above
```

```python
# scripts/generate_docs.py
# Generates both:
# - src/tools.py docstring
# - prompts/search_bookmarks.md
```

```bash
# Build command
python scripts/generate_docs.py && mcpb pack
```

**Benefit**: Change YAML once, both outputs updated automatically

---

## Migration Path

### Step 1: Audit Current State (5 min)
```bash
# Count your duplication
grep -r "def.*(" src/ | wc -l        # Python functions
find prompts/ -name "*.md" | wc -l   # Prompt templates
# If prompt_count > 0: You have duplication
```

### Step 2: Choose Approach (5 min)
- Simple server (<10 tools): Approach 1 (docstring only)
- Medium server (10-30 tools): Approach 2 (prompt template primary)
- Complex server (>30 tools): Approach 3 (generated)

### Step 3: Implement (varies)
- Approach 1: Enhance docstrings, remove prompt templates
- Approach 2: Write comprehensive prompt templates, minimal docstrings
- Approach 3: Create YAML specs, write generation script

### Step 4: Automate (1 hour)
```python
# Add pre-commit hook
# .git/hooks/pre-commit
#!/bin/bash
python scripts/generate_docs.py
git add generated/ prompts/
```

---

## Conclusion

**The Duplication Dilemma**: Docstrings vs prompt templates

**The Solution**: 
- Small servers: Comprehensive docstrings only
- Large servers: Single source YAML → generate both
- All servers: Never manually maintain both!

**The Tools**:
- YAML for canonical source
- Jinja2 for generation
- Pre-commit hooks for automation
- mcpb for packaging

**The Result**: Claude succeeds on first try, developers get great IDE support, no sync issues.

---

## References

- **MCPB Documentation**: https://github.com/anthropics/mcpb
- **MCP Prompt Templates**: [Link to official docs]
- **FastMCP Guide**: https://github.com/jlowin/fastmcp
- **This Document**: Part of MCP Tool Documentation Standards v1.0
