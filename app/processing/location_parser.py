class LocationParser:
    @staticmethod
    def extract_country(location: str | None) -> str:
        if not location:
            return ""

        parts = [part.strip() for part in location.split(",") if part.strip()]
        if not parts:
            return ""

        return parts[-1].lower()