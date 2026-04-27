import base64
import uuid

from django.core.files.base import ContentFile
from rest_framework import serializers


class Base64ImageField(serializers.ImageField):
    """Поле для загрузки изображений в формате base64."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format_info, image_string = data.split(';base64,')
            extension = format_info.split('/')[-1]

            file_name = f'{uuid.uuid4()}.{extension}'
            data = ContentFile(
                base64.b64decode(image_string),
                name=file_name,
            )

        return super().to_internal_value(data)
