import math

from lat_lon_to_pixels import lat_lon_to_pixels, pixels_to_lat_lon


class TestLatLonToPixels:
    def test_center_point_returns_center_pixel(self):
        """Center lat/lon should return center pixel (w/2, h/2)."""
        center = (40.0, -74.0)  # NYC
        size = (100, 100)
        result = lat_lon_to_pixels(center, center, size)
        assert result == (50.0, 50.0)

    def test_top_left_returns_origin(self):
        """Point at top-left of the image should return (0, 0)."""
        center = (0.0, 0.0)
        size = (100, 100)
        # Top-left in image coords (0,0) corresponds to lat=90, lon=-180
        lat_lon = (90.0, -180.0)
        result = lat_lon_to_pixels(lat_lon, center, size)
        assert result == (0.0, 0.0)

    def test_bottom_right_returns_max_pixels(self):
        """Point at bottom-right of the image should return (w, h)."""
        center = (0.0, 0.0)
        size = (100, 100)
        lat_lon = (-90.0, 180.0)
        result = lat_lon_to_pixels(lat_lon, center, size)
        assert result == (100.0, 100.0)

    def test_non_center_coordinates(self):
        """Test a point offset from center."""
        center = (40.0, -74.0)  # NYC
        size = (360, 180)
        # Move 1 degree east should increase x by 1 pixel
        lat_lon = (40.0, -73.0)
        result = lat_lon_to_pixels(lat_lon, center, size)
        assert result[0] == pytest.approx(181.0, rel=1e-6)
        assert result[1] == pytest.approx(90.0, rel=1e-6)


class TestPixelsToLatLon:
    def test_center_pixel_returns_center_lat_lon(self):
        """Center pixel (w/2, h/2) should return the center lat/lon."""
        center = (40.0, -74.0)  # NYC
        size = (100, 100)
        result = pixels_to_lat_lon((50.0, 50.0), center, size)
        assert result == (40.0, -74.0)

    def test_origin_returns_top_left_lat_lon(self):
        """Pixel (0, 0) should return top-left lat/lon."""
        center = (0.0, 0.0)
        size = (100, 100)
        # Pixel (0,0) is top-left, which is lat=90, lon=-180
        result = pixels_to_lat_lon((0.0, 0.0), center, size)
        assert result == (90.0, -180.0)

    def test_max_pixels_returns_bottom_right(self):
        """Pixel (w, h) should return bottom-right lat/lon."""
        center = (0.0, 0.0)
        size = (100, 100)
        # Pixel (w, h) is bottom-right, which is lat=-90, lon=180
        result = pixels_to_lat_lon((100.0, 100.0), center, size)
        assert result == (-90.0, 180.0)


class TestRoundTrip:
    """Test that converting lat/lon to pixels and back gives the original value."""

    def test_roundtrip_center(self):
        center = (40.0, -74.0)
        size = (100, 100)
        original = (40.0, -74.0)

        pixels = lat_lon_to_pixels(original, center, size)
        result = pixels_to_lat_lon(pixels, center, size)
        assert result == original

    def test_roundtrip_various_points(self):
        center = (0.0, 0.0)
        size = (360, 180)

        test_points = [
            (0.0, 0.0),
            (45.0, 90.0),
            (-45.0, -90.0),
            (80.0, 170.0),
            (-80.0, -170.0),
        ]

        for original in test_points:
            pixels = lat_lon_to_pixels(original, center, size)
            result = pixels_to_lat_lon(pixels, center, size)
            assert result == pytest.approx(original, rel=1e-6)


import pytest

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
