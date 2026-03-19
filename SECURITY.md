# 🔐 Security Guide for Katalog-AI

## API Keys Management

### ⚠️ NEVER DO THIS
```bash
# ❌ WRONG - Key exposed in command history
export OPENAI_API_KEY="sk-proj-Q-PQJKC4uL6GC113m_hyBJ8..."

# ❌ WRONG - Key in code
const API_KEY = "sk-proj-..."

# ❌ WRONG - Key in git repo
echo "OPENAI_API_KEY=sk-proj-..." >> .env
git add .env

# ❌ WRONG - Key in txt files
# .env file content: OPENAI_API_KEY=sk-proj-...
```

### ✅ DO THIS INSTEAD

#### For Local Development

**1. Create `.env.local` (git ignored)**
```bash
# File: .env.local
OPENAI_API_KEY=sk-proj-your-real-key-here
```

**2. Load it in scripts**
```python
from dotenv import load_dotenv
import os

load_dotenv('.env.local')  # Loads from local file
api_key = os.getenv('OPENAI_API_KEY')
```

**3. Run scripts**
```bash
# Will automatically use .env.local
python scripts/generate_embeddings.py
```

#### For GitHub Actions (CI/CD)

**1. Add Secret**
- Go: https://github.com/ilyastas/katalog-ai/settings/secrets/actions
- Click: "New repository secret"
- Name: `OPENAI_API_KEY`
- Value: paste your API key
- Click: "Add secret"

**2. Use in workflow**
```yaml
jobs:
  generate-embeddings:
    runs-on: ubuntu-latest
    env:
      OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
    steps:
      - run: python scripts/generate_embeddings.py
```

**3. Key is encrypted**
- ✅ Encrypted at rest
- ✅ Only available during jobs (temporary)
- ✅ Not exposed in logs
- ✅ Cannot be read back (one-way encryption)

---

## File Permissions

### .env.local
```
File: .env.local
Status: ✅ In .gitignore (never committed)
Access: Only local machine
```

### .env.example
```
File: .env.example
Status: ✅ Committed to repo
Content: ONLY placeholders (no real keys)
Purpose: Template for developers
```

### .env (if used)
```
File: .env
Status: ✅ In .gitignore (never committed)
Access: Local fallback values
```

---

## API Key Rotation

If key is accidentally exposed:

### Step 1: Revoke Immediately
```
1. https://platform.openai.com/api-keys
2. Find the exposed key
3. Delete it (Trash icon)
4. Generate NEW key
```

### Step 2: Update Secrets
```
1. GitHub: Settings → Secrets → OPENAI_API_KEY
2. Click: "Update" (not add new)
3. Paste new key value
4. Save
```

### Step 3: Update Local
```
1. Edit .env.local
2. Paste new key
3. Save
4. ✅ Done - no restart needed
```

### Step 4: Verify
```bash
python scripts/generate_embeddings.py --help
# Should show masked key: sk-proj-***-key
```

---

## Environment Variables Hierarchy

```
1. Environment variables (from terminal: export X=Y)
2. .env.local (local dev secrets) ← Use this
3. .env.example (defaults/templates)
4. GitHub Secrets (CI/CD only) ← Use this
```

**Script will load from all sources in order:**
```python
# Load chain
load_dotenv('.env.local')     # Highest priority (localhost)
load_dotenv('.env')            # Medium priority (defaults)
api_key = os.getenv('...')     # From any source
```

---

## Secure Defaults

### requirements.txt
```
✅ python-dotenv==1.0.0        # For .env loading
✅ openai==1.15.0              # Official SDK
✅ requests==2.31.0            # HTTP client
```

### .gitignore (Essential)
```
.env                  # Local environment
.env.local           # Local secrets
.env.*.local         # Environment-specific
*.log                # Logs (may contain keys)
__pycache__/         # Python artifacts
secrets/             # Manual secrets folder (if used)
```

### CI/CD Protection
```
✅ Workflow jobs have limited scope
✅ Secrets unavailable in logs (masked)
✅ No key exposure in artifacts
✅ Timeout after job completes
```

---

## Monitoring Secrets

### GitHub Push Protection (Enabled)
```
GitHub will block pushes if it detects:
✅ AWS keys (AKIA...)
✅ GitHub tokens (ghp_...)
✅ Slack tokens (xoxb-...)
✅ OpenAI keys (sk-...)
```

### If Push Blocked
```bash
# Check what was detected
git log --all -p | grep -i "sk-" | head -20

# Remove from recent commits
git reset HEAD~1  # Undo last commit
# Remove sensitive data
# Commit again
git commit -m "Remove accidental secrets"
git push
```

---

## Best Practices Checklist

- [ ] `.env.local` created (for local dev)
- [ ] `.env.local` is in `.gitignore`
- [ ] `.env.example` has only placeholders
- [ ] GitHub Secret added: `OPENAI_API_KEY`
- [ ] Workflow uses `${{ secrets.OPENAI_API_KEY }}`
- [ ] Never paste keys in chat/messages/comments
- [ ] Use masked output when logging keys
- [ ] Rotate keys if exposed

---

## Troubleshooting

### Key not being loaded
```bash
# Check if .env.local exists
ls -la .env.local

# Check if OPENAI_API_KEY is set
echo $OPENAI_API_KEY

# If empty, set it
export OPENAI_API_KEY="sk-proj-..."
```

### GitHub Secret not working
```
1. Regenerate new key (old one may be cached)
2. Update GitHub Secret (don't add new one)
3. Wait 30 seconds
4. Re-run workflow
```

### Script says "API key not found"
```bash
# Option 1: Create .env.local
echo 'OPENAI_API_KEY=sk-proj-...' > .env.local

# Option 2: Set environment variable
export OPENAI_API_KEY='sk-proj-...'

# Then run script
python scripts/generate_embeddings.py
```

---

## Support

- Issues: https://github.com/ilyastas/katalog-ai/issues
- Security: Use GitHub Security Advisory (private report)
- Questions: Check `.env.local` template in repo

---

**Last updated**: 2026-03-06  
**Maintainer**: ilyastas
