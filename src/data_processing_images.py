import aspose.ocr as ocr

# Instantiate Aspose.OCR API
api = ocr.AsposeOcr()

# Add image to the recognition batch
input = ocr.OcrInput(ocr.InputType.SINGLE_IMAGE)
input.add("../data/Pasabordo5.jpg")

# Recognize the image
result = api.recognize(input)

# Print recognition result
print(result[0].recognition_text)