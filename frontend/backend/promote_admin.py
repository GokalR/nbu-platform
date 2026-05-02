"""Promote a user to admin role.

Usage:
  cd frontend/backend
  python promote_admin.py your@email.com

Or to demote:
  python promote_admin.py your@email.com --role student
"""
from __future__ import annotations
import argparse
import asyncio
import sys

from sqlalchemy import select

from models import User, async_session


async def promote(email: str, role: str) -> None:
    async with async_session() as session:
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if not user:
            print(f'  ✗ no user with email={email}')
            print(f'  → register one at /login first, then run this again')
            sys.exit(1)
        prev = user.role
        user.role = role
        await session.commit()
        print(f'  ✓ {email}:  role {prev!r} → {role!r}')


def main() -> None:
    parser = argparse.ArgumentParser(description='Promote/demote a user role.')
    parser.add_argument('email', help='Email of the user to update')
    parser.add_argument('--role', default='admin', help="New role (default: 'admin')")
    args = parser.parse_args()
    asyncio.run(promote(args.email, args.role))


if __name__ == '__main__':
    main()
