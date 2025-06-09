from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse
from typing import List, Optional
import os
import tempfile
import shutil
import time
from pathlib import Path
import SimpleITK as sitk
import numpy as np
from PIL import Image
import uuid
import logging
import base64
from io import BytesIO

from open_webui.models.users import User
from open_webui.utils.auth import get_current_user
from open_webui.storage.provider import Storage
from open_webui.config import UPLOAD_DIR


router = APIRouter(tags=["ct"])

# Create a temporary directory for storing converted images
TEMP_DIR = os.path.join(tempfile.gettempdir(), "ct_conversions")
TEMP_DIR = Path(TEMP_DIR)
TEMP_DIR.mkdir(exist_ok=True)

def convert_ct_to_images(mhd_path: str, raw_path: str) -> List[dict]:
    """
    Convert CT scan files to a list of base64 encoded PNG images.
    Returns a list of dictionaries containing base64 encoded images and metadata.
    """
    try:
        # Read the CT scan using SimpleITK
        try:
            reader = sitk.ImageFileReader()
            reader.SetFileName(mhd_path)
            image = reader.Execute()
        except Exception as e:
            logging.error(f"Failed to read MHD file {mhd_path}: {e}")
            raise HTTPException(status_code=400, detail=f"Invalid MHD file: {e}")

        # Get the number of slices
        size = image.GetSize()
        num_slices = size[2] if len(size) > 2 else 1

        images = []
        for i in range(num_slices):
            try:
                # Extract the slice
                if len(size) > 2:
                    slice_image = image[:, :, i]
                else:
                    slice_image = image

                # Convert to numpy array and normalize
                array = sitk.GetArrayFromImage(slice_image)
                array = ((array - array.min()) * (255.0 / (array.max() - array.min()))).astype(np.uint8)

                # Convert to PIL Image
                pil_image = Image.fromarray(array)

                # Convert to base64
                buffered = BytesIO()
                pil_image.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode()

                # Add to the list of images
                images.append({
                    "data": f"data:image/png;base64,{img_str}",
                    "slice_index": i
                })
            except Exception as e:
                logging.error(f"Failed to process slice {i}: {e}")
                raise HTTPException(status_code=500, detail=f"Error processing slice {i}: {e}")

        return images

    except HTTPException:
        raise # Re-raise HTTPExceptions that were already formed
    except Exception as e:
        logging.error(f"Unhandled error in convert_ct_to_images: {e}")
        raise HTTPException(status_code=500, detail=f"Error converting CT scan: {str(e)}")

@router.post("/convert")
async def convert_ct_files(
    request: Request,
    mhd_filename: str,  # expected to be the filename like 'scan.mhd'
    raw_filename: str,  # expected to be the filename like 'scan.raw'
    current_user: User = Depends(get_current_user)
):
    """
    Convert CT scan files to base64 encoded image slices.
    The file IDs passed should be the actual filenames stored in UPLOAD_DIR.
    """
    try:
        # Get the full file paths from the filenames
        try:
            mhd_path = Storage.get_file(f"{UPLOAD_DIR}/{mhd_filename}")
            raw_path = Storage.get_file(f"{UPLOAD_DIR}/{raw_filename}")
            logging.debug(f"DEBUG: Resolved mhd_path: {mhd_path}, raw_path: {raw_path}")
        except Exception as e:
            logging.error(f"Failed to retrieve files from storage: {e}")
            raise HTTPException(status_code=404, detail=f"File not found or accessible: {e}")

        # Validate that files exist
        if not os.path.exists(mhd_path) or not os.path.exists(raw_path):
            logging.warning(f"File existence check failed: MHD exists={os.path.exists(mhd_path)}, RAW exists={os.path.exists(raw_path)}")
            raise HTTPException(status_code=404, detail="One or both CT files not found on backend storage")

        # Update the MHD file to point to the correct RAW file
        try:
            with open(mhd_path, 'r') as f:
                mhd_content = f.read()
            
            # Replace the ElementDataFile line with the correct RAW filename
            mhd_content = mhd_content.replace(
                f"ElementDataFile = {os.path.basename(raw_path).split('_', 1)[1]}",
                f"ElementDataFile = {os.path.basename(raw_path)}"
            )
            
            with open(mhd_path, 'w') as f:
                f.write(mhd_content)
        except Exception as e:
            logging.error(f"Failed to update MHD file: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to update MHD file: {e}")

        # Perform conversion
        images = convert_ct_to_images(mhd_path, raw_path)
        return {"images": images}

    except HTTPException:
        raise  # FastAPI-friendly error already raised
    except Exception as e:
        logging.error(f"Unhandled error in convert_ct_files: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error during CT conversion: {str(e)}")


@router.get("/images/{conversion_id}/{filename}")
async def get_converted_image(
    conversion_id: str,
    filename: str,
    token: str = None,
    current_user: User = Depends(get_current_user)
):
    """
    Serve a converted CT scan image.
    """
    try:
        image_path = TEMP_DIR / conversion_id / filename
        if not image_path.exists():
            logging.warning(f"Image not found at {image_path}")
            raise HTTPException(status_code=404, detail="Image not found")

        try:
            # Set proper permissions before serving
            os.chmod(image_path, 0o644)
            return FileResponse(
                str(image_path),
                media_type="image/png",
                headers={"Cache-Control": "no-cache"}
            )
        except Exception as e:
            logging.error(f"Failed to serve image {image_path}: {e}")
            raise HTTPException(status_code=500, detail=f"Error serving image: {e}")

    except HTTPException:
        raise # Re-raise HTTPExceptions that were already formed
    except Exception as e:
        logging.error(f"Unhandled error in get_converted_image endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error when fetching image: {str(e)}")

def delete_conversion_directory(conversion_id: str) -> bool:
    """
    Delete a specific conversion directory and its contents.
    Returns True if successful, False otherwise.
    """
    try:
        conversion_dir = TEMP_DIR / conversion_id
        if conversion_dir.exists():
            shutil.rmtree(conversion_dir)
            logging.info(f"Deleted conversion directory: {conversion_dir}")
            return True
        return False
    except Exception as e:
        logging.error(f"Failed to delete conversion directory {conversion_id}: {e}")
        return False

def cleanup_old_conversions():
    """
    Remove conversion directories older than 24 hours.
    """
    try:
        current_time = time.time()
        for item in TEMP_DIR.iterdir():
            try:
                if item.is_dir():
                    # Check if directory is older than 24 hours
                    if current_time - item.stat().st_mtime > 86400:  # 24 hours in seconds
                        shutil.rmtree(item)
                        logging.info(f"Cleaned up old conversion directory: {item}")
            except Exception as e:
                logging.error(f"Error cleaning up item {item}: {str(e)}")
    except Exception as e:
        logging.error(f"Unhandled error during cleanup_old_conversions: {str(e)}")

# Add this to your chat deletion endpoint or wherever you handle chat deletion
@router.delete("/conversions/{conversion_id}")
async def delete_conversion(
    conversion_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Delete a specific conversion directory and its contents.
    """
    try:
        if delete_conversion_directory(conversion_id):
            return {"message": "Conversion deleted successfully"}
        raise HTTPException(status_code=404, detail="Conversion not found")
    except Exception as e:
        logging.error(f"Error deleting conversion {conversion_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete conversion: {str(e)}")