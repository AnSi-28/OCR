from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
import shutil
import os
import uuid
from fastapi.middleware.cors import CORSMiddleware
import cv2

from ocr import extract_text
from preprocessing import extract_text_regions, sort_regions

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
PROCESSED_DIR = "processed"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

app.mount("/processed", StaticFiles(directory=PROCESSED_DIR), name="processed")


@app.post("/upload/")
async def upload_image(file: UploadFile = File(...)):
    try:
        file_id = str(uuid.uuid4())
        file_path = os.path.join(UPLOAD_DIR, f"{file_id}.jpg")

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        img, regions = extract_text_regions(file_path)
        lines = sort_regions(regions)

        final_text = ""

        boxed_img = img.copy()

        for line in lines:
            for (x, y, w, h) in line:

                # 🔥 Add padding
                pad = 10
                x1 = max(0, x - pad)
                y1 = max(0, y - pad)
                x2 = min(img.shape[1], x + w + pad)
                y2 = min(img.shape[0], y + h + pad)

                crop = img[y1:y2, x1:x2]

                # 🔥 Mild upscale (safe)
                crop = cv2.resize(
                    crop,
                    None,
                    fx=1.3,
                    fy=1.3,
                    interpolation=cv2.INTER_CUBIC
                )

                crop_path = os.path.join(PROCESSED_DIR, f"crop_{x}_{y}.png")
                cv2.imwrite(crop_path, crop)

                text = extract_text(crop_path)
                final_text += text + " "

                # Draw rectangle (original box)
                cv2.rectangle(
                    boxed_img,
                    (x, y),
                    (x + w, y + h),
                    (0, 255, 0),
                    2
                )

            final_text += "\n"

        output_image_path = os.path.join(PROCESSED_DIR, f"{file_id}_boxed.jpg")
        cv2.imwrite(output_image_path, boxed_img)

        return {
            "extracted_text": final_text.strip(),
            "image_url": f"http://127.0.0.1:8000/processed/{file_id}_boxed.jpg"
        }

    except Exception as e:
        return {"error": str(e)}