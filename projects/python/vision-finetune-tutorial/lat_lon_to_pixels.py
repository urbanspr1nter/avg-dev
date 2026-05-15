import math


def lat_lon_to_pixels(lat_lon, center_lat_lon, image_size):
    """
    Convert a latitude, longitude coordinate to pixel coordinates.

    Args:
        lat_lon: tuple (lat, lon) of the location to convert
        center_lat_lon: tuple (lat, lon) of the image center
        image_size: tuple (w, h) width, height in pixels of the image

    Returns:
        tuple (x, y) pixel coordinates
    """
    lat, lon = lat_lon
    center_lat, center_lon = center_lat_lon
    w, h = image_size

    # Pixel scale: degrees per pixel (approximate, varies with latitude)
    # 360 degrees of longitude spans the image width
    degrees_per_pixel_x = 360.0 / w
    degrees_per_pixel_y = 180.0 / h  # 180 degrees of latitude spans the image height

    # Calculate offset from center
    delta_lon = lon - center_lon
    delta_lat = lat - center_lat

    # Convert to pixels relative to center, then offset to image coordinates
    # Center of image is at (w/2, h/2)
    x = w / 2 + delta_lon / degrees_per_pixel_x
    y = (
        h / 2 - delta_lat / degrees_per_pixel_y
    )  # Note: y is inverted (lat increases upward)

    return (x, y)


def pixels_to_lat_lon(pixels, center_lat_lon, image_size):
    """
    Convert pixel coordinates to latitude, longitude.

    Args:
        pixels: tuple (x, y) pixel coordinates
        center_lat_lon: tuple (lat, lon) of the image center
        image_size: tuple (w, h) width, height in pixels of the image

    Returns:
        tuple (lat, lon) coordinates
    """
    x, y = pixels
    center_lat, center_lon = center_lat_lon
    w, h = image_size

    # Pixel scale: degrees per pixel
    degrees_per_pixel_x = 360.0 / w
    degrees_per_pixel_y = 180.0 / h

    # Convert pixel offset from center to degrees
    delta_lon = (x - w / 2) * degrees_per_pixel_x
    delta_lat = (h / 2 - y) * degrees_per_pixel_y  # Note: y is inverted

    # Add to center coordinates
    lon = center_lon + delta_lon
    lat = center_lat + delta_lat

    return (lat, lon)
