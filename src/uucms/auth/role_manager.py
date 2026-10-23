"""Central registry for role credentials used by authentication fixtures."""

from collections.abc import Mapping
from dataclasses import dataclass
import os


@dataclass(frozen=True)
class RoleCredentials:
    username: str
    password: str


@dataclass(frozen=True)
class _RoleConfig:
    username: str
    password: str | None
    password_env: str | None


class RoleManager:
    """Resolves a role key to credentials from the shared login-data registry."""

    def __init__(self, login_data: Mapping[str, object]) -> None:
        self._default_role = self._role_config_from(
            login_data, role_name="default"
        )
        roles = login_data.get("roles", {})
        if not isinstance(roles, Mapping):
            raise ValueError(
                "The 'roles' field in the login registry must be an object"
            )
        self._roles = {
            str(role_name): self._role_config_from(
                credentials, role_name=str(role_name)
            )
            for role_name, credentials in roles.items()
        }

    def available_roles(self) -> tuple[str, ...]:
        """Return configured registry keys without exposing credentials."""
        return ("default", *sorted(self._roles))

    def credentials_for(self, role_name: str = "default") -> RoleCredentials:
        """Return credentials for a configured role or raise a clear error."""
        key = role_name.strip()
        if key.casefold() in {"", "default"}:
            return self._resolve_credentials(self._default_role, role_name="default")
        try:
            role = self._roles[key]
        except KeyError as exc:
            available = ", ".join(self.available_roles())
            raise ValueError(
                f"Unknown login role {role_name!r}; configured role keys: {available}"
            ) from exc
        return self._resolve_credentials(role, role_name=key)

    @staticmethod
    def _resolve_credentials(
        role: _RoleConfig, *, role_name: str
    ) -> RoleCredentials:
        password = role.password
        if role.password_env:
            password = os.environ.get(role.password_env)
            if not password:
                raise ValueError(
                    f"Environment variable {role.password_env!r} is required "
                    f"for login role {role_name!r}"
                )
        return RoleCredentials(username=role.username, password=password or "")

    @staticmethod
    def _role_config_from(value: object, *, role_name: str) -> _RoleConfig:
        if not isinstance(value, Mapping):
            raise ValueError(
                f"Credentials for role {role_name!r} in "
                "the login registry must be an object"
            )
        username = str(value.get("username", "")).strip()
        raw_password = value.get("password")
        password = str(raw_password) if raw_password is not None else None
        raw_password_env = value.get("password_env")
        password_env = (
            str(raw_password_env).strip() if raw_password_env is not None else None
        )
        if not username or not (password or password_env):
            raise ValueError(
                f"Credentials for role {role_name!r} in "
                "the login registry "
                "must include username and either password or password_env"
            )
        return _RoleConfig(
            username=username, password=password, password_env=password_env
        )
