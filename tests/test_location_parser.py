from app.processing.location_parser import LocationParser


def test_extract_country_returns_last_part_lowercase():
    location = "Berlin, Germany"
    result = LocationParser.extract_country(location)
    assert result == "germany"


def test_extract_country_returns_empty_string_when_location_is_none():
    result = LocationParser.extract_country(None)
    assert result == ""


def test_extract_country_returns_empty_string_when_location_is_blank():
    result = LocationParser.extract_country("   ")
    assert result == ""


def test_extract_country_handles_multiple_parts():
    location = "Tokyo, Kanto, Japan"
    result = LocationParser.extract_country(location)
    assert result == "japan"