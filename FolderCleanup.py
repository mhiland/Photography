import os
import shutil
from PIL import Image
import pyheif
import piexif
from PIL.ExifTags import TAGS
import datetime
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata
import pillow_heif

# Configurable source and destination directories
#source_directory = '/Volumes/home/Photos/2021/09/'  
source_directory = '/Users/mhiland/Pictures/Camera Roll Backup/2024'
destination_directory = '/Volumes/home/Photos'

def get_heic_creation_date(image_path):
    try:
        heif_file = pillow_heif.open_heif(image_path)
        exif_dict = piexif.load(heif_file.info['exif'])
        creation_date = exif_dict.get('Exif', {}).get(piexif.ExifIFD.DateTimeOriginal)
        if creation_date:
            return creation_date.decode('utf-8')
        else:
            print("No creation date found")
            return None
    except Exception as e:
        print(f"Error reading creation date for {image_path}: {e}")
        return None

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

def get_mov_creation_date(file_path):
    try:
        parser = createParser(file_path)
        if not parser:
            print(f"Unable to create parser for {file_path}")
            return None
        
        with parser:
            metadata = extractMetadata(parser)
            if not metadata:
                print(f"No metadata found for {file_path}")
                return None
            
            # Extract specific metadata
            for line in metadata.exportPlaintext():
                if "Creation date" in line:
                    return line.split(':', 1)[1].strip()

    except Exception as e:
        print(f"Error reading metadata for {file_path}: {e}")
        return None

# Function to extract creation date from photo metadata
def get_creation_date(image_path):
    exif_creation_date = None
    try:
        # Handle RAW files separately as PIL doesn't support them
        if image_path.lower().endswith(('.raf','.json')):
            # For Fuji RAW files, use file's modified time as a fallback
            return datetime.datetime.fromtimestamp(os.path.getmtime(image_path))
        elif image_path.lower().endswith('.heic'):
            value = get_heic_creation_date(image_path)
            exif_creation_date = datetime.datetime.strptime(value, '%Y:%m:%d %H:%M:%S')
        elif image_path.lower().endswith('.mov'):
            value = get_mov_creation_date(image_path)
            exif_creation_date = datetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        else:
            value = get_exif_data(image_path)
            exif_creation_date = datetime.datetime.strptime(value, '%Y:%m:%d %H:%M:%S')
    except Exception as e:
        print(f"Error reading EXIF data for {image_path}: {e}")
    return exif_creation_date

# Function to organize photos
def organize_photos(src_directory, dest_directory):
    for root, dirs, files in os.walk(src_directory):
        for file in files:
            # Filter for common image files and Fuji RAW filesß
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif', '.raf', '.mov', '.json', '.heic')):
                file_path = os.path.join(root, file)
                
                # Get creation date from EXIF or file's modified time for RAW files
                exif_date = get_creation_date(file_path)
                # Get last modified date
                modified_date = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
                # Use the earlier of the two dates, if both are available
                use_date = min(filter(None, [exif_date, modified_date]))
                
                if use_date is not None:
                    # Construct year and month directories in the destination folder
                    year_dir = os.path.join(dest_directory, str(use_date.year))
                    month_dir = os.path.join(year_dir, f"{str(use_date.month).zfill(2)}")
                    
                    if not os.path.exists(year_dir):
                        os.makedirs(year_dir)
                    if not os.path.exists(month_dir):
                        os.makedirs(month_dir)
                    
                    # Move the file
                    destination_path = os.path.join(month_dir, file)
                    shutil.copy(file_path, destination_path)
                    print(f"Moved {file} to {destination_path}")

# Ensure the destination directory exists
if not os.path.exists(destination_directory):
    os.makedirs(destination_directory)

# Call the function with your configured paths
organize_photos(source_directory, destination_directory)
