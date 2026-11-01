"""
Provisions doctor accounts from an externally-maintained data file instead
of public self-registration — this is the "doctor database is external,
built from data we enter ourselves" requirement.

Usage:
    python seed_doctors.py [path/to/doctors.json]

Defaults to data/doctors_seed.json. The file is a JSON list of objects with
at least "email", "username" and "password" (see that file for the shape;
"full_name"/"specialty" are accepted but not stored yet — they're there so
the external data source can carry more than the current schema uses).

Mirrors the existing seed_patients.py in spirit (a small standalone script
the team runs against the dev/staging database), but goes through
PasswordHandler so the accounts can actually log in, and marks every row as
role="doctor" so it never collides with patient self-registration.
"""

import asyncio
import json
import sys
import uuid
from pathlib import Path

from core.database import get_session
from core.database.session import set_session_context
from core.security import PasswordHandler
from app.models.user import User, UserRole
from app.repositories.user import UserRepository

DEFAULT_SOURCE = Path(__file__).parent / "data" / "doctors_seed.json"


async def seed(source: Path) -> None:
    doctors = json.loads(source.read_text(encoding="utf-8"))

    # get_session() uses a scoped session keyed by this context var, which
    # SQLAlchemyMiddleware normally sets per-request. Standalone scripts
    # (this one, and seed_patients.py) need to set it themselves.
    set_session_context(str(uuid.uuid4()))

    async for session in get_session():
        repo = UserRepository(User, db_session=session)
        created, skipped = 0, 0

        for entry in doctors:
            email = entry["email"]
            existing = await repo.get_by_email(email)
            if existing:
                print(f"Skip (ya existe): {email}")
                skipped += 1
                continue

            session.add(
                User(
                    email=email,
                    username=entry["username"],
                    password=PasswordHandler.hash(entry["password"]),
                    role=UserRole.DOCTOR.value,
                )
            )
            created += 1

        try:
            await session.commit()
            print(f"Doctores creados: {created} · omitidos: {skipped}")
        except Exception as e:
            await session.rollback()
            print(f"Error creando doctores: {e}")
        break


if __name__ == "__main__":
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_SOURCE
    asyncio.run(seed(path))
