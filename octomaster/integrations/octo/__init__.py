"""
Octo Browser integration module.
"""

from octomaster.integrations.octo.client import OctoClient
from octomaster.integrations.octo.models import Profile, Proxy, Tag

__all__ = ["OctoClient", "Profile", "Proxy", "Tag"]
