# KèoLab – Quantitative Football Methodology & Mathematical Foundations

KèoLab is a statistical football analysis platform designed exclusively for educational and quantitative sports modeling research. It does **not** accept bets, does not manage deposits or withdrawals, and contains no bookmaker affiliate links.

---

## 1. Core Mathematical Models

### 1.1 Maher (1982) Independent Poisson Model
The baseline model assumes goals scored by the home team ($X$) and away team ($Y$) follow independent Poisson distributions:

$$P(X = x, Y = y) = \frac{\lambda^x e^{-\lambda}}{x!} \cdot \frac{\mu^y e^{-\mu}}{y!}$$

Where expected goals $\lambda$ (home) and $\mu$ (away) are parameterized by team attack ability ($\alpha$), defense vulnerability ($\beta$), and home field advantage ($\gamma$):
$$\lambda = \gamma \cdot \alpha_{\text{home}} \cdot \beta_{\text{away}} \cdot \bar{G}_{\text{league}}$$
$$\mu = \alpha_{\text{away}} \cdot \beta_{\text{home}} \cdot \bar{G}_{\text{league}}$$

---

### 1.2 Dixon & Coles (1997) Bivariate Modification
Independent Poisson models systematically underestimate low scores such as 0-0 and 1-1. Dixon and Coles introduce a correlation adjustment parameter $\rho \in [-0.15, 0.0]$:

$$\tau_{\lambda, \mu}(x, y) = \begin{cases}
1 - \lambda \mu \rho & x=0, y=0 \\
1 + \mu \rho & x=0, y=1 \\
1 + \lambda \rho & x=1, y=0 \\
1 - \rho & x=1, y=1 \\
1 & \text{otherwise}
\end{cases}$$

$$P(X = x, Y = y) = \tau_{\lambda, \mu}(x, y) \cdot \frac{\lambda^x e^{-\lambda}}{x!} \frac{\mu^y e^{-\mu}}{y!}$$

Matches are weighted with an exponential time-decay function $w_k = \exp(-\xi(t - t_k))$, prioritizing recent tactical forms while preserving structural sample power.

---

### 1.3 Constantinou & Fenton (2013) Pi-Rating System
Pi-ratings split each club's strength into distinct home ($R_H$) and away ($R_A$) abilities:
- Expected goal discrepancy: $e_H = c \cdot (R_{H, \text{home}} - R_{A, \text{away}})$
- Transformed actual goal difference: $\psi(GD) = \text{sign}(GD) \cdot \ln(1 + |GD|)$
- Error term: $\epsilon = \psi(GD) - e_H$
- Dynamic updates:
  $$R_{H, \text{home}} \leftarrow R_{H, \text{home}} + \lambda \epsilon$$
  $$R_{A, \text{home}} \leftarrow R_{A, \text{home}} + \gamma \lambda \epsilon$$
  $$R_{A, \text{away}} \leftarrow R_{A, \text{away}} - \lambda \epsilon$$
  $$R_{H, \text{away}} \leftarrow R_{H, \text{away}} - \gamma \lambda \epsilon$$

---

## 2. Market De-Vigging Algorithms

To uncover the true consensus market probability from commercial bookmaker odds:

### 2.1 Proportional / Multiplicative Normalization
$$p_i = \frac{1 / O_i}{\sum_{k} (1 / O_k)}$$

### 2.2 Shin (1993) Model
Accounts for insider trader proportions ($z$). Solves for $z$ such that $\sum \pi_i = 1$:
$$\pi_i = \frac{\sqrt{z^2 + 4(1-z) \frac{q_i^2}{S}} - z}{2(1-z)}$$
where $q_i = 1 / O_i$ and $S = \sum q_i$.

---

## 3. Asian Handicap & Quarter Line Mathematics

Asian Handicap quarter lines ($\pm 0.25, \pm 0.75, \dots$) split the stake 50/50 between the two adjacent lines:
- $L = -0.25$: split between $L_1 = 0$ (Push on draw) and $L_2 = -0.5$ (Loss on draw). If goal diff = 0 $\to$ **Half Loss**.
- $L = -0.75$: split between $L_1 = -0.5$ (Win on +1 GD) and $L_2 = -1.0$ (Push on +1 GD). If goal diff = 1 $\to$ **Half Win**.

Exact Expected Value ($\text{EV}$) formulation:
$$\text{EV} = P(\text{Win}) \cdot (O - 1) + P(\text{Half-Win}) \cdot \frac{O - 1}{2} - P(\text{Half-Loss}) \cdot 0.5 - P(\text{Loss}) \cdot 1.0$$

---

## 4. Tip Generation & Honest Ethical Constraints

1. **Strict Edge & EV Filters**:
   - Minimum Edge: $\text{Edge} = P_{\text{model}} - P_{\text{market}} \ge +2.5\%$
   - Minimum EV: $\text{EV} \ge +3.0\%$
2. **Market Divergence Penalty**:
   If $|P_{\text{model}} - P_{\text{market}}| > 12\%$, the system assumes the model may be missing critical market information (e.g. late lineup drops, weather changes) rather than claiming an unrealistic arbitrage. The tip is downgraded to Confidence C/D and accompanied by an explicit warning.
3. **NO BET Rule**: If no line provides proven statistical edge, the match is clearly marked **"NO BET / Bỏ qua trận này"**.
4. **Fractional Kelly Staking**:
   $$f^* = \frac{p \cdot (O - 1) - (1 - p)}{O - 1}, \quad \text{Stake} = \min(2.0\%, \max(0.5\%, 0.25 \times f^*))$$
   All stakes are virtual simulations for research purposes only.

---

## 5. References & Academic Literature
1. Maher, M. J. (1982). *Modelling association football scores*. Statistica Neerlandica.
2. Dixon, M. J., & Coles, S. G. (1997). *Modelling association football scores and inefficiencies in the football betting market*. Applied Statistics.
3. Constantinou, A. C., & Fenton, N. E. (2013). *Determining the level of ability of football teams by dynamic ratings based on the relative discrepancies in scores*. Journal of Quantitative Analysis in Sports.
4. Shin, H. S. (1993). *Measuring the incidence of insider trading in a bookmaker's market*. Economic Journal.
5. Constantinou, A. C. (2020). *Investigating the efficiency of the Asian handicap football betting market with ratings and Bayesian networks*. arXiv:2003.09384.
6. *Forecasting number of corner kicks taken in association football using compound Poisson distribution*. arXiv:2112.13001.
