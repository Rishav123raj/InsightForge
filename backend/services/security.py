from fastapi import Header, HTTPException, status
from .config import get_settings

ROLE_SCOPES = {
    "leadership": {"analytics:read", "docs:read", "pii:masked"},
    "analyst": {"analytics:read", "docs:read", "pii:masked"},
    "marketing": {"analytics:read", "docs:read", "pii:masked", "marketing:read"},
}


def require_user(
    x_api_key: str = Header(default=""),
    x_user_role: str = Header(default="analyst"),
    x_user_id: str = Header(default="demo-user"),
) -> dict:
    settings = get_settings()
    if x_api_key != settings.api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
    if x_user_role not in ROLE_SCOPES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unknown role")
    return {"user_id": x_user_id, "role": x_user_role, "scopes": ROLE_SCOPES[x_user_role]}


def mask_email(email: str) -> str:
    if not email or "@" not in email:
        return "***"
    name, domain = email.split("@", 1)
    return f"{name[:1]}***@{domain}"


if __name__ == "__main__":
    print("Testing authentication layer...\n")

    try:
        user = require_user(
            x_api_key="my-secret-key-123",
            x_user_role="analyst",
            x_user_id="rishav"
        )

        print("AUTH SUCCESS")
        print(user)

    except Exception as e:
        print("AUTH FAILED")
        print(type(e).__name__)
        print(str(e))

    print("\n" + "=" * 80)

    print("Testing email masking...\n")

    print(mask_email("john.doe@gmail.com"))
    print(mask_email("alice@yahoo.com"))