# Screen Capture Feature - Chrome Extension

## Overview
The OpenFactVerification Chrome extension now includes a **Screen Capture** feature that allows users to select a portion of their screen and analyze it for factual claims, similar to Google Lens functionality.

## How to Use

### 1. Access Screen Capture
- Open the OpenFactVerification extension popup
- Navigate to the **Media** tab
- Click the **"Capture Screen"** button (📷 icon)

### 2. Screen Selection Process
1. **Permission Request**: The extension will request screen capture permissions
2. **Selection Overlay**: A semi-transparent overlay will appear over your screen
3. **Area Selection**: Click and drag to select the area you want to analyze
4. **Confirmation**: A dialog will appear asking you to confirm the capture
5. **Processing**: The selected area will be captured and sent for fact-checking

### 3. View Results
- The extension will analyze the captured image for factual claims
- Results will be displayed in a modal showing:
  - Overall factuality score
  - Number of claims found
  - Individual claim assessments (Supported/Refuted/Controversial)
  - Evidence sources (when available)

## Features

### Screen Selection Overlay
- **Visual Feedback**: Semi-transparent overlay with selection rectangle
- **Instructions**: Clear guidance displayed during selection
- **Keyboard Controls**: Press ESC to cancel selection
- **Minimum Size**: Prevents accidentally small selections

### Image Processing
- **High Quality**: Captures at full screen resolution
- **Focused Analysis**: Uses Gemini Vision AI to extract only factual claims
- **Smart Filtering**: Ignores visual descriptions, focuses on verifiable information

### Integration
- **Seamless Workflow**: Integrates with existing fact-checking pipeline
- **Unified Results**: Uses same result display as text and file fact-checking
- **Error Handling**: Graceful error messages and fallback options

## Technical Implementation

### Permissions Required
- `desktopCapture`: For screen capture functionality
- `tabs`: For tab management and injection

### Key Components
1. **Popup Interface** (`popup.js`): Screen capture button and UI
2. **Background Script** (`background.js`): Desktop capture API integration
3. **Screen Capture Module** (`screen-capture.js`): Selection overlay and capture logic
4. **Content Script** (`content.js`): Result display integration

### API Integration
- Uses Chrome's `desktopCapture` API for screen access
- Processes captured images through existing multimodal pipeline
- Leverages Gemini Vision for factual content extraction

## Use Cases

### News and Social Media
- Fact-check screenshots of news articles
- Verify claims in social media posts
- Analyze infographics and data visualizations

### Research and Education
- Verify statistics in presentations
- Check claims in online articles
- Analyze charts and graphs for accuracy

### General Web Browsing
- Quick fact-checking of any visual content
- Verify claims in images and screenshots
- Analyze text within images

## Limitations

### Technical Constraints
- Requires screen capture permissions
- May not work on restricted pages (chrome://, extension pages)
- Network dependent for processing

### Content Limitations
- Works best with text-heavy images
- May have difficulty with low-resolution or blurry content
- Optimized for factual claims, not visual analysis

## Privacy and Security
- Screenshots are processed locally and sent securely to the backend
- No permanent storage of captured images
- Uses encrypted communication with fact-checking API
- User has full control over what gets captured and analyzed

## Troubleshooting

### Common Issues
1. **Permission Denied**: Grant screen capture permissions when prompted
2. **Selection Not Working**: Ensure you're not on a restricted page
3. **Processing Errors**: Check backend server connection (localhost:2024)
4. **No Claims Found**: Try selecting areas with more text content

### Error Messages
- **"Screen capture was cancelled"**: User cancelled the permission dialog
- **"Failed to start screen capture"**: Permission or technical issue
- **"Please select a larger area"**: Selection too small (minimum 10x10 pixels)
- **"No verifiable factual claims found"**: No fact-checkable content in selection

## Future Enhancements
- Batch processing of multiple screen areas
- OCR improvements for better text recognition
- Real-time fact-checking as you browse
- Integration with browser bookmark system for flagged content