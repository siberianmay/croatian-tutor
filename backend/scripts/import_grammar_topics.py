"""Import grammar topics from JSON file into the database."""

import asyncio
import json
import sys
from pathlib import Path

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, delete

from app.database import async_session_maker
from app.models.grammar_topic import GrammarTopic
from app.models.enums import CEFRLevel


async def import_topics(json_path: Path, *, clear_existing: bool = False) -> None:
    """
    Import grammar topics from JSON file.

    Args:
        json_path: Path to the JSON file
        clear_existing: If True, delete all existing topics first
    """
    with open(json_path, "r", encoding="utf-8") as f:
        topics_data = json.load(f)

    print(f"Loaded {len(topics_data)} topics from {json_path}")

    async with async_session_maker() as session:
        if clear_existing:
            # Delete all existing topics
            await session.execute(delete(GrammarTopic))
            print("Cleared existing grammar topics")

        # First pass: insert all topics without prerequisite_ids
        # Map display_order -> database id
        display_order_to_id: dict[int, int] = {}

        for topic_data in sorted(topics_data, key=lambda x: x["display_order"]):
            # Check if topic already exists by name
            result = await session.execute(
                select(GrammarTopic).where(GrammarTopic.name == topic_data["name"])
            )
            existing = result.scalar_one_or_none()

            if existing:
                print(f"  Skipping existing topic: {topic_data['name']}")
                display_order_to_id[topic_data["display_order"]] = existing.id
                continue

            topic = GrammarTopic(
                name=topic_data["name"],
                cefr_level=CEFRLevel(topic_data["cefr_level"]),
                prerequisite_ids=None,  # Set later
                rule_description=topic_data.get("rule_description"),
                display_order=topic_data["display_order"],
            )
            session.add(topic)
            await session.flush()

            display_order_to_id[topic_data["display_order"]] = topic.id
            print(f"  Created topic #{topic.id}: {topic.name}")

        # Second pass: update prerequisite_ids using the mapping
        for topic_data in topics_data:
            prereq_orders = topic_data.get("prerequisite_ids")
            if not prereq_orders:
                continue

            topic_id = display_order_to_id[topic_data["display_order"]]
            prereq_ids = [display_order_to_id[order] for order in prereq_orders]

            result = await session.execute(
                select(GrammarTopic).where(GrammarTopic.id == topic_id)
            )
            topic = result.scalar_one()
            topic.prerequisite_ids = prereq_ids

        await session.commit()
        print(f"\nImported {len(display_order_to_id)} grammar topics successfully")


async def main() -> None:
    """Main entry point."""
    # Default path relative to project root
    json_path = Path(__file__).parent.parent.parent / "dev" / "grammar_topics.json"

    # Use --clear flag to clear existing topics
    clear_existing = "--clear" in sys.argv

    # Check for custom path (non-flag arguments)
    for arg in sys.argv[1:]:
        if not arg.startswith("--"):
            json_path = Path(arg)
            break

    if not json_path.exists():
        print(f"Error: File not found: {json_path}")
        sys.exit(1)

    await import_topics(json_path, clear_existing=clear_existing)


if __name__ == "__main__":
    asyncio.run(main())
