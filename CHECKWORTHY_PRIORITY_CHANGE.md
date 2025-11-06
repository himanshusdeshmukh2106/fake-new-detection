# CheckWorthy Priority Change

## What Changed

**Before:** ML Model Primary → LLM Fallback  
**After:** LLM Primary → ML Model Fallback ✅

## New Flow

```
Step 1: Try LLM (Gemini 2.5 Flash)
  ├─ Success → Use LLM results
  └─ Failure → Go to Step 2

Step 2: Try ML Classifier (Fallback)
  ├─ Success → Use ML results
  └─ Failure → Go to Step 3

Step 3: Last Resort
  └─ Treat all claims as checkworthy
```

## Why This Change?

### Advantages of LLM Primary:
1. **More accurate** - LLM understands context better
2. **More flexible** - Can handle edge cases
3. **Better reasoning** - Explains why claims are checkworthy
4. **Up-to-date** - Uses latest model capabilities

### ML as Fallback:
1. **Reliability** - If API fails, ML still works offline
2. **Speed** - ML is instant if LLM fails
3. **Cost savings** - Only uses API when it works
4. **Graceful degradation** - System never completely fails

## Expected Behavior

### Normal Operation (LLM works):
```
[INFO] 📡 Using LLM for 2 claims (primary method)...
[INFO] ✅ LLM identified: 1/2 claims as checkworthy
```

### LLM Fails (ML fallback):
```
[WARNING] ⚠️  LLM checkworthy detection failed: [error]
[INFO] 🤖 Using ML classifier as fallback for 2 claims...
[INFO] ✅ ML Fallback: 1/2 claims identified as checkworthy
```

### Both Fail (last resort):
```
[WARNING] ⚠️  Both LLM and ML failed - treating all claims as checkworthy
```

## Impact

- **Accuracy:** Higher (LLM is more accurate than ML)
- **Speed:** Slightly slower (LLM takes ~2-3 seconds, ML is instant)
- **Reliability:** Same (still has fallback)
- **Cost:** Slightly higher (uses API more often)

## Trade-offs

| Aspect | LLM Primary | ML Primary (old) |
|--------|-------------|------------------|
| Accuracy | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Speed | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Cost | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Reliability | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Context Understanding | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |

## Recommendation

This change is **good for production** because:
- ✅ Better accuracy is worth the slight speed trade-off
- ✅ Still has ML fallback for reliability
- ✅ LLM is the industry standard for this task
- ✅ Aligns with best practices

The ML model remains valuable as a **safety net** when the API is unavailable.
