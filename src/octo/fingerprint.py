"""
Fingerprint management module for Octo Browser.

Provides fingerprint generation and customization.
"""

from typing import List, Optional, Dict, Any
import random
from loguru import logger

from src.octo.models import Fingerprint


class FingerprintGenerator:
    """Browser fingerprint generator."""

    # Common screen resolutions
    SCREEN_RESOLUTIONS = [
        "1920x1080",
        "1366x768",
        "1536x864",
        "1440x900",
        "1280x720",
        "2560x1440",
        "3840x2160",
        "1600x900",
        "1280x800",
        "1024x768",
    ]

    # Common platforms
    PLATFORMS = [
        "Win32",
        "MacIntel",
        "Linux x86_64",
        "Linux i686",
    ]

    # Common user agents
    USER_AGENTS = [
        # Chrome Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        # Chrome macOS
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        # Chrome Linux
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        # Edge Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
        # Firefox Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        # Firefox macOS
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
    ]

    # Common WebGL vendors/renderers
    WEBGL_CONFIGS = [
        {"vendor": "Intel Inc.", "renderer": "Intel Iris OpenGL Engine"},
        {"vendor": "NVIDIA Corporation", "renderer": "NVIDIA GeForce GTX 1060/PCIe/SSE2"},
        {"vendor": "AMD", "renderer": "AMD Radeon RX 580 Series"},
        {"vendor": "Intel Inc.", "renderer": "Intel(R) UHD Graphics 630"},
        {"vendor": "Google Inc. (Intel)", "renderer": "ANGLE (Intel, Intel(R) UHD Graphics 630 Direct3D11 vs_5_0 ps_5_0)"},
    ]

    # Common timezones
    TIMEZONES = [
        "America/New_York",
        "America/Chicago",
        "America/Denver",
        "America/Los_Angeles",
        "Europe/London",
        "Europe/Paris",
        "Europe/Berlin",
        "Asia/Tokyo",
        "Asia/Shanghai",
        "Australia/Sydney",
    ]

    # Common languages
    LANGUAGES = [
        ["en-US", "en"],
        ["en-GB", "en"],
        ["de-DE", "de", "en-US", "en"],
        ["fr-FR", "fr", "en-US", "en"],
        ["es-ES", "es", "en-US", "en"],
        ["ja-JP", "ja", "en-US", "en"],
        ["zh-CN", "zh", "en-US", "en"],
    ]

    # Hardware configurations
    HARDWARE_CONFIGS = [
        {"concurrency": 4, "memory": 4},
        {"concurrency": 8, "memory": 8},
        {"concurrency": 12, "memory": 16},
        {"concurrency": 16, "memory": 32},
        {"concurrency": 6, "memory": 8},
    ]

    def __init__(self):
        """Initialize fingerprint generator."""
        logger.info("FingerprintGenerator initialized")

    def generate_random(self) -> Fingerprint:
        """Generate random fingerprint.

        Returns:
            Random fingerprint configuration
        """
        fp = Fingerprint()

        # Screen
        fp.screen_resolution = random.choice(self.SCREEN_RESOLUTIONS)
        fp.screen_color_depth = random.choice([24, 32])

        # WebGL
        webgl_config = random.choice(self.WEBGL_CONFIGS)
        fp.webgl_vendor = webgl_config["vendor"]
        fp.webgl_renderer = webgl_config["renderer"]

        # Noise
        fp.canvas_noise = True
        fp.audio_noise = True

        # Navigator
        fp.user_agent = random.choice(self.USER_AGENTS)
        fp.platform = random.choice(self.PLATFORMS)

        # Languages
        languages = random.choice(self.LANGUAGES)
        fp.language = languages[0]
        fp.languages = languages

        # Hardware
        hw_config = random.choice(self.HARDWARE_CONFIGS)
        fp.hardware_concurrency = hw_config["concurrency"]
        fp.device_memory = hw_config["memory"]

        # Timezone
        fp.timezone = random.choice(self.TIMEZONES)

        logger.debug("Generated random fingerprint")
        return fp

    def generate_consistent(self, seed: int) -> Fingerprint:
        """Generate consistent fingerprint based on seed.

        Args:
            seed: Random seed

        Returns:
            Fingerprint configuration
        """
        # Use seed for consistent random
        rng = random.Random(seed)

        fp = Fingerprint()

        # Screen
        fp.screen_resolution = rng.choice(self.SCREEN_RESOLUTIONS)
        fp.screen_color_depth = rng.choice([24, 32])

        # WebGL
        webgl_config = rng.choice(self.WEBGL_CONFIGS)
        fp.webgl_vendor = webgl_config["vendor"]
        fp.webgl_renderer = webgl_config["renderer"]

        # Noise
        fp.canvas_noise = True
        fp.audio_noise = True

        # Navigator
        fp.user_agent = rng.choice(self.USER_AGENTS)
        fp.platform = rng.choice(self.PLATFORMS)

        # Languages
        languages = rng.choice(self.LANGUAGES)
        fp.language = languages[0]
        fp.languages = languages

        # Hardware
        hw_config = rng.choice(self.HARDWARE_CONFIGS)
        fp.hardware_concurrency = hw_config["concurrency"]
        fp.device_memory = hw_config["memory"]

        # Timezone
        fp.timezone = rng.choice(self.TIMEZONES)

        logger.debug(f"Generated consistent fingerprint with seed {seed}")
        return fp

    def generate_for_location(self, country_code: str) -> Fingerprint:
        """Generate fingerprint for specific location.

        Args:
            country_code: Country code (US, GB, DE, etc.)

        Returns:
            Location-appropriate fingerprint
        """
        fp = self.generate_random()

        # Set timezone and language based on country
        location_config = {
            "US": {
                "timezones": ["America/New_York", "America/Chicago", "America/Los_Angeles"],
                "languages": [["en-US", "en"]],
            },
            "GB": {
                "timezones": ["Europe/London"],
                "languages": [["en-GB", "en"]],
            },
            "DE": {
                "timezones": ["Europe/Berlin"],
                "languages": [["de-DE", "de", "en-US", "en"]],
            },
            "FR": {
                "timezones": ["Europe/Paris"],
                "languages": [["fr-FR", "fr", "en-US", "en"]],
            },
            "JP": {
                "timezones": ["Asia/Tokyo"],
                "languages": [["ja-JP", "ja", "en-US", "en"]],
            },
            "CN": {
                "timezones": ["Asia/Shanghai"],
                "languages": [["zh-CN", "zh", "en-US", "en"]],
            },
        }

        config = location_config.get(country_code.upper())

        if config:
            fp.timezone = random.choice(config["timezones"])
            languages = random.choice(config["languages"])
            fp.language = languages[0]
            fp.languages = languages
        else:
            logger.warning(f"Unknown country code: {country_code}, using default")

        logger.debug(f"Generated fingerprint for {country_code}")
        return fp

    def generate_mobile(self) -> Fingerprint:
        """Generate mobile device fingerprint.

        Returns:
            Mobile fingerprint configuration
        """
        fp = Fingerprint()

        # Mobile screen resolutions
        mobile_resolutions = [
            "390x844",  # iPhone 13
            "393x851",  # Pixel 6
            "412x915",  # Samsung Galaxy S21
            "360x780",  # Common Android
        ]

        fp.screen_resolution = random.choice(mobile_resolutions)
        fp.screen_color_depth = 24

        # Mobile user agents
        mobile_ua = [
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (Linux; Android 13; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
            "Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
        ]

        fp.user_agent = random.choice(mobile_ua)

        # Mobile platform
        if "iPhone" in fp.user_agent:
            fp.platform = "iPhone"
        else:
            fp.platform = "Linux armv8l"

        # Mobile hardware
        fp.hardware_concurrency = random.choice([4, 6, 8])
        fp.device_memory = random.choice([2, 4, 6, 8])

        # Languages
        languages = random.choice(self.LANGUAGES)
        fp.language = languages[0]
        fp.languages = languages

        # Timezone
        fp.timezone = random.choice(self.TIMEZONES)

        # Noise
        fp.canvas_noise = True
        fp.audio_noise = True

        logger.debug("Generated mobile fingerprint")
        return fp

    def customize_fingerprint(
        self,
        base: Optional[Fingerprint] = None,
        **overrides,
    ) -> Fingerprint:
        """Customize fingerprint with specific values.

        Args:
            base: Base fingerprint (None = random)
            **overrides: Fields to override

        Returns:
            Customized fingerprint
        """
        fp = base or self.generate_random()

        # Apply overrides
        for key, value in overrides.items():
            if hasattr(fp, key):
                setattr(fp, key, value)
            else:
                logger.warning(f"Unknown fingerprint field: {key}")

        logger.debug("Customized fingerprint")
        return fp

    def clone_fingerprint(self, source: Fingerprint) -> Fingerprint:
        """Clone fingerprint.

        Args:
            source: Source fingerprint

        Returns:
            Cloned fingerprint
        """
        return Fingerprint.from_dict(source.to_dict())

    def generate_batch(self, count: int, unique: bool = True) -> List[Fingerprint]:
        """Generate batch of fingerprints.

        Args:
            count: Number of fingerprints
            unique: Whether to ensure uniqueness

        Returns:
            List of fingerprints
        """
        fingerprints: List[Fingerprint] = []

        if unique:
            # Use seeds for consistent unique fingerprints
            for i in range(count):
                fp = self.generate_consistent(seed=i)
                fingerprints.append(fp)
        else:
            # Generate random
            for _ in range(count):
                fp = self.generate_random()
                fingerprints.append(fp)

        logger.info(f"Generated batch of {count} fingerprints (unique={unique})")
        return fingerprints

    def validate_fingerprint(self, fp: Fingerprint) -> Dict[str, Any]:
        """Validate fingerprint configuration.

        Args:
            fp: Fingerprint to validate

        Returns:
            Validation result
        """
        errors = []
        warnings = []

        # Check screen resolution
        if fp.screen_resolution:
            if "x" not in fp.screen_resolution:
                errors.append("Invalid screen resolution format")
            else:
                try:
                    width, height = fp.screen_resolution.split("x")
                    w, h = int(width), int(height)
                    if w <= 0 or h <= 0:
                        errors.append("Screen resolution must be positive")
                except ValueError:
                    errors.append("Invalid screen resolution values")

        # Check color depth
        if fp.screen_color_depth not in [24, 32]:
            warnings.append("Color depth should be 24 or 32")

        # Check hardware
        if fp.hardware_concurrency and fp.hardware_concurrency <= 0:
            errors.append("Hardware concurrency must be positive")

        if fp.device_memory and fp.device_memory <= 0:
            errors.append("Device memory must be positive")

        # Check language
        if not fp.language:
            warnings.append("Language not set")

        if not fp.languages:
            warnings.append("Languages list is empty")

        # Check timezone
        if not fp.timezone:
            warnings.append("Timezone not set")

        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
        }

    def get_fingerprint_summary(self, fp: Fingerprint) -> str:
        """Get human-readable fingerprint summary.

        Args:
            fp: Fingerprint

        Returns:
            Summary string
        """
        lines = [
            f"Screen: {fp.screen_resolution} ({fp.screen_color_depth}-bit)",
            f"Platform: {fp.platform}",
            f"Language: {fp.language}",
            f"Timezone: {fp.timezone}",
            f"Hardware: {fp.hardware_concurrency} cores, {fp.device_memory}GB RAM",
        ]

        if fp.webgl_vendor:
            lines.append(f"WebGL: {fp.webgl_vendor} - {fp.webgl_renderer}")

        if fp.canvas_noise or fp.audio_noise:
            noise = []
            if fp.canvas_noise:
                noise.append("canvas")
            if fp.audio_noise:
                noise.append("audio")
            lines.append(f"Noise: {', '.join(noise)}")

        return "\n".join(lines)


