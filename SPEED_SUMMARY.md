# Why Fact-Checking Is Slow - Simple Explanation

## The Process (5 Steps)

Think of it like a detective investigation:

1. **Read the document** (3-5 sec)
   - AI reads your text and extracts claims
   - 1 API call to Gemini

2. **Analyze claims** (5-10 sec)
   - Which claims are important?
   - Where did each claim come from?
   - What should we search for?
   - 3 parallel API calls

3. **Search the internet** (10-20 sec) ⚠️ **SLOWEST PART**
   - For each claim, search Google multiple times
   - Example: 3 claims × 3 searches each = 9 web searches
   - Each search takes 1-3 seconds
   - This is like a human Googling things - takes time!

4. **Read search results** (5-10 sec)
   - AI reads all the evidence found
   - 1 API call per claim

5. **Make verdict** (3-5 sec)
   - AI compares claim vs evidence
   - Decides: Supported, Refuted, or Controversial

**Total: 26-50 seconds**

## Why So Slow?

### Main Reason: Web Searches
- Can't make web searches faster (network speed)
- More claims = more searches = more time
- This is unavoidable for accurate fact-checking

### Secondary Reasons:
- API rate limits (10 requests/minute on free tier)
- Retries when AI makes mistakes (the warnings you saw)
- Processing multiple claims sequentially

## What I Just Did ✅

**Reduced retries from 3 to 1**
- When AI makes mistakes, it now retries once instead of 3 times
- Saves 20-40 seconds when retries happen
- You'll see fewer warning messages

## Can It Be Faster?

**Realistic expectations:**
- Short text (1-2 claims): ~20 seconds
- Medium text (3-5 claims): ~35 seconds
- Long text (6+ claims): ~50+ seconds

**To make it faster:**
1. ✅ Use shorter text (fewer claims = fewer searches)
2. ✅ Already using fastest model (Gemini 2.5 Flash)
3. ✅ Already reduced retries
4. 🔄 Could use Vertex AI (you have it configured) - would help with rate limits
5. 🔄 Could cache results for repeated checks

**Bottom line:** Most of the time is spent searching the web for evidence. That's the nature of fact-checking - it needs to verify claims against real sources!
