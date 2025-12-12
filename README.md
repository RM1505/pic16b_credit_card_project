# pic16b_credit_card_project
We plan to build a credit card reward optimizer that (1) recommends credit cards based on client card history, spending habits, and goals and (2) integrates a proxy credit card that connects a client's cards and distributes purchases to maximize rewards and cash back.

## Pitch
Credit cards are complicated. The AMEX Platinum, for example, advertises thousands of dollars in annual benefits for a sub-$1,000 fee, but those benefits are scattered across vouchers (such as Uber & Resy), variable-value Membership Rewards points, and experiential perks (such as airport lounges). Complex reward structures mean many cardholders never realize anything close to the advertised value.

We propose a Credit-Card Reward Optimizer to give consumers a real, measurable advantage. 
* Phase 1 (MVP): build a web scraper and normalized database of U.S. consumer credit-card offers and reward rules, then deliver a personalized recommender that matches a user’s historical spending to the cards that maximize their net benefit. 
* Phase 2 (stretch): create a “proxy” mechanism that routes or allocates purchases across a user’s cards to realize combined rewards (initially via actionable recommendations and virtual card tokens; later, explore automated routing where feasible).

## Group Contribution Statement
Rigel: Built custom web scrapers for major issuers, cleaners, scraped credit card tiers.
Sasha: Parsed data from web scrapers into clean, usable dataframes.
Ameer: Developed optimization framework to incorporate trigger-based reward bonuses.
Angela: Found dollars per point values for major issuers, rewards handling, built front end (NiceGUI).
