from PIL import Image
import pillow_heif
import piexif
from PIL.ExifTags import TAGS
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata

pillow_heif.register_heif_opener()

def get_exif_data(image_path):
    try:
        image = Image.open(image_path)
        exif_data = piexif.load(image.info['exif'])
        date_time_original = exif_data['Exif'][piexif.ExifIFD.DateTimeOriginal].decode('utf-8')
        return date_time_original
    except KeyError:
        print(f"No EXIF data found for {image_path}")
        return None
    except Exception as e:
        print(f"Error reading EXIF data for {image_path}: {e}")
        return None

heic_image_path = "/Users/mhiland/Pictures/Camera Roll Backup/2021/09 - Sep/fb97342d0b03c57c-photo-full.jpg"
exif_data = get_exif_data(heic_image_path)
if exif_data:
    print(exif_data)
