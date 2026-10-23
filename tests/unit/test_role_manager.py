"""Unit tests for centralized role credential lookup."""

import pytest

from uucms.auth.role_manager import RoleCredentials, RoleManager


@pytest.fixture
def registry() -> dict:
    return {
        "username": "default-user",
        "password": "default-password",
        "roles": {
            "student": {"username": "student-user", "password": "student-password"},
            "registrar_evaluation": {
                "username": "registrar-user",
                "password": "registrar-password",
            },
        },
    }


def test_role_manager_resolves_default_credentials(registry: dict) -> None:
    manager = RoleManager(registry)

    assert manager.credentials_for() == RoleCredentials(
        username="default-user", password="default-password"
    )
    assert manager.credentials_for("default") == manager.credentials_for()


def test_role_manager_resolves_configured_role(registry: dict) -> None:
    manager = RoleManager(registry)

    assert manager.credentials_for("registrar_evaluation") == RoleCredentials(
        username="registrar-user", password="registrar-password"
    )
    assert manager.available_roles() == (
        "default",
        "registrar_evaluation",
        "student",
    )


def test_role_manager_resolves_password_from_environment(
    registry: dict, monkeypatch: pytest.MonkeyPatch
) -> None:
    registry["roles"]["state_admin"] = {
        "username": "state-admin-user",
        "password_env": "UUCMS_PASSWORD_STATE_ADMIN",
    }
    monkeypatch.setenv("UUCMS_PASSWORD_STATE_ADMIN", "state-admin-password")

    manager = RoleManager(registry)

    assert manager.credentials_for("state_admin") == RoleCredentials(
        username="state-admin-user", password="state-admin-password"
    )


def test_role_manager_resolves_default_password_from_environment(
    registry: dict, monkeypatch: pytest.MonkeyPatch
) -> None:
    registry.pop("password")
    registry["password_env"] = "UUCMS_PASSWORD_DEFAULT"
    monkeypatch.setenv("UUCMS_PASSWORD_DEFAULT", "default-env-password")

    manager = RoleManager(registry)

    assert manager.credentials_for() == RoleCredentials(
        username="default-user", password="default-env-password"
    )


def test_role_manager_requires_configured_password_environment_variable(
    registry: dict, monkeypatch: pytest.MonkeyPatch
) -> None:
    registry["roles"]["state_admin"] = {
        "username": "state-admin-user",
        "password_env": "UUCMS_PASSWORD_STATE_ADMIN",
    }
    monkeypatch.delenv("UUCMS_PASSWORD_STATE_ADMIN", raising=False)

    manager = RoleManager(registry)

    with pytest.raises(
        ValueError,
        match="Environment variable 'UUCMS_PASSWORD_STATE_ADMIN' is required",
    ):
        manager.credentials_for("state_admin")


def test_role_manager_requires_default_password_environment_variable(
    registry: dict, monkeypatch: pytest.MonkeyPatch
) -> None:
    registry.pop("password")
    registry["password_env"] = "UUCMS_PASSWORD_DEFAULT"
    monkeypatch.delenv("UUCMS_PASSWORD_DEFAULT", raising=False)

    manager = RoleManager(registry)

    with pytest.raises(
        ValueError,
        match="Environment variable 'UUCMS_PASSWORD_DEFAULT' is required",
    ):
        manager.credentials_for()


def test_role_manager_rejects_unconfigured_role(registry: dict) -> None:
    manager = RoleManager(registry)

    with pytest.raises(ValueError, match="Unknown login role 'principal'"):
        manager.credentials_for("principal")


@pytest.mark.parametrize(
    "registry",
    [
        {"username": "", "password": "secret"},
        {"username": "user", "password": ""},
        {
            "username": "user",
            "password": "secret",
            "roles": {"student": {"username": "student", "password": ""}},
        },
        {
            "username": "user",
            "password": "secret",
            "roles": {
                "student": {
                    "username": "student",
                    "password": "",
                    "password_env": "",
                }
            },
        },
        {"username": "user", "password": "secret", "roles": []},
    ],
)
def test_role_manager_rejects_incomplete_or_invalid_registry(registry: dict) -> None:
    with pytest.raises(ValueError):
        RoleManager(registry)
