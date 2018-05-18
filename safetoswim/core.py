import numpy as np
import math
import PIL
from keras.applications import ResNet50
import io
from keras.preprocessing.image import img_to_array
from keras.applications import imagenet_utils
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

class PhotoProcessor(object):
    def __init__(self, image):
        self._image = Image.open(io.BytesIO(image))
        self.gps_data = {}
        self.exif_data = {}
        self.get_exif_data(self._image)
        self.latitude, self.longitude = self.get_lat_lon(self.exif_data)

    def get_exif_data(self, image):
        """Returns a dictionary from the exif data of an PIL Image item. Also converts the GPS Tags"""
        info = image._getexif()
        if info:
            for tag, value in info.items():
                decoded = TAGS.get(tag, tag)
                if decoded == "GPSInfo":
                    for t in value:
                        sub_decoded = GPSTAGS.get(t, t)
                        self.gps_data[sub_decoded] = value[t]

                    self.exif_data[decoded] = self.gps_data
                else:
                    self.exif_data[decoded] = value

    def _convert_to_degress(self, value):
        """Helper function to convert the GPS coordinates stored in the EXIF to degress in float format"""
        deg_num, deg_denom = value[0]
        d = float(deg_num) / float(deg_denom)

        min_num, min_denom = value[1]
        m = float(min_num) / float(min_denom)

        sec_num, sec_denom = value[2]
        s = float(sec_num) / float(sec_denom)

        return round(d + (m / 60.0) + (s / 3600.0), 5)

    def get_lat_lon(self, exif_data):
        """Returns the latitude and longitude, if available, from the provided exif_data (obtained through get_exif_data above)"""
        lat = None
        lon = None

        if "GPSInfo" in exif_data:
            gps_info = exif_data["GPSInfo"]

            gps_latitude = gps_info.get("GPSLatitude")
            gps_latitude_ref = gps_info.get('GPSLatitudeRef')
            gps_longitude = gps_info.get('GPSLongitude')
            gps_longitude_ref = gps_info.get('GPSLongitudeRef')

            if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
                lat = self._convert_to_degress(gps_latitude)
                if gps_latitude_ref != "N":
                    lat *= -1

                lon = self._convert_to_degress(gps_longitude)
                if gps_longitude_ref != "E":
                    lon *= -1

        return lat, lon

    def prepare_rgb_data(self, img_size):
        rgb_data = None
        if self._image.mode != 'RGB':
            rgb_data = self._image.convert('RGB ')
        else:
            rgb_data = self._image

        rgb_data = rgb_data.resize(img_size)
        rgb_data = img_to_array(rgb_data)
        rgb_data = np.expand_dims(rgb_data, axis=0)
        rgb_data = imagenet_utils.preprocess_input(rgb_data)

        return rgb_data