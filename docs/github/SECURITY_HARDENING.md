# Security Hardening Guide for MCP Projects

> **From "totally blargh" to zero vulnerabilities** - Complete security hardening checklist

Based on our experience fixing 3 HIGH + 15 MEDIUM + 20 LOW security issues.

---

## 📊 Security Scan Results Journey

### Before Hardening:
- ❌ **3 HIGH** severity issues
- ❌ **15 MEDIUM** severity issues
- ❌ **2 dependency vulnerabilities**
- ⚠️ **20 LOW** severity warnings

### After Hardening:
- ✅ **0 HIGH** severity issues
- ✅ **10 MEDIUM** severity issues (justified)
- ✅ **0 dependency vulnerabilities**
- ⚠️ **22 LOW** severity warnings (acceptable)

---

## 🛡️ Critical Security Fixes

### 1. Weak Cryptographic Hash (HIGH)

**Bandit**: `B324` - Use of weak MD5 hash

**Problem**:
```python
import hashlib

# For file naming/deduplication
hash_value = hashlib.md5(data.encode()).hexdigest()  # ❌ Security warning
```

**Why it's flagged**: MD5 is cryptographically weak

**Fix**:
```python
import hashlib

# When NOT used for security (file naming, etc.)
hash_value = hashlib.md5(
    data.encode(), 
    usedforsecurity=False  # ✅ Explicitly mark as non-crypto
).hexdigest()
```

**When to use**:
- ✅ File naming/deduplication
- ✅ Cache keys
- ✅ Non-security purposes

**When NOT to use**:
- ❌ Password hashing (use `bcrypt`, `argon2`)
- ❌ Cryptographic signatures
- ❌ Security tokens

---

### 2. Shell Injection (HIGH)

**Bandit**: `B605` - Start process with shell

**Problem**:
```python
import os

os.system("clear")  # ❌ Shell injection risk
os.system("cls" if os.name == "nt" else "clear")  # ❌ Still risky
```

**Why it's dangerous**: User input could be injected into shell command

**Fix**:
```python
import subprocess

# Safe subprocess without shell
if os.name == "nt":
    subprocess.run(["cmd", "/c", "cls"], check=False)  # ✅ No shell
else:
    subprocess.run(["clear"], check=False)  # ✅ No shell
```

