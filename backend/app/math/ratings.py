import math
from typing import Tuple, Dict


class EloRatingSystem:
    """
    Elo Rating System for football with home advantage and margin-of-victory scaling.
    """

    def __init__(self, base_k: float = 24.0, home_adv: float = 65.0):
        self.base_k = base_k
        self.home_adv = home_adv

    def expected_prob(self, home_elo: float, away_elo: float) -> Tuple[float, float]:
        """Calculates expected outcome probability for home and away teams."""
        dr = (home_elo + self.home_adv) - away_elo
        e_home = 1.0 / (1.0 + math.pow(10.0, -dr / 400.0))
        e_away = 1.0 - e_home
        return e_home, e_away

    def update(
        self,
        home_elo: float,
        away_elo: float,
        home_score: int,
        away_score: int
    ) -> Tuple[float, float]:
        """
        Updates Elo ratings based on match result.
        Returns: (new_home_elo, new_away_elo)
        """
        e_home, e_away = self.expected_prob(home_elo, away_elo)

        gd = home_score - away_score
        if gd > 0:
            s_home, s_away = 1.0, 0.0
        elif gd == 0:
            s_home, s_away = 0.5, 0.5
        else:
            s_home, s_away = 0.0, 1.0

        # Margin of Victory multiplier
        mov_multiplier = 1.0 + math.log(1.0 + abs(gd))
        k = self.base_k * mov_multiplier

        new_home_elo = home_elo + k * (s_home - e_home)
        new_away_elo = away_elo + k * (s_away - e_away)

        return round(new_home_elo, 2), round(new_away_elo, 2)


class PiRatingSystem:
    """
    Pi-rating system (Constantinou & Fenton 2013).
    Separates home ability and away ability for each team.
    """

    def __init__(self, c: float = 3.0, learning_rate: float = 0.07, cross_weight: float = 0.35):
        self.c = c
        self.lambda_rate = learning_rate
        self.gamma_rate = cross_weight

    def expected_goal_diff(self, home_team_r_home: float, away_team_r_away: float) -> float:
        """Expected discrepancy in goals based on home ability vs away ability."""
        return self.c * (home_team_r_home - away_team_r_away)

    def psi_goal_diff(self, goal_diff: int) -> float:
        """Diminishing returns transform for goal difference."""
        sign = 1.0 if goal_diff > 0 else (-1.0 if goal_diff < 0 else 0.0)
        return sign * math.log(1.0 + abs(goal_diff))

    def update(
        self,
        home_r_h: float,
        home_r_a: float,
        away_r_h: float,
        away_r_a: float,
        home_score: int,
        away_score: int
    ) -> Tuple[float, float, float, float]:
        """
        Updates (home_r_h, home_r_a, away_r_h, away_r_a)
        """
        gd = home_score - away_score
        exp_gd = self.expected_goal_diff(home_r_h, away_r_a)
        actual_transformed = self.psi_goal_diff(gd)
        error = actual_transformed - exp_gd

        # Update home team
        new_home_rh = home_r_h + self.lambda_rate * error
        new_home_ra = home_r_a + self.gamma_rate * self.lambda_rate * error

        # Update away team
        new_away_ra = away_r_a - self.lambda_rate * error
        new_away_rh = away_r_h - self.gamma_rate * self.lambda_rate * error

        return (
            round(new_home_rh, 4),
            round(new_home_ra, 4),
            round(new_away_rh, 4),
            round(new_away_ra, 4)
        )
