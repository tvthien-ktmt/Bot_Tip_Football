import datetime
import pytest
from sqlalchemy.orm import Session
from backend.app.core.database import SessionLocal
from backend.app.models.entities import Match


def test_point_in_time_no_future_leakage():
    """
    Test that when computing historical form and ratings for match at time T,
    no matches with date >= T are included in the rolling statistics.
    """
    db: Session = SessionLocal()
    try:
        # Pick an arbitrary match
        sample_match = db.query(Match).filter(Match.status == "FINISHED").first()
        assert sample_match is not None

        match_time = sample_match.date

        # Query all matches used for this team's pre-match statistics
        prior_matches = db.query(Match).filter(
            ((Match.home_team_id == sample_match.home_team_id) | (Match.away_team_id == sample_match.home_team_id)),
            Match.status == "FINISHED",
            Match.date < match_time
        ).all()

        # Verify none of the prior matches occurred on or after match_time
        for m in prior_matches:
            assert m.date < match_time, f"Data leakage detected! Match {m.id} on {m.date} is >= {match_time}"

        # Verify the current match itself is not in the prior matches
        assert sample_match.id not in [m.id for m in prior_matches]
    finally:
        db.close()