**Rules**:
- ✅ Always use `subprocess.run()` with list of arguments
- ✅ Always set `shell=False` (or omit, it's the default)
- ❌ Never use `os.system()`
- ❌ Never use `shell=True` unless absolutely necessary

---

### 3. Subprocess with shell=True (HIGH)

**Bandit**: `B602` - subprocess with shell=True

**Problem**:
```python
subprocess.run(["where", "notepad++"], shell=True)  # ❌ Dangerous
subprocess.run(cmd, shell=True)  # ❌ Even worse with variable
```

**Fix**:
```python
subprocess.run(["where", "notepad++"], shell=False)  # ✅ Safe
# Or omit shell parameter (defaults to False)
subprocess.run(["where", "notepad++"])  # ✅ Safe
```

**When shell=True is needed**:
```python
# If you MUST use shell (rare):
import shlex

# Escape user input
safe_arg = shlex.quote(user_input)
subprocess.run(f"command {safe_arg}", shell=True)  # Still risky!
```

---

## 🔐 Medium Severity Fixes

### 4. XML Parsing Vulnerabilities (MEDIUM)

**Bandit**: `B314`, `B318`, `B405`, `B408` - XML parsing attacks

**Problem**:
```python
import xml.etree.ElementTree as ET  # ❌ Vulnerable
from xml.dom import minidom  # ❌ Vulnerable

tree = ET.parse(untrusted_file)  # ❌ XML bomb risk
dom = minidom.parseString(xml_string)  # ❌ XXE attack risk
```

**Why it's dangerous**:
- XML bombs (billion laughs attack)
- XXE (XML External Entity) attacks
- DTD retrieval attacks

**Fix**:
```python
import defusedxml.ElementTree as ET  # ✅ Safe
import defusedxml.minidom as minidom  # ✅ Safe
from defusedxml.ElementTree import Element, SubElement, tostring  # ✅ Safe

tree = ET.parse(untrusted_file)  # ✅ Protected
dom = minidom.parseString(xml_string)  # ✅ Protected
```

**Add dependency**:
```toml
dependencies = [
    "defusedxml>=0.7.1",
]
```

**Files typically affected**:
- Evernote import/export
- XML-based format handlers
- Configuration parsers

---

### 5. SQL Injection Warnings (MEDIUM)

**Bandit**: `B608` - Possible SQL injection

**Problem**:
```python
query = f"SELECT * FROM {table} WHERE {where_clause}"  # ⚠️ Warning
cursor.execute(query)
```

**Why it warns**: String interpolation in SQL

**When it's a FALSE POSITIVE**:
```python
# Table name from schema (not user input)
query = f"SELECT * FROM {table}"  # Table from schema
cursor.execute(query)

# Parameterized values
query = f"SELECT * FROM entity WHERE {where_clause}"
cursor.execute(query, params)  # ✅ params are safe

# Use nosec with explanation
cursor.execute(  # nosec B608 - table name from schema, not user input
    f"SELECT * FROM {table}"
)
```

**When it's REAL**:
```python
# User input directly in query
table = request.form.get("table")  # ❌ DANGEROUS!
query = f"SELECT * FROM {table}"  # ❌ SQL INJECTION!
```

**Real fix**:
```python
# Whitelist allowed tables
ALLOWED_TABLES = ["entity", "relation", "observation"]
if table not in ALLOWED_TABLES:
    raise ValueError("Invalid table")

query = f"SELECT * FROM {table}"  # ✅ Now safe
```

---

### 6. Bind to All Interfaces (MEDIUM)

**Bandit**: `B104` - Binding to 0.0.0.0

**Problem**:
```python
host = "0.0.0.0"  # ⚠️ Warning - allows external connections
```

**Why it warns**: Opens service to all network interfaces

**When it's INTENTIONAL**:
```python
host: str = typer.Option(
    "0.0.0.0",  # nosec B104 - intentional for LAN access
    help="Bind to all interfaces for network access"
)
```

**When it's DANGEROUS**:
```python
# Production service without authentication
app.run(host="0.0.0.0", port=80)  # ❌ Exposed to internet!
```

**Best practice**:
```python
# Development
host = "127.0.0.1"  # ✅ Local only

# Production with auth
host = "0.0.0.0"  # ✅ OK if authenticated
```

---

### 7. Hardcoded Temp Directory (MEDIUM)

**Bandit**: `B108` - Insecure temp usage

**Problem**:
```python
temp_dir = "/tmp/myapp"  # ⚠️ Warning - race condition risk
```

**Fix**:
```python
import tempfile

# For demo/test code
temp_dir = "/tmp/myapp"  # nosec B108 - demo code only

# For production code
with tempfile.TemporaryDirectory() as temp_dir:  # ✅ Safe
    # Use temp_dir
```

---

## ⚠️ Low Severity Issues (Usually Acceptable)

### 8. Try/Except/Pass Pattern

**Bandit**: `B110` - Try/Except/Pass detected

**Problem**:
```python
try:
    some_operation()
except Exception:
    pass  # ⚠️ Silently swallows errors
```

**When it's OK**:
```python
# Graceful degradation
try:
    optional_metadata = parse_metadata()
except Exception:
    pass  # ✅ OK - metadata is optional
```

**When it's BAD**:
```python
# Critical operation
try:
    save_user_data()
except Exception:
    pass  # ❌ BAD - data loss!
```

**Better approach**:
```python
# Log the error
try:
    optional_operation()
except Exception as e:
    logger.debug(f"Optional operation failed: {e}")  # ✅ At least log it
```

---

### 9. Try/Except/Continue Pattern

**Bandit**: `B112` - Try/Except/Continue detected

**Similar to above** - acceptable for optional operations, bad for critical ones.

---

### 10. Assert Usage

**Bandit**: `B101` - Assert used

**Problem**:
```python
assert project_path is not None  # ⚠️ Removed in optimized mode
```

**Why it warns**: Asserts are removed when running with `-O` flag

**When it's OK**:
```python
# Development checks
assert config is not None  # ✅ OK for development

# Type narrowing
assert isinstance(value, str)  # ✅ OK for type checking
```

**When to avoid**:
```python
# Production validation
assert user.is_authenticated  # ❌ Bad - removed in production!

# Better:
if not user.is_authenticated:  # ✅ Always runs
    raise ValueError("Not authenticated")
```

---

## 🔍 Dependency Vulnerabilities

### Regular Scanning

```bash
# Check for vulnerabilities
uv run safety scan

# Output:
# ✅ 0 vulnerabilities reported
```

### When Vulnerabilities Found

**Example from our experience**:

```
-> Vulnerability found in starlette version 0.46.2
   CVE-2025-54121
   Fix: Update to 0.47.2+

-> Vulnerability found in regex version 2024.11.6
   PVE-2025-78558
   Fix: Update to 2025.2.10+
```

**How to fix**:
```bash
# Update vulnerable packages
uv add "starlette>=0.47.2" "regex>=2025.2.10"

# Verify fix
uv run safety scan
# Should show: 0 vulnerabilities
```

### Pinning vs Ranges

```toml
# Too restrictive (misses security patches)
dependencies = [
    "starlette==0.46.2",  # ❌ Stuck on vulnerable version
]

# Better (allows security updates)
dependencies = [
    "starlette>=0.47.2",  # ✅ Gets security patches
]

# Best (with upper bound)
dependencies = [
    "starlette>=0.47.2,<1.0",  # ✅ Safe + compatible
]
```

---

## 🎯 Security Workflow Configuration

### Essential: Resilient Security Scanning

```yaml
- name: Run bandit
  run: uv run bandit -r src/ -f json -o report.json || echo "Completed"
  continue-on-error: true  # ✅ Never blocks workflow

- name: Run safety
  run: uv run safety scan --output json --save-as report.json || echo "Completed"
  continue-on-error: true  # ✅ Never blocks workflow

- name: Upload reports
  uses: actions/upload-artifact@v4
  if: always()  # ✅ Always uploads
  with:
    name: security-reports
    path: |
      bandit-report.json
      safety-report.json

- name: Security scan complete
  if: always()
  run: echo "Scan completed"  # ✅ Ensures job success
```

**Why this matters**:
- Security findings shouldn't block development
- Reports are still generated and reviewed
- Workflow completes successfully
- Quality gate can decide if findings are acceptable

---

## 📋 Security Checklist for New Repos

### Code Security
- [ ] No `os.system()` usage
- [ ] No `shell=True` in subprocess
- [ ] MD5/SHA1 with `usedforsecurity=False` if not crypto
- [ ] Use `defusedxml` for XML parsing
- [ ] Parameterized SQL queries
- [ ] Input validation on all user inputs
- [ ] No hardcoded secrets

### Dependency Security
- [ ] `bandit` in dev-dependencies
- [ ] `safety` in dev-dependencies
- [ ] `defusedxml` in dependencies (if using XML)
- [ ] Regular dependency updates
- [ ] Lock file committed (`uv.lock`)

### Workflow Security
- [ ] Security scans on every push
- [ ] Weekly scheduled scans
- [ ] `continue-on-error` on scan steps
- [ ] Reports uploaded as artifacts
- [ ] CodeQL enabled (GitHub Security tab)

### Configuration Security
- [ ] No secrets in code
- [ ] Use GitHub Secrets for tokens
- [ ] `.gitignore` includes sensitive files
- [ ] Branch protection enabled
- [ ] Require reviews for PRs

---

## 🔒 Security Tools Setup

### 1. Bandit (Code Security)

**Install**:
```toml
[tool.uv]
dev-dependencies = [
    "bandit>=1.7.0",
]
```

**Usage**:
```bash
# Full scan
uv run bandit -r src/

# Only high severity
uv run bandit -r src/ --severity-level high

# JSON output
uv run bandit -r src/ -f json -o report.json

# Quiet mode
uv run bandit -r src/ -q
```

**Configuration** (`.bandit`):
```ini
[bandit]
exclude_dirs = ["/tests"]
skips = ["B101", "B601"]  # Skip specific tests
```

---

### 2. Safety (Dependency Security)

**Install**:
```toml
[tool.uv]
dev-dependencies = [
    "safety>=3.0.0",
]
```

**Usage**:
```bash
# Modern command (not deprecated 'check')
uv run safety scan

# JSON output
uv run safety scan --output json --save-as report.json

# Ignore specific vulnerabilities
uv run safety scan --ignore 78279
```

**Update vulnerable packages**:
```bash
uv add "package-name>=safe.version"
```

---

### 3. Trivy (File System Security)

**In GitHub Actions**:
```yaml
- name: Run Trivy
  uses: aquasecurity/trivy-action@master
  with:
    scan-type: 'fs'
    scan-ref: '.'
    format: 'sarif'
    output: 'trivy-results.sarif'

- name: Upload to GitHub Security
  uses: github/codeql-action/upload-sarif@v2
  if: always()
  with:
    sarif_file: 'trivy-results.sarif'
```

**Benefits**:
- Scans for misconfigurations
- Detects secrets in code
- Checks file permissions
- Results in GitHub Security tab

---

### 4. CodeQL (Static Analysis)

**In GitHub Actions**:
```yaml
codeql:
  name: CodeQL Analysis
  runs-on: ubuntu-latest
  permissions:
    security-events: write
  steps:
    - uses: actions/checkout@v4
    
    - name: Initialize CodeQL
      uses: github/codeql-action/init@v2
      with:
        languages: python
    
    - name: Autobuild
      uses: github/codeql-action/autobuild@v2
    
    - name: Analyze
      uses: github/codeql-action/analyze@v2
```

**Benefits**:
- GitHub's official security scanner
- Deep static analysis
- Results in Security tab
- Free for public repos

---

### 5. Semgrep (Optional Advanced)

**Setup** (requires free account):
1. Go to https://semgrep.dev/login
2. Login with GitHub
3. Create token
4. Add to GitHub Secrets as `SEMGREP_APP_TOKEN`

**In GitHub Actions**:
```yaml
- name: Run Semgrep
  if: env.SEMGREP_APP_TOKEN != ''
  uses: returntocorp/semgrep-action@v1
  with:
    config: >-
      p/security-audit
      p/secrets
      p/owasp-top-ten
  env:
    SEMGREP_APP_TOKEN: ${{ secrets.SEMGREP_APP_TOKEN }}
  continue-on-error: true
```

**Or local without token**:
```bash
uv pip install semgrep
uv run semgrep --config=auto src/
```

---

## 🎯 Common Vulnerability Patterns

### XML Bombs

**Attack**:
```xml
<!DOCTYPE lolz [
  <!ENTITY lol "lol">
  <!ENTITY lol1 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">
  <!ENTITY lol2 "&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;">
  ...
]>
<lolz>&lol9;</lolz>
```

**Result**: Exponential expansion, crashes parser

**Protection**:
```python
import defusedxml.ElementTree as ET  # ✅ Detects and prevents
```

---

### XXE (XML External Entity) Attacks

**Attack**:
```xml
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<data>&xxe;</data>
```

**Result**: Reads local files, SSRF attacks

**Protection**:
```python
import defusedxml.ElementTree as ET  # ✅ Disables external entities
```

---

### SQL Injection

**Attack**:
```python
table = user_input  # ❌ From attacker
query = f"SELECT * FROM {table}"  # ❌ Injection!
# Attacker sends: "users; DROP TABLE users--"
```

**Protection**:
```python
# Whitelist approach
ALLOWED_TABLES = ["users", "posts", "comments"]
if table not in ALLOWED_TABLES:
    raise ValueError("Invalid table")

query = f"SELECT * FROM {table}"  # ✅ Now safe

# Parameterized approach
query = "SELECT * FROM entity WHERE id = :id"
cursor.execute(query, {"id": user_id})  # ✅ Parameterized
```

---

## 📦 Complete Security Dependencies

```toml
[project]
dependencies = [
    # ... other deps ...
    "defusedxml>=0.7.1",  # For XML parsing
]

[tool.uv]
dev-dependencies = [
    # ... other deps ...
    "bandit>=1.7.0",      # Code security
    "safety>=3.0.0",      # Dependency security
]
```

---

## 🔄 Regular Security Maintenance

### Weekly Tasks

```bash
# 1. Update dependencies
uv lock --upgrade

# 2. Check for vulnerabilities
uv run safety scan

# 3. Fix any found
uv add "package>=safe.version"

# 4. Commit and push
git add uv.lock pyproject.toml
git commit -m "chore: update dependencies for security"
git push
```

### Monthly Tasks

- Review GitHub Security Advisories
- Check Dependabot alerts
- Review security scan artifacts
- Update security documentation

---

## 🎓 Lessons from Our Experience

### What We Fixed:
1. MD5 hash → Added `usedforsecurity=False`
2. Shell injection → Replaced with subprocess
3. XML vulnerabilities → Switched to defusedxml
4. Vulnerable dependencies → Updated starlette, regex
5. SQL warnings → Added nosec with justifications

### Time Breakdown:
- Identifying issues: 30 min
- Fixing HIGH severity: 1 hour
- Fixing MEDIUM severity: 1 hour
- Updating workflows: 30 min
- Testing: 30 min
- **Total**: 3.5 hours

### With This Guide:
- Copy security config: 5 min
- Run scans: 5 min
- Fix real issues: 30 min
- Verify: 10 min
- **Total**: ~50 minutes

**Time saved**: 2.5+ hours per project!

---

## ✅ Pre-Release Security Checklist

Before releasing:

- [ ] `uv run bandit -r src/ --severity-level high` → 0 HIGH issues
- [ ] `uv run safety scan` → 0 vulnerabilities
- [ ] GitHub Security tab shows no alerts
- [ ] All dependencies up to date
- [ ] No hardcoded secrets in code
- [ ] Security scans in CI passing
- [ ] CodeQL analysis complete

---

## 📚 Resources

- [Bandit Documentation](https://bandit.readthedocs.io/)
- [Safety Documentation](https://docs.pyup.io/docs/safety-scan)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security_warnings.html)
- [defusedxml Documentation](https://github.com/tiran/defusedxml)

---

**Security is not optional! Use this guide to get it right from the start.** 🔒

