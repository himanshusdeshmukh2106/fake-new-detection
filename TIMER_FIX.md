# Timer Fix Summary

## Issue
The elapsed time timer in the web dashboard was stuck at 0 seconds and not updating during fact-check processing.

## Root Cause
The inline timer element (`#timer` with `#elapsed-time` span) was never:
1. Made visible (display was set to 'none')
2. Updated by the timer interval function

Only the loading overlay timer was working.

## Solution
Updated `templates/main_layout.html` to:

1. **Show the inline timer** when form is submitted:
   ```javascript
   const inlineTimer = document.getElementById('timer');
   if (inlineTimer) {
       inlineTimer.style.display = 'block';
   }
   ```

2. **Update both timers** in the interval function:
   ```javascript
   const timer = setInterval(() => {
       seconds++;
       document.getElementById('loading-elapsed-time').textContent = seconds;
       const elapsedTime = document.getElementById('elapsed-time');
       if (elapsedTime) {
           elapsedTime.textContent = seconds;
       }
   }, 1000);
   ```

3. **Hide the inline timer** when processing completes:
   ```javascript
   if (inlineTimer) {
       inlineTimer.style.display = 'none';
   }
   ```

## Result
✅ Both timers now work correctly:
- Loading overlay timer (full screen)
- Inline timer (below the "Check Facts" button)

Both update every second during fact-check processing.