# Preset fingerprints
class FingerprintPresets:
    """Predefined fingerprint presets."""

    @staticmethod
    def windows_chrome() -> Fingerprint:
        """Windows + Chrome fingerprint."""
        fp = Fingerprint()
        fp.screen_resolution = "1920x1080"
        fp.screen_color_depth = 24
        fp.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        fp.platform = "Win32"
        fp.language = "en-US"
        fp.languages = ["en-US", "en"]
        fp.hardware_concurrency = 8
        fp.device_memory = 8
        fp.timezone = "America/New_York"
        fp.webgl_vendor = "Google Inc. (Intel)"
        fp.webgl_renderer = "ANGLE (Intel, Intel(R) UHD Graphics 630 Direct3D11 vs_5_0 ps_5_0)"
        return fp

    @staticmethod
    def macos_chrome() -> Fingerprint:
        """macOS + Chrome fingerprint."""
        fp = Fingerprint()
        fp.screen_resolution = "1920x1080"
        fp.screen_color_depth = 24
        fp.user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        fp.platform = "MacIntel"
        fp.language = "en-US"
        fp.languages = ["en-US", "en"]
        fp.hardware_concurrency = 8
        fp.device_memory = 16
        fp.timezone = "America/Los_Angeles"
        fp.webgl_vendor = "Intel Inc."
        fp.webgl_renderer = "Intel Iris OpenGL Engine"
        return fp

    @staticmethod
    def linux_chrome() -> Fingerprint:
        """Linux + Chrome fingerprint."""
        fp = Fingerprint()
        fp.screen_resolution = "1920x1080"
        fp.screen_color_depth = 24
        fp.user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        fp.platform = "Linux x86_64"
        fp.language = "en-US"
        fp.languages = ["en-US", "en"]
        fp.hardware_concurrency = 12
        fp.device_memory = 16
        fp.timezone = "America/New_York"
        fp.webgl_vendor = "NVIDIA Corporation"
        fp.webgl_renderer = "NVIDIA GeForce GTX 1060/PCIe/SSE2"
        return fp
