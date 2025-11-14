"""
Proxy management module for Octo Browser.

Provides proxy operations and assignment strategies.
"""

from typing import List, Optional, Dict, Any
from pathlib import Path
import csv
from loguru import logger

from src.octo.models import Proxy, ProxyType, BulkOperationResult


class ProxyManager:
    """Proxy management and operations."""

    def __init__(self):
        """Initialize proxy manager."""
        self.proxies: List[Proxy] = []
        logger.info("ProxyManager initialized")

    def load_from_file(self, file_path: Path) -> int:
        """Load proxies from file.

        Supports formats:
        - host:port
        - host:port:login:password
        - type://host:port
        - type://login:password@host:port

        Args:
            file_path: Path to proxy file

        Returns:
            Number of proxies loaded
        """
        self.proxies.clear()

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()

                    if not line or line.startswith("#"):
                        continue

                    proxy = self._parse_proxy_string(line)
                    if proxy:
                        self.proxies.append(proxy)

            logger.info(f"Loaded {len(self.proxies)} proxies from {file_path}")
            return len(self.proxies)

        except Exception as e:
            logger.error(f"Failed to load proxies from {file_path}: {e}")
            return 0

    def load_from_csv(self, file_path: Path) -> int:
        """Load proxies from CSV file.

        Expected columns: type, host, port, login, password

        Args:
            file_path: Path to CSV file

        Returns:
            Number of proxies loaded
        """
        self.proxies.clear()

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)

                for row in reader:
                    try:
                        proxy = Proxy(
                            type=ProxyType(row.get("type", "http")),
                            host=row["host"],
                            port=int(row["port"]),
                            login=row.get("login") or None,
                            password=row.get("password") or None,
                            change_ip_url=row.get("change_ip_url") or None,
                        )
                        self.proxies.append(proxy)
                    except Exception as e:
                        logger.warning(f"Failed to parse proxy row: {row} - {e}")
                        continue

            logger.info(f"Loaded {len(self.proxies)} proxies from {file_path}")
            return len(self.proxies)

        except Exception as e:
            logger.error(f"Failed to load proxies from CSV {file_path}: {e}")
            return 0

    def save_to_csv(self, file_path: Path) -> bool:
        """Save proxies to CSV file.

        Args:
            file_path: Path to save CSV

        Returns:
            True if successful
        """
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, "w", encoding="utf-8", newline="") as f:
                fieldnames = ["type", "host", "port", "login", "password", "change_ip_url"]
                writer = csv.DictWriter(f, fieldnames=fieldnames)

                writer.writeheader()

                for proxy in self.proxies:
                    writer.writerow(proxy.to_dict())

            logger.info(f"Saved {len(self.proxies)} proxies to {file_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to save proxies to {file_path}: {e}")
            return False

    def _parse_proxy_string(self, proxy_str: str) -> Optional[Proxy]:
        """Parse proxy from string.

        Args:
            proxy_str: Proxy string

        Returns:
            Proxy instance or None
        """
        try:
            # Format: type://login:password@host:port
            if "://" in proxy_str:
                parts = proxy_str.split("://", 1)
                proxy_type = ProxyType(parts[0])
                rest = parts[1]

                # Check for auth
                if "@" in rest:
                    auth, host_port = rest.rsplit("@", 1)
                    login, password = auth.split(":", 1)
                else:
                    host_port = rest
                    login = None
                    password = None

                # Parse host:port
                host, port = host_port.rsplit(":", 1)

                return Proxy(
                    type=proxy_type,
                    host=host,
                    port=int(port),
                    login=login,
                    password=password,
                )

            # Format: host:port:login:password
            elif proxy_str.count(":") >= 3:
                parts = proxy_str.split(":")
                return Proxy(
                    type=ProxyType.HTTP,
                    host=parts[0],
                    port=int(parts[1]),
                    login=parts[2],
                    password=parts[3],
                )

            # Format: host:port
            elif proxy_str.count(":") == 1:
                host, port = proxy_str.split(":")
                return Proxy(
                    type=ProxyType.HTTP,
                    host=host,
                    port=int(port),
                )

            else:
                logger.warning(f"Invalid proxy format: {proxy_str}")
                return None

        except Exception as e:
            logger.warning(f"Failed to parse proxy '{proxy_str}': {e}")
            return None

    def add_proxy(self, proxy: Proxy) -> None:
        """Add proxy to list.

        Args:
            proxy: Proxy to add
        """
        self.proxies.append(proxy)

    def remove_proxy(self, index: int) -> bool:
        """Remove proxy by index.

        Args:
            index: Proxy index

        Returns:
            True if successful
        """
        try:
            if 0 <= index < len(self.proxies):
                del self.proxies[index]
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to remove proxy at index {index}: {e}")
            return False

    def get_proxy(self, index: int) -> Optional[Proxy]:
        """Get proxy by index.

        Args:
            index: Proxy index

        Returns:
            Proxy or None
        """
        if 0 <= index < len(self.proxies):
            return self.proxies[index]
        return None

    def get_all_proxies(self) -> List[Proxy]:
        """Get all proxies.

        Returns:
            List of proxies
        """
        return self.proxies.copy()

    def count(self) -> int:
        """Get proxy count.

        Returns:
            Number of proxies
        """
        return len(self.proxies)

    def filter_by_type(self, proxy_type: ProxyType) -> List[Proxy]:
        """Filter proxies by type.

        Args:
            proxy_type: Proxy type

        Returns:
            Filtered proxies
        """
        return [p for p in self.proxies if p.type == proxy_type]

    def get_proxies_with_auth(self) -> List[Proxy]:
        """Get proxies that require authentication.

        Returns:
            Proxies with login/password
        """
        return [p for p in self.proxies if p.login and p.password]

    def get_proxies_without_auth(self) -> List[Proxy]:
        """Get proxies that don't require authentication.

        Returns:
            Proxies without login/password
        """
        return [p for p in self.proxies if not p.login or not p.password]

    def validate_proxy(self, proxy: Proxy) -> Dict[str, Any]:
        """Validate proxy configuration.

        Args:
            proxy: Proxy to validate

        Returns:
            Validation result
        """
        errors = []
        warnings = []

        # Check required fields
        if not proxy.host:
            errors.append("Host is required")

        if not proxy.port or proxy.port <= 0 or proxy.port > 65535:
            errors.append("Port must be between 1 and 65535")

        # Check auth consistency
        if (proxy.login and not proxy.password) or (not proxy.login and proxy.password):
            warnings.append("Both login and password should be provided for auth")

        # Check type
        if proxy.type not in ProxyType:
            errors.append(f"Invalid proxy type: {proxy.type}")

        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
        }

    def get_round_robin_proxy(self, index: int) -> Optional[Proxy]:
        """Get proxy using round-robin strategy.

        Args:
            index: Index (will be wrapped to proxy count)

        Returns:
            Proxy or None
        """
        if not self.proxies:
            return None

        return self.proxies[index % len(self.proxies)]

    def assign_round_robin(
        self, count: int, start_index: int = 0
    ) -> List[Proxy]:
        """Get proxies for round-robin assignment.

        Args:
            count: Number of proxies needed
            start_index: Starting index

        Returns:
            List of proxies (cycling through available proxies)
        """
        if not self.proxies:
            return []

        result: List[Proxy] = []

        for i in range(count):
            proxy = self.get_round_robin_proxy(start_index + i)
            if proxy:
                result.append(proxy)

        return result

    def shuffle_proxies(self) -> None:
        """Shuffle proxy list for random distribution."""
        import random
        random.shuffle(self.proxies)
        logger.info("Proxies shuffled")

    def deduplicate(self) -> int:
        """Remove duplicate proxies.

        Returns:
            Number of duplicates removed
        """
        original_count = len(self.proxies)

        # Create set of unique proxy strings
        seen = set()
        unique_proxies = []

        for proxy in self.proxies:
            proxy_key = f"{proxy.type.value}://{proxy.host}:{proxy.port}"
            if proxy.login:
                proxy_key += f":{proxy.login}"

            if proxy_key not in seen:
                seen.add(proxy_key)
                unique_proxies.append(proxy)

        self.proxies = unique_proxies
        removed = original_count - len(self.proxies)

        if removed > 0:
            logger.info(f"Removed {removed} duplicate proxies")

        return removed

    def get_statistics(self) -> Dict[str, Any]:
        """Get proxy statistics.

        Returns:
            Statistics dictionary
        """
        if not self.proxies:
            return {
                "total": 0,
                "by_type": {},
                "with_auth": 0,
                "without_auth": 0,
            }

        # Count by type
        type_counts: Dict[str, int] = {}
        for proxy_type in ProxyType:
            count = sum(1 for p in self.proxies if p.type == proxy_type)
            if count > 0:
                type_counts[proxy_type.name] = count

        # Count auth
        with_auth = sum(1 for p in self.proxies if p.login and p.password)
        without_auth = len(self.proxies) - with_auth

        return {
            "total": len(self.proxies),
            "by_type": type_counts,
            "with_auth": with_auth,
            "without_auth": without_auth,
        }

    def clear(self) -> None:
        """Clear all proxies."""
        self.proxies.clear()
        logger.info("Proxies cleared")
