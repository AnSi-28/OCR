import cv2

def extract_text_regions(image_path):
    img = cv2.imread(image_path)

    if img is None:
        raise ValueError("Image not loaded")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Threshold
    thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)[1]

    # Dilate to connect text lines
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 3))
    dilated = cv2.dilate(thresh, kernel, iterations=1)

    # Find contours (text regions)
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    regions = []

    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)

        # Filter noise
        if w > 50 and h > 15:
            regions.append((x, y, w, h))

    # Sort top to bottom
    regions = sorted(regions, key=lambda x: x[1])

    return img, regions

def sort_regions(regions):
    regions = sorted(regions, key=lambda x: x[1])

    lines = []
    current_line = []
    threshold = 20

    for box in regions:
        if not current_line:
            current_line.append(box)
            continue

        if abs(box[1] - current_line[0][1]) < threshold:
            current_line.append(box)
        else:
            current_line = sorted(current_line, key=lambda x: x[0])
            lines.append(current_line)
            current_line = [box]

    if current_line:
        current_line = sorted(current_line, key=lambda x: x[0])
        lines.append(current_line)

    return lines