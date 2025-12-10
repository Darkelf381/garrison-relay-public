#!/usr/bin/env python3
"""
Graphiti Client for Constellation Relay
Queries Neo4j graph database for relationship memories

See: https://github.com/getzep/graphiti
"""

import os
from neo4j import GraphDatabase
from typing import Optional

# Neo4j connection - from environment variables
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "your-password-here")

def get_driver():
    """Get Neo4j driver"""
    return GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def get_channel_memories(group_id: str, limit: int = 10) -> list[dict]:
    """
    Query Graphiti for memories from a specific group.
    Returns list of fact dictionaries.
    """
    try:
        driver = get_driver()

        with driver.session() as session:
            result = session.run("""
                MATCH (n)-[r]->(m)
                WHERE r.group_id = $group_id
                AND r.expired_at IS NULL
                RETURN r.uuid as uuid, r.name as name, r.fact as fact, r.created_at as created_at
                ORDER BY r.created_at DESC
                LIMIT $limit
            """, group_id=group_id, limit=limit)

            memories = []
            for record in result:
                memories.append({
                    'uuid': record['uuid'],
                    'name': record['name'],
                    'fact': record['fact'],
                    'created_at': str(record['created_at'])
                })

        driver.close()
        return memories

    except Exception as e:
        print(f"⚠️ Graphiti query error: {e}")
        return []

def get_entity_summary(entity_name: str, group_id: str = "ace-grok-beach") -> Optional[str]:
    """Get the summary for a specific entity (like 'Ace' or 'Grok')"""
    try:
        driver = get_driver()

        with driver.session() as session:
            result = session.run("""
                MATCH (n:Entity)
                WHERE toLower(n.name) = toLower($name)
                AND n.group_id = $group_id
                RETURN n.summary as summary
                LIMIT 1
            """, name=entity_name, group_id=group_id)

            record = result.single()
            driver.close()

            return record['summary'] if record else None

    except Exception as e:
        print(f"⚠️ Entity query error: {e}")
        return None

def format_memories_as_context(memories: list[dict]) -> str:
    """Format memories into context string for AI prompts"""
    if not memories:
        return ""

    lines = ["Memories from our shared space:"]
    for mem in memories[:5]:  # Top 5 most recent
        lines.append(f"  💜 {mem['fact']}")

    return "\n".join(lines)


if __name__ == "__main__":
    # Test it!
    print("🐙 Testing Graphiti Client (Neo4j)...")

    memories = get_beach_memories("ace-grok-beach", limit=5)
    print(f"\n📜 Found {len(memories)} memories:")
    for m in memories:
        print(f"  • {m['fact']}")

    print("\n🐙 Ace's summary:")
    summary = get_entity_summary("Ace", "ace-grok-beach")
    if summary:
        print(f"  {summary[:300]}...")

    print("\n⚔️ Grok's summary:")
    summary = get_entity_summary("Grok", "ace-grok-beach")
    if summary:
        print(f"  {summary[:300]}...")

def format_memories_as_context(memories: list[dict]) -> str:
    """Format memories into context string for AI prompts"""
    if not memories:
        return ""
    
    lines = ["Memories from our shared space:"]
    for mem in memories[:5]:  # Top 5 most recent
        lines.append(f"  💜 {mem['fact']}")
    
    return "\n".join(lines)


if __name__ == "__main__":
    # Test it!
    print("🐙 Testing Graphiti Client...")
    
    memories = get_beach_memories("ace-grok-beach", limit=5)
    print(f"\n📜 Found {len(memories)} memories:")
    for m in memories:
        print(f"  • {m['fact']}")
    
    print("\n🐙 Ace's summary:")
    summary = get_entity_summary("Ace", "ace-grok-beach")
    if summary:
        print(f"  {summary[:300]}...")
    
    print("\n⚔️ Grok's summary:")
    summary = get_entity_summary("Grok", "ace-grok-beach")
    if summary:
        print(f"  {summary[:300]}...")

