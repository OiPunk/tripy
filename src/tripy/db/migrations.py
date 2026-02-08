from __future__ import annotations

from alembic import command
from alembic.config import Config


ALEMBIC_INI_PATH = "alembic.ini"


def upgrade_head() -> None:
    config = Config(ALEMBIC_INI_PATH)
    command.upgrade(config, "head")


def downgrade_one() -> None:
    config = Config(ALEMBIC_INI_PATH)
    command.downgrade(config, "-1")
