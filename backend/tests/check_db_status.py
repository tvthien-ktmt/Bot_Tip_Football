from backend.app.core.database import SessionLocal
from backend.app.models.entities import Match, League, Team, Tip

def main():
    db = SessionLocal()
    print("=== ACTIVE LEAGUES IN DB ===")
    for l in db.query(League).filter_by(active=True).all():
        n_sched = db.query(Match).filter_by(league_id=l.id, status='SCHEDULED').count()
        n_tips = db.query(Tip).join(Match).filter(Match.league_id == l.id).count()
        print(f"League {l.code} ({l.name}): {n_sched} scheduled matches, {n_tips} tips")

    print("\n=== SAMPLE CHAMPIONSHIP MATCHES ===")
    champ = db.query(League).filter_by(code='E1').first()
    matches = db.query(Match).filter_by(league_id=champ.id, status='SCHEDULED').order_by(Match.date.asc()).limit(5).all()
    for m in matches:
        tip = db.query(Tip).filter_by(match_id=m.id).first()
        tip_str = f"TIP: {tip.selection} @{tip.odds} (Grade {tip.confidence_grade})" if tip else "NO BET"
        print(f"{m.date} | {m.home_team.name} vs {m.away_team.name} | AH {m.ah_line} | {tip_str}")

    print("\n=== SAMPLE PREMIER LEAGUE MATCHES ===")
    pl = db.query(League).filter_by(code='E0').first()
    pl_matches = db.query(Match).filter_by(league_id=pl.id, status='SCHEDULED').order_by(Match.date.asc()).limit(5).all()
    for m in pl_matches:
        tip = db.query(Tip).filter_by(match_id=m.id).first()
        tip_str = f"TIP: {tip.selection} @{tip.odds} (Grade {tip.confidence_grade})" if tip else "NO BET"
        print(f"{m.date} | {m.home_team.name} vs {m.away_team.name} | AH {m.ah_line} | {tip_str}")

    # Verify Birmingham in Championship
    birm = db.query(Team).filter_by(name='Birmingham').first()
    print("\nBirmingham in DB:", birm.name if birm else "NOT FOUND")
    buli = db.query(Team).filter_by(name='Bundesliga').first()
    print("Bundesliga as a team in DB:", buli.name if buli else "None (Correct!)")

    db.close()

if __name__ == "__main__":
    main()
