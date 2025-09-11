import cv2
import os
import uuid
from google.cloud import storage
import google.generativeai as genai
from .logger import CustomLogger

logger = CustomLogger(__name__).getlog()

# Google Cloud Storage configuration
GCS_BUCKET_NAME = "my-media-storage-12345"
GCS_BASE_URL = "https://storage.googleapis.com/my-media-storage-12345"


def upload_to_gcs(file_path: str, gemini_api_key: str) -> str:
    """
    Upload file to Google Cloud Storage and return public URL
    
    Args:
        file_path (str): Local path to the file
        gemini_api_key (str): Gemini API key (used for authentication context)
    
    Returns:
        str: Public URL of uploaded file
    """
    try:
        # Generate unique filename
        file_extension = os.path.splitext(file_path)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        
        # Initialize Google Cloud Storage client
        # Note: This assumes you have credentials configured
        # via GOOGLE_APPLICATION_CREDENTIALS environment variable
        client = storage.Client()
        bucket = client.bucket(GCS_BUCKET_NAME)
        blob = bucket.blob(unique_filename)
        
        # Upload file
        logger.info(f"Uploading {file_path} to GCS as {unique_filename}")
        blob.upload_from_filename(file_path)
        
        # Make blob publicly accessible
        blob.make_public()
        
        # Return public URL
        public_url = f"{GCS_BASE_URL}/{unique_filename}"
        logger.info(f"File uploaded successfully: {public_url}")
        return public_url
        
    except Exception as e:
        logger.error(f"Failed to upload file to GCS: {e}")
        # Fallback: return local file path (for development)
        logger.warning("Using local file path as fallback")
        return file_path


def image2text(input_path: str, gemini_api_key: str) -> str:
    """
    Convert image to text using Gemini 2.5 Pro Vision
    
    Args:
        input_path (str): Path to image file
        gemini_api_key (str): Gemini API key
    
    Returns:
        str: Description of the image
    """
    try:
        # Configure Gemini
        genai.configure(api_key=gemini_api_key)
        
        # Upload image to Google Cloud Storage
        image_url = upload_to_gcs(input_path, gemini_api_key)
        
        # Use Gemini 2.0 Flash Experimental model (most current vision model)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # If image is uploaded to GCS, use URL; otherwise use local file
        if image_url.startswith('http'):
            # Use image URL
            prompt = [
                "Analyze this image and provide a detailed description of what you see. "
                "Focus on factual content that can be verified. Include any text, objects, "
                "people, locations, or events visible in the image.",
                {
                    "mime_type": "image/jpeg",
                    "data": image_url
                }
            ]
        else:
            # Use local file
            with open(input_path, 'rb') as image_file:
                image_data = image_file.read()
            
            prompt = [
                "Analyze this image and provide a detailed description of what you see. "
                "Focus on factual content that can be verified. Include any text, objects, "
                "people, locations, or events visible in the image.",
                {
                    "mime_type": "image/jpeg",
                    "data": image_data
                }
            ]
        
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        logger.error(f"Error processing image with Gemini Vision: {e}")
        return f"Error processing image: {str(e)}"


def video2text(input_path: str, gemini_api_key: str) -> str:
    """
    Convert video to text using Gemini 2.5 Pro Vision
    
    Args:
        input_path (str): Path to video file
        gemini_api_key (str): Gemini API key
    
    Returns:
        str: Description of the video content
    """
    try:
        # Configure Gemini
        genai.configure(api_key=gemini_api_key)
        
        # Upload video to Google Cloud Storage
        video_url = upload_to_gcs(input_path, gemini_api_key)
        
        # Use Gemini 2.0 Flash Experimental model
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # If video is uploaded to GCS, use URL; otherwise extract frames
        if video_url.startswith('http'):
            # Use video URL directly with Gemini
            prompt = [
                "Analyze this video and provide a detailed description of what happens. "
                "Focus on factual content that can be verified. Include any text, objects, "
                "people, actions, locations, or events visible in the video. "
                "Provide a chronological summary of the key moments.",
                {
                    "mime_type": "video/mp4",
                    "data": video_url
                }
            ]
        else:
            # Fallback: Extract frames and analyze
            frames = extract_video_frames(input_path)
            if not frames:
                return "Error: Could not extract frames from video"
            
            # Analyze multiple frames
            prompt = [
                "These are frames from a video. Analyze the sequence and provide a detailed "
                "description of what happens in the video. Focus on factual content that can "
                "be verified. Include any text, objects, people, actions, locations, or events "
                "visible across the frames. Provide a chronological summary."
            ]
            
            # Add frame data
            for i, frame_data in enumerate(frames[:10]):  # Limit to 10 frames
                prompt.append({
                    "mime_type": "image/jpeg",
                    "data": frame_data
                })
        
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        logger.error(f"Error processing video with Gemini Vision: {e}")
        return f"Error processing video: {str(e)}"


def extract_video_frames(video_path: str, max_frames: int = 10) -> list:
    """
    Extract frames from video for analysis
    
    Args:
        video_path (str): Path to video file
        max_frames (int): Maximum number of frames to extract
    
    Returns:
        list: List of frame data as bytes
    """
    frames = []
    try:
        video = cv2.VideoCapture(video_path)
        total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Calculate frame interval to get evenly distributed frames
        frame_interval = max(1, total_frames // max_frames)
        
        frame_count = 0
        while video.isOpened() and len(frames) < max_frames:
            success, frame = video.read()
            if not success:
                break
                
            if frame_count % frame_interval == 0:
                # Encode frame as JPEG
                _, buffer = cv2.imencode('.jpg', frame)
                frames.append(buffer.tobytes())
            
            frame_count += 1
        
        video.release()
        logger.info(f"Extracted {len(frames)} frames from video")
        return frames
        
    except Exception as e:
        logger.error(f"Error extracting frames from video: {e}")
        return []


def modal_normalization(modal="text", input=None, gemini_api_key=None):
    """
    Process different input modalities and convert to text
    
    Args:
        modal (str): Input type - 'string', 'text', 'image', 'video'
        input: Input content or path to file
        gemini_api_key (str): Gemini API key for vision processing
    
    Returns:
        str: Processed text content
    """
    logger.info(f"== Processing: Modal: {modal}, Input: {input}")
    
    if modal == "string":
        response = str(input)
    elif modal == "text":
        with open(input, "r", encoding="utf-8") as f:
            response = f.read()
    elif modal == "image":
        if not gemini_api_key:
            raise ValueError("Gemini API key required for image processing")
        response = image2text(input, gemini_api_key)
    elif modal == "video":
        if not gemini_api_key:
            raise ValueError("Gemini API key required for video processing")
        response = video2text(input, gemini_api_key)
    elif modal == "speech":
        raise NotImplementedError("Speech processing has been removed. Please use text, image, or video input.")
    else:
        raise NotImplementedError(f"Modal type '{modal}' is not supported. Supported types: string, text, image, video")
    
    logger.info(f"== Processed: Modal: {modal}, Input: {input}")
    return response