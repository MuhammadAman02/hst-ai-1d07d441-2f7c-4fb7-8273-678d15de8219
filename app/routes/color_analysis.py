from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import logging
from typing import Dict, Any
from core.image_processor import ImageProcessor
from core.color_analyzer import ColorAnalyzer
from models.schemas import ColorRecommendationResponse, SkinToneAnalysis
from app.config import get_settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()
settings = get_settings()

# Initialize processors
image_processor = ImageProcessor()
color_analyzer = ColorAnalyzer()

@router.post("/analyze-skin-tone", response_model=ColorRecommendationResponse)
async def analyze_skin_tone(file: UploadFile = File(...)):
    """
    Analyze skin tone from uploaded image and provide color recommendations.
    """
    try:
        logger.info(f"Processing image upload: {file.filename}")
        
        # Validate file type
        if file.content_type not in settings.allowed_image_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed types: {settings.allowed_image_types}"
            )
        
        # Validate file size
        file_content = await file.read()
        if len(file_content) > settings.max_image_size:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {settings.max_image_size} bytes"
            )
        
        # Process image and analyze skin tone
        logger.info("Processing image for skin tone analysis")
        processed_image = image_processor.process_image(file_content)
        
        logger.info("Analyzing skin tone")
        skin_tone_data = color_analyzer.analyze_skin_tone(processed_image)
        
        logger.info("Generating color recommendations")
        color_recommendations = color_analyzer.get_color_recommendations(skin_tone_data)
        
        # Create response
        response = ColorRecommendationResponse(
            skin_tone=SkinToneAnalysis(
                category=skin_tone_data["category"],
                undertone=skin_tone_data["undertone"],
                dominant_colors=skin_tone_data["dominant_colors"],
                confidence_score=skin_tone_data["confidence"]
            ),
            recommended_colors=color_recommendations["recommended"],
            avoid_colors=color_recommendations["avoid"],
            color_palettes=color_recommendations["palettes"],
            styling_tips=color_recommendations["tips"]
        )
        
        logger.info(f"Analysis complete. Skin tone: {skin_tone_data['category']}")
        return response
        
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing image: {str(e)}"
        )

@router.get("/color-palettes")
async def get_color_palettes():
    """Get available color palettes for different skin tones."""
    try:
        palettes = color_analyzer.get_all_palettes()
        return JSONResponse(content={"palettes": palettes})
    except Exception as e:
        logger.error(f"Error fetching color palettes: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching color palettes")

@router.get("/skin-tone-guide")
async def get_skin_tone_guide():
    """Get educational information about skin tones and color theory."""
    guide = {
        "skin_tone_categories": {
            "fair": {
                "description": "Light skin with pink, red, or blue undertones",
                "characteristics": ["Burns easily", "May have freckles", "Visible veins appear blue/purple"]
            },
            "light": {
                "description": "Light to medium skin with various undertones",
                "characteristics": ["Burns moderately", "Tans gradually", "Mixed vein colors"]
            },
            "medium": {
                "description": "Medium skin with warm or cool undertones",
                "characteristics": ["Tans well", "Rarely burns", "Olive or golden tones"]
            },
            "dark": {
                "description": "Deep skin with rich undertones",
                "characteristics": ["Rarely burns", "Rich pigmentation", "Golden, red, or blue undertones"]
            }
        },
        "undertone_types": {
            "cool": {
                "description": "Pink, red, or blue undertones",
                "best_colors": ["Blues", "Purples", "Emerald greens", "True reds"]
            },
            "warm": {
                "description": "Yellow, golden, or peachy undertones",
                "best_colors": ["Oranges", "Yellows", "Warm reds", "Earth tones"]
            },
            "neutral": {
                "description": "Balanced mix of warm and cool undertones",
                "best_colors": ["Most colors work well", "Focus on saturation and brightness"]
            }
        }
    }
    return JSONResponse(content=guide)