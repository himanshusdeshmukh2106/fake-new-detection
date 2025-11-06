# Decompose Warning Explanation

## Warning Message
```
[WARNING] Restore claims partially satisfied. Using available mappings. Retry 1/3
[WARNING] Restore claims partially satisfied. Using available mappings. Retry 2/3
```

## What It Means

This warning appears in `factcheck/core/Decompose.py` during the claim decomposition process. It's **NOT related to the ML model**.

### Root Cause

The system is trying to map extracted claims back to their original text spans in the document. The warning occurs when:

1. **The LLM (Gemini) extracts claims** from your text
2. **The system tries to find where each claim appears** in the original document
3. **Some claims can't be exactly matched** to text spans in the original document

This happens because:
- The LLM might paraphrase or slightly reword claims
- The LLM might extract implied claims not explicitly stated
- Text formatting differences (whitespace, punctuation)

### What Happens

When this occurs, the system:
1. **Retries up to 3 times** to get better mappings from the LLM
2. **Uses fallback strategies**:
   - Keyword matching to find relevant text chunks
   - Uses the claim itself as the text span if no match found
3. **Continues processing** with partial results rather than failing

### Is This a Problem?

**No, this is normal behavior** and not an error:
- ✅ The fact-checking still works
- ✅ Claims are still verified
- ✅ Results are still accurate
- ⚠️ Just means some claims might not have perfect text span mappings

### When It Happens More Often

- Complex or long documents
- Documents with implied claims
- Paraphrased content
- Using Gemini 2.5 Flash (faster but sometimes less precise on text spans)

### How to Reduce Warnings

If you want fewer warnings:
1. Use more explicit, direct statements in your text
2. Avoid very long documents (break them up)
3. The system already retries automatically, so no action needed

## Conclusion

This is a **graceful degradation** feature - the system handles imperfect LLM responses and continues working rather than crashing. It's working as designed! 👍
