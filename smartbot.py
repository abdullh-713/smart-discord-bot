from transformers import ViTFeatureExtractor, ViTForImageClassification
from PIL import Image
import torch
import requests
from io import BytesIO

# تحميل النموذج الجاهز
model_name = "google/vit-base-patch16-224"
feature_extractor = ViTFeatureExtractor.from_pretrained(model_name)
model = ViTForImageClassification.from_pretrained(model_name)

# تحميل صورة للتجربة
image_url = "https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/transformers/tasks/image_classification.jpeg"
image = Image.open(BytesIO(requests.get(image_url).content))

# تجهيز الصورة
inputs = feature_extractor(images=image, return_tensors="pt")

# توقع النتيجة
with torch.no_grad():
    outputs = model(**inputs)
    logits = outputs.logits
    predicted_class_idx = logits.argmax(-1).item()

# عرض التصنيف
print(model.config.id2label[predicted_class_idx])
