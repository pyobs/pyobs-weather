"""pyobs-auth USER_RESOLVER for pyobs-weather.

Weather has no pre-existing user base (no login of any kind existed before this), so unlike
pyobs-archive's resolver there's no legacy account to preserve - but the same email/username
matching is kept anyway so a manually created local User (e.g. an early Django-admin account)
still links up on its first Keycloak login instead of getting a second, disconnected User.
Keycloak's `sub` claim is the join key (see pyobs-core's shared-auth design doc), stored on
KeycloakIdentity. Newly-minted accounts are active by default: authorization is the
PYOBS_AUTH['REQUIRED_GROUPS'] claims gate (Keycloak group membership), not local activation -
see pyobs-core's specs/design/shared-authz-keycloak.md. is_staff/is_superuser are untouched by
this resolver either way - weather doesn't sync a privilege role from Keycloak, so those stay
local-only (createsuperuser / Django admin).
"""

from __future__ import annotations

from typing import Any

from django.contrib.auth.models import User

from pyobs_weather.authentication.models import KeycloakIdentity


def resolve_user(claims: dict[str, Any]) -> User | None:
    sub = claims["sub"]

    try:
        return KeycloakIdentity.objects.get(keycloak_sub=sub).user
    except KeycloakIdentity.DoesNotExist:
        pass

    email = claims.get("email")
    username = claims.get("preferred_username") or sub

    user = User.objects.filter(email=email).first() if email else None
    if user is None:
        # Falls back to username since email matching alone misses accounts that predate
        # having an email address set - without this, User.objects.create() below hits a
        # UNIQUE constraint on username instead of linking the existing account.
        user = User.objects.filter(username=username).first()
    if user is None:
        user = User.objects.create(username=username, email=email or "", is_active=True)

    KeycloakIdentity.objects.update_or_create(user=user, defaults={"keycloak_sub": sub})
    return user
