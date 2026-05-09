import logging

from fastapi import Header, HTTPException, status

from .config import get_settings


# -----------------------------------------------------------------------------
# Logging Configuration
# -----------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,

    format="%(asctime)s | %(levelname)s | %(message)s",

    handlers=[
        logging.FileHandler("insightforge.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("insightforge.security")


# -----------------------------------------------------------------------------
# Role-Based Access Scopes
# -----------------------------------------------------------------------------

ROLE_SCOPES = {
    "leadership": {
        "analytics:read",
        "docs:read",
        "pii:masked"
    },

    "analyst": {
        "analytics:read",
        "docs:read",
        "pii:masked"
    },

    "marketing": {
        "analytics:read",
        "docs:read",
        "pii:masked",
        "marketing:read"
    },
}


# -----------------------------------------------------------------------------
# Authentication / Authorization
# -----------------------------------------------------------------------------

def require_user(
    x_api_key: str = Header(default=""),
    x_user_role: str = Header(default="analyst"),
    x_user_id: str = Header(default="demo-user"),
) -> dict:

    logger.info(
        f"Authenticating user={x_user_id} "
        f"role={x_user_role}"
    )

    settings = get_settings()

    # -------------------------------------------------------------------------
    # API Key Validation
    # -------------------------------------------------------------------------

    if x_api_key != settings.api_key:

        logger.warning(
            f"Authentication failed for user={x_user_id} "
            f"(invalid API key)"
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )

    # -------------------------------------------------------------------------
    # Role Validation
    # -------------------------------------------------------------------------

    if x_user_role not in ROLE_SCOPES:

        logger.warning(
            f"Authorization failed for user={x_user_id} "
            f"(unknown role={x_user_role})"
        )

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unknown role"
        )

    logger.info(
        f"Authentication successful for user={x_user_id}"
    )

    logger.info(
        f"Assigned scopes: {ROLE_SCOPES[x_user_role]}"
    )

    return {
        "user_id": x_user_id,
        "role": x_user_role,
        "scopes": ROLE_SCOPES[x_user_role]
    }


# -----------------------------------------------------------------------------
# Email Masking Utility
# -----------------------------------------------------------------------------

def mask_email(email: str) -> str:

    logger.info("Masking email address")

    if not email or "@" not in email:

        logger.warning(
            "Invalid email format encountered during masking"
        )

        return "***"

    name, domain = email.split("@", 1)

    masked = f"{name[:1]}***@{domain}"

    logger.info("Email masked successfully")

    return masked


# -----------------------------------------------------------------------------
# Standalone Testing
# -----------------------------------------------------------------------------

if __name__ == "__main__":

    print("Testing authentication layer...\n")

    logger.info("Running standalone security module test")

    try:

        user = require_user(
            x_api_key="my-secret-key-123",
            x_user_role="analyst",
            x_user_id="rishav"
        )

        print("AUTH SUCCESS")
        print(user)

        logger.info("Standalone auth test passed")

    except Exception as e:

        logger.exception(
            f"Standalone auth test failed: {str(e)}"
        )

        print("AUTH FAILED")
        print(type(e).__name__)
        print(str(e))

    print("\n" + "=" * 80)

    print("Testing email masking...\n")

    print(mask_email("john.doe@gmail.com"))
    print(mask_email("alice@yahoo.com"))

    logger.info("Email masking tests completed")