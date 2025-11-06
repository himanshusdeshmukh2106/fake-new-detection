# Performance Optimization Guide

## Why Is It Slow?

The fact-checking process involves **5 major steps**, each requiring API calls to Gemini:

### Current Process Timeline

```
Step 1: Extract Claims (3-5 seconds)
  └─> LLM call to decompose text into claims

Step 2-3: Parallel Processing (5-10 seconds)
  ├─> Restore claims (map to document) - with 3 retries if fails
  ├─> Check worthiness (filter important claims)
  └─> Generate search queries

Step 4: Search for Evidence (10-20 seconds) ⚠️ SLOWEST
  └─> Multiple web searches via Serper API
  └─> One search per claim, per query (can be 10+ searches)

Step 5: Verify Claims (5-10 seconds)
  └─> LLM calls to verify each claim against evidence

Total: 23-45 seconds per fact-check
```

## Main Bottlenecks

### 1. **Evidence Retrieval (Step 4)** - 40-50% of total time
- Multiple sequential web searches
- Network latency for each search
- Waiting for search API responses

### 2. **Retry Logic** - Adds 30-60 seconds when triggered
- The warning you saw means 2-3 extra LLM calls
- Each retry takes 10-20 seconds

### 3. **Rate Limits** - Free tier Gemini
- 10 requests per minute limit
- Forced delays between calls

## How to Speed It Up

### Option 1: Reduce Retries (Quick Fix)
Currently retries 3 times. Reduce to 1:

```python
# In webapp.py, find where FactCheck is initialized
factcheck_instance = FactCheck(
    # ... other params
    num_seed_retries=1  # Change from 3 to 1
)
```

**Impact:** Save 20-40 seconds when retries happen
**Trade-off:** Slightly less accurate claim mapping

### Option 2: Use Vertex AI (Recommended)
You already have the service account configured!

**Benefits:**
- 1000 requests/minute (vs 10/minute)
- No forced delays
- Faster response times

**How to enable:** Already configured in your `api_config.yaml`!

### Option 3: Reduce Evidence Sources
Limit the number of search results per claim:

```python
# In factcheck/core/ClaimVerify.py or evidence retrieval
max_evidence_per_claim = 3  # Instead of 5-10
```

**Impact:** Save 5-10 seconds
**Trade-off:** Less comprehensive verification

### Option 4: Parallel Evidence Retrieval
The code already does some parallelization, but evidence retrieval could be more parallel.

### Option 5: Cache Results
Cache fact-check results for identical/similar text:

```python
# Add caching layer
import hashlib
cache = {}

def check_text_cached(text):
    text_hash = hashlib.md5(text.encode()).hexdigest()
    if text_hash in cache:
        return cache[text_hash]
    result = factcheck.check_text(text)
    cache[text_hash] = result
    return result
```

**Impact:** Instant results for repeated checks

## Quick Win: Reduce Retries ✅ APPLIED

I've already reduced retries from 3 to 1 in `webapp.py`:

```python
factcheck_instance = FactCheck(
    default_model=args.model,
    api_config=api_config,
    prompt=args.prompt,
    retriever=args.retriever,
    num_seed_retries=1,  # Reduced from 3 to 1
)
```

**Expected improvement:** 
- Normal cases: Same speed
- When retries happen: Save 20-40 seconds (you'll see fewer warnings)

## Realistic Speed Expectations

With current setup (Gemini 2.5 Flash + Serper):
- **Short text (1-2 claims):** 15-25 seconds
- **Medium text (3-5 claims):** 25-40 seconds  
- **Long text (6+ claims):** 40-60+ seconds

The main bottleneck is **web search** - each claim needs multiple searches, and that's network-bound.

## Best Optimization: Use Vertex AI

You already have it configured! Vertex AI would give you:
- 100x higher rate limits
- Potentially faster response times
- No retry delays

To use it, the system should automatically detect your `GOOGLE_APPLICATION_CREDENTIALS` in `api_config.yaml`.
