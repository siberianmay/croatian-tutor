#!/usr/bin/env python
"""
Seed script for Italian grammar topics.

This script loads Italian grammar topics from JSON files (A1-C1) and inserts
them into the database. It handles the prerequisite_ids mapping by:
1. First inserting all topics without prerequisites
2. Then updating prerequisites using a display_order -> database_id mapping

Usage:
    cd backend
    python -m scripts.seed_italian_topics [options]

Options:
    --force     Delete existing Italian topics and re-seed (non-interactive)
    --skip      Skip if Italian topics exist (non-interactive)
    --help      Show this help message
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session_maker
from app.models.grammar_topic import GrammarTopic
from app.models.language import Language
from app.models.enums import CEFRLevel


# JSON files to load, in order
JSON_FILES = [
    "italian_grammar_topics_a1.json",
    "italian_grammar_topics_a2.json",
    "italian_grammar_topics_b1.json",
    "italian_grammar_topics_b2.json",
    "italian_grammar_topics_c1.json",
]

ITALIAN_LANGUAGE_CODE = "it"
DEV_DIR = backend_dir / "content"


async def ensure_italian_language(db: AsyncSession) -> None:
    """Ensure Italian language exists in the database."""
    result = await db.execute(
        select(Language).where(Language.code == ITALIAN_LANGUAGE_CODE)
    )
    language = result.scalar_one_or_none()

    if not language:
        print(f"Creating Italian language entry...")
        language = Language(
            code=ITALIAN_LANGUAGE_CODE,
            name="Italian",
            native_name="Italiano",
            is_active=True,
        )
        db.add(language)
        await db.flush()
        print(f"✓ Created Italian language (code: {ITALIAN_LANGUAGE_CODE})")
    else:
        print(f"✓ Italian language already exists (code: {ITALIAN_LANGUAGE_CODE})")


async def get_existing_italian_topics(db: AsyncSession) -> dict[int, int]:
    """
    Get existing Italian topics and return mapping of display_order -> id.
    """
    result = await db.execute(
        select(GrammarTopic.display_order, GrammarTopic.id)
        .where(GrammarTopic.language == ITALIAN_LANGUAGE_CODE)
    )
    return {row[0]: row[1] for row in result.all()}


async def count_italian_topics(db: AsyncSession) -> int:
    """Count existing Italian topics."""
    result = await db.execute(
        select(func.count(GrammarTopic.id))
        .where(GrammarTopic.language == ITALIAN_LANGUAGE_CODE)
    )
    return result.scalar_one()


def load_topics_from_json(filename: str) -> list[dict]:
    """Load topics from a JSON file."""
    filepath = DEV_DIR / filename
    if not filepath.exists():
        print(f"✗ File not found: {filepath}")
        return []

    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def parse_cefr_level(level_str: str) -> CEFRLevel:
    """Parse CEFR level string to enum."""
    level_map = {
        "A1": CEFRLevel.A1,
        "A2": CEFRLevel.A2,
        "B1": CEFRLevel.B1,
        "B2": CEFRLevel.B2,
        "C1": CEFRLevel.C1,
        "C2": CEFRLevel.C2,
    }
    return level_map[level_str]


async def seed_topics(db: AsyncSession, *, force: bool = False, skip_existing: bool = False) -> None:
    """
    Seed Italian grammar topics into the database.

    Args:
        db: Async database session
        force: Delete existing Italian topics and re-seed
        skip_existing: Skip seeding if Italian topics exist
    """
    # Check existing topics
    existing_count = await count_italian_topics(db)
    if existing_count > 0:
        print(f"\n⚠ Found {existing_count} existing Italian topics.")

        if skip_existing:
            print("Skipping seed operation (--skip flag).")
            return

        if force:
            await db.execute(
                GrammarTopic.__table__.delete().where(
                    GrammarTopic.language == ITALIAN_LANGUAGE_CODE
                )
            )
            await db.flush()
            print(f"✓ Deleted {existing_count} existing Italian topics (--force flag).")
        else:
            # Interactive mode
            response = input("Do you want to skip seeding? (y/n): ").strip().lower()
            if response == "y":
                print("Skipping seed operation.")
                return

            response = input("Do you want to DELETE existing Italian topics and re-seed? (y/n): ").strip().lower()
            if response == "y":
                await db.execute(
                    GrammarTopic.__table__.delete().where(
                        GrammarTopic.language == ITALIAN_LANGUAGE_CODE
                    )
                )
                await db.flush()
                print(f"✓ Deleted {existing_count} existing Italian topics.")
            else:
                print("Aborting seed operation.")
                return

    # Load all topics from JSON files
    all_topics = []
    for filename in JSON_FILES:
        topics = load_topics_from_json(filename)
        if topics:
            print(f"✓ Loaded {len(topics)} topics from {filename}")
            all_topics.extend(topics)
        else:
            print(f"✗ No topics loaded from {filename}")

    if not all_topics:
        print("No topics to seed.")
        return

    print(f"\nTotal topics to seed: {len(all_topics)}")

    # Sort by display_order to ensure correct insertion order
    all_topics.sort(key=lambda t: t["display_order"])

    # Phase 1: Insert all topics WITHOUT prerequisite_ids
    # Build mapping of display_order -> database_id
    display_order_to_id: dict[int, int] = {}

    print("\nPhase 1: Inserting topics...")
    for topic_data in all_topics:
        topic = GrammarTopic(
            language=ITALIAN_LANGUAGE_CODE,
            name=topic_data["name"],
            cefr_level=parse_cefr_level(topic_data["cefr_level"]),
            prerequisite_ids=None,  # Will set in phase 2
            rule_description=topic_data.get("rule_description"),
            display_order=topic_data["display_order"],
        )
        db.add(topic)
        await db.flush()
        await db.refresh(topic)

        display_order_to_id[topic_data["display_order"]] = topic.id
        print(f"  ✓ [{topic.id}] {topic.name} (display_order: {topic.display_order})")

    print(f"\n✓ Inserted {len(all_topics)} topics.")

    # Phase 2: Update prerequisite_ids with correct database IDs
    print("\nPhase 2: Updating prerequisite_ids...")
    updates_made = 0

    for topic_data in all_topics:
        json_prerequisites = topic_data.get("prerequisite_ids")
        if not json_prerequisites:
            continue

        # Map display_order values to database IDs
        db_prerequisites = []
        for prereq_display_order in json_prerequisites:
            if prereq_display_order in display_order_to_id:
                db_prerequisites.append(display_order_to_id[prereq_display_order])
            else:
                print(f"  ⚠ Warning: Prerequisite {prereq_display_order} not found for topic {topic_data['name']}")

        if db_prerequisites:
            topic_id = display_order_to_id[topic_data["display_order"]]
            result = await db.execute(
                select(GrammarTopic).where(GrammarTopic.id == topic_id)
            )
            topic = result.scalar_one()
            topic.prerequisite_ids = db_prerequisites
            await db.flush()
            updates_made += 1
            print(f"  ✓ [{topic_id}] {topic_data['name']}: prerequisites = {db_prerequisites}")

    print(f"\n✓ Updated prerequisites for {updates_made} topics.")


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Seed Italian grammar topics into the database.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Delete existing Italian topics and re-seed (non-interactive)",
    )
    parser.add_argument(
        "--skip",
        action="store_true",
        help="Skip if Italian topics exist (non-interactive)",
    )
    return parser.parse_args()


async def main() -> None:
    """Main entry point."""
    args = parse_args()

    if args.force and args.skip:
        print("Error: Cannot use --force and --skip together.")
        sys.exit(1)

    print("=" * 60)
    print("Italian Grammar Topics Seeder")
    print("=" * 60)

    async with async_session_maker() as db:
        try:
            # Ensure Italian language exists
            await ensure_italian_language(db)

            # Seed topics
            await seed_topics(db, force=args.force, skip_existing=args.skip)

            # Commit all changes
            await db.commit()
            print("\n" + "=" * 60)
            print("✓ Seed completed successfully!")
            print("=" * 60)

        except Exception as e:
            await db.rollback()
            print(f"\n✗ Error: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(main())
