import math

def meters_to_degrees_latitude(meters):
    return meters / 111320


def meters_to_degrees_longitude(meters, latitude):
    return meters / (111320 * math.cos(math.radians(latitude)))