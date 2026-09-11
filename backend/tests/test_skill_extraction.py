"""
Tests for the skill extraction pipeline's keyword-matching path,
which doesn't require the embedding model to be downloaded. The
semantic-matching path is exercised separately in
test_skill_extraction_semantic.py, which skips itself if
sentence-transformers isn't available.
"""
from app.models.skills import Skill
from app.ai.skill_extraction import extract_skills


def _seed_skills(db_session):
    db_session.add_all([
        Skill(name="Computer Troubleshooting", category="IT Support", skill_type="technical",
              synonyms="debugging computers, fixing computers, repairing computers"),
        Skill(name="Technical Support", category="IT Support", skill_type="technical",
              synonyms="tech support, help desk"),
        Skill(name="Teaching", category="Soft Skills", skill_type="soft", synonyms="training, tutoring"),
        Skill(name="Inventory Management", category="Business Operations", skill_type="technical",
              synonyms="inventory, stock management"),
    ])
    db_session.commit()


def test_keyword_extraction_matches_synonyms(db_session):
    _seed_skills(db_session)
    text = (
        "I repaired computers for my village, helped people install software, "
        "maintained a small shop's billing system, and taught basic computer usage to students."
    )
    results = extract_skills(text, db_session)
    names = {r.skill_name for r in results}

    assert "Computer Troubleshooting" in names  # via "repaired computers" synonym
    # "taught" is not a listed synonym for Teaching, so keyword-only matching
    # won't catch it here — this is exactly the gap the semantic path (Phase 8)
    # is meant to close once an embedding model is available.
    assert "Teaching" not in names


def test_extraction_returns_no_duplicate_skills(db_session):
    _seed_skills(db_session)
    text = "I fixed computers. I also spent time debugging computers for clients."
    results = extract_skills(text, db_session)
    skill_ids = [r.skill_id for r in results]
    assert len(skill_ids) == len(set(skill_ids))


def test_extraction_on_empty_taxonomy_returns_empty(db_session):
    results = extract_skills("Any text at all", db_session)
    assert results == []


def test_inventory_management_detected_from_informal_experience(db_session):
    _seed_skills(db_session)
    text = "I manage the accounts and inventory for my family's small business."
    results = extract_skills(text, db_session)
    names = {r.skill_name for r in results}
    assert "Inventory Management" in names
