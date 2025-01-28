import logging

logger = logging.getLogger(__name__)


def process(userinfo: dict, expected_claims: list[str]) -> tuple[list[str], dict[str, str]]:
    """Process expected claims from the userinfo dict.

    - Boolean claims comes back in userinfo like `{ "claim": "1" | "0" }` or `{ "claim": "true" }`
    - Other claims come back in userinfo like `{ "claim": "value" }`

    Returns a tuple `(claims: list[str], errors: dict[str, int])`
    """
    claims = []
    errors = {}

    for claim in expected_claims:
        claim_value = userinfo.get(claim)
        if not claim_value:
            logger.warning(f"userinfo did not contain: {claim}")
        try:
            claim_value = int(claim_value)
        except (TypeError, ValueError):
            pass
        if isinstance(claim_value, int):
            if claim_value == 1:
                # if userinfo contains our claim and the flag is 1 (true), store the *claim*
                claims.append(claim)
            elif claim_value >= 10:
                errors[claim] = claim_value
        elif isinstance(claim_value, str):
            if claim_value.lower() == "true":
                claims.append(claim)
            elif claim_value.lower() != "false":
                claims.append(f"{claim}:{claim_value}")

    return (claims, errors)
