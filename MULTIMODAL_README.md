# Fake News Detection with Gemini 2.5 Pro Vision

This enhanced version supports **multimodal fact-checking** with Google's Gemini 2.5 Pro Vision model.

## 🚀 **New Features**

### **Multimodal Support:**
- ✅ **Text** - Direct text input for fact-checking
- ✅ **Images** - Upload images for visual content analysis
- ✅ **Videos** - Upload videos for content verification
- ❌ **Speech** - Removed (use text, image, or video instead)

### **Technology Stack:**
- **Gemini 2.5 Pro Vision** - For image and video analysis
- **Google Cloud Storage** - For file uploads with public URLs
- **Serper API** - For evidence retrieval
- **Flask Web Interface** - With file upload support

## 📋 **Setup Instructions**

### 1. **Install Dependencies**
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 2. **Configure API Keys**
Edit `api_config.yaml`:
```yaml
SERPER_API_KEY: \"your_serper_api_key_here\"
GEMINI_API_KEY: \"your_gemini_api_key_here\"
GCS_BUCKET_NAME: \"my-media-storage-12345\"
GCS_BASE_URL: \"https://storage.googleapis.com/my-media-storage-12345\"
```

### 3. **Google Cloud Storage Setup (Optional)**
For file uploads to work properly:
```bash
# Set credentials
set GOOGLE_APPLICATION_CREDENTIALS=path/to/your/service-account-key.json

# Check setup guide
python gcs_setup_guide.py
```

## 🔧 **Usage**

### **Web Interface**
```bash
python webapp.py --api_config api_config.yaml
```
**Features:**
- Text input form for direct fact-checking
- File upload for images/videos
- Real-time processing with progress timer
- Comprehensive fact-check results

### **Command Line**
```bash
# Text fact-checking
python -m factcheck --modal string --input \"Your claim here\" --api_config api_config.yaml

# Image analysis
python -m factcheck --modal image --input \"path/to/image.jpg\" --api_config api_config.yaml

# Video analysis
python -m factcheck --modal video --input \"path/to/video.mp4\" --api_config api_config.yaml
```

## 🏗️ **Architecture Changes**

### **Multimodal Processing Pipeline:**
1. **File Upload** → Temporary storage
2. **Google Cloud Storage** → Public URL generation
3. **Gemini Vision** → Content analysis and text extraction
4. **Claim Extraction** → Filter factual claims from visual descriptions
5. **Fact-Checking Pipeline** → Standard claim verification
6. **Results** → Comprehensive verification report

### **Supported File Types:**
- **Images:** `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.webp`
- **Videos:** `.mp4`, `.avi`, `.mov`, `.wmv`, `.flv`, `.webm`, `.m4v`

## 🔍 **How It Works**

### **Image Processing:**
1. User uploads image via web interface
2. Image is uploaded to Google Cloud Storage
3. **Enhanced Gemini Vision** analyzes image with factual-focused prompts
4. **Dual-layer filtering** extracts only verifiable factual claims
5. Results show verification of extracted factual content

### **Video Processing:**
1. User uploads video file
2. Video is uploaded to Google Cloud Storage
3. **Enhanced Gemini Vision** analyzes video with factual-focused prompts
4. **Frame Analysis** (fallback) extracts factual content from key frames
5. **Dual-layer filtering** ensures only verifiable claims are extracted
6. Results show chronological factual information from video content

### **Enhanced Intelligent Claim Extraction:**

The system includes **advanced claim extraction** with comprehensive filtering:

**✅ STRICT INCLUSION - Extracts Only:**
- Specific numerical facts, statistics, measurements, dates, years
- Names of real people, organizations, institutions, companies  
- Geographic locations, addresses, place names
- Historical events, scientific facts, documented phenomena
- Verifiable text content visible in images/videos (signs, labels)
- Factual statements about real-world entities, products, services
- Claims about relationships, affiliations, associations
- Statements about achievements, awards, records, accomplishments

**❌ STRICT EXCLUSION - Filters Out:**
- Visual descriptions (colors, shapes, sizes, positioning)
- **Background descriptions** ("white background", "blue sky", "green grass")
- Aesthetic opinions ("beautiful", "stunning", "attractive", "nice")
- **Visual composition** ("in the center", "on the left", "at the top")
- **Object appearances** ("red car", "tall building", "large window")
- General observations ("there is", "shows", "depicts", "contains")
- Subjective assessments ("seems", "appears to be", "looks like")
- **Spatial relationships** ("next to", "behind", "in front of")
- **Visual qualities** ("bright", "dark", "clear", "blurry")
- Weather/lighting conditions ("sunny", "well-lit", "shadowy")

**Enhanced Examples:**
- **Input:** "The image has a white background showing Einstein won the Nobel Prize in Physics in 1921"
- **Extracted:** "Einstein won the Nobel Prize in Physics in 1921"
- **Filtered Out:** "white background", visual descriptions

## 🛠️ **Configuration**

### **API Keys Required:**
- **GEMINI_API_KEY** - Get from [Google AI Studio](https://makersuite.google.com/app/apikey)
- **SERPER_API_KEY** - Get from [Serper.dev](https://serper.dev/)

### **Optional GCS Setup:**
- **Google Cloud Credentials** - For file uploads
- **GCS Bucket** - Public storage for media files

## ⚡ **Performance Notes**

- **Gemini Vision** is optimized for factual content extraction
- **Rate Limits** are set to 15 requests/minute for Gemini
- **Fallback Mode** uses local files if GCS is not configured
- **File Size Limits** depend on your GCS configuration

## 🚨 **Important Changes**

- ❌ **OpenAI removed** - No longer using GPT-4 Vision
- ❌ **Speech processing removed** - Use other modalities
- ✅ **Gemini 2.5 Pro Vision** - Primary multimodal model
- ✅ **Google Cloud Storage** - For scalable file handling

## 🎯 **Example Workflow**

1. **Start the webapp:** `python webapp.py --api_config api_config.yaml`
2. **Open browser:** Go to http://localhost:2024
3. **Upload image/video:** Select file and click \"Upload & Check\"
4. **View results:** Get comprehensive fact-check analysis

The system now provides powerful multimodal fact-checking capabilities using Google's latest AI technologies!