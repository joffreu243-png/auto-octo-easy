"""
Octo Browser integration module for OctoMaster Pro.

Provides comprehensive integration with Octo Browser API including:
- Enhanced API wrapper with rate limiting and caching
- Profile management and bulk operations
- Proxy and tag management
- Fingerprint generation
- Import/export functionality
"""

from src.octo.api import OctoAPI, RateLimiter, ResponseCache
from src.octo.models import (
    # Enums
    ProfileStatus,
    ProxyType,
    BrowserType,
    # Data models
    Profile,
    Proxy,
    Tag,
    Fingerprint,
    # Request models
    ProfileCreateRequest,
    ProfileUpdateRequest,
    # Result models
    BulkOperationResult,
)
from src.octo.profile_manager import ProfileManager
from src.octo.proxy_manager import ProxyManager
from src.octo.tag_manager import TagManager
from src.octo.mass_operations import MassOperations
from src.octo.fingerprint import FingerprintGenerator, FingerprintPresets
from src.octo.import_export import ProfileImportExport

__all__ = [
    # API
    "OctoAPI",
    "RateLimiter",
    "ResponseCache",
    # Enums
    "ProfileStatus",
    "ProxyType",
    "BrowserType",
    # Models
    "Profile",
    "Proxy",
    "Tag",
    "Fingerprint",
    "ProfileCreateRequest",
    "ProfileUpdateRequest",
    "BulkOperationResult",
    # Managers
    "ProfileManager",
    "ProxyManager",
    "TagManager",
    "MassOperations",
    # Fingerprint
    "FingerprintGenerator",
    "FingerprintPresets",
    # Import/Export
    "ProfileImportExport",
]
