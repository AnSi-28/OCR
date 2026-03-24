from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from PIL import Image
import torch

processor = TrOCRProcessor.from_pretrained("microsoft/trocr-base-printed")
model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-base-printed")

device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)


def extract_text(image_path: str) -> str:
    image = Image.open(image_path).convert("RGB")

    pixel_values = processor(
        images=image,
        return_tensors="pt"
    ).pixel_values.to(device)

    # 🔥 Beam search (better decoding)
    generated_ids = model.generate(
        pixel_values,
        num_beams=5,
        max_length=64,
        early_stopping=True
    )

    text = processor.batch_decode(
        generated_ids,
        skip_special_tokens=True
    )[0]

    return text.strip()