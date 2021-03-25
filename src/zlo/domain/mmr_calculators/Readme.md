This module package has a lot of rules for calculating MMR for games
List of this rules:
 - Best Move:  
   Calculate MMR for this rule:  
   If in best move player has 2 mafia - he will get 2 MMR bonus  
   Else if in best move player has 3 mafia - he will get 3 points  
   
   Points for this rule (`constants.py`):  
   `BONUS_FOR_2_GUESS_MAFIA_IN_BEST_MOVE` for 2 guessing  
   `BONUS_FOR_3_GUESS_MAFIA_IN_BEST_MOVE` for 3 guessing
   
 - Three voted:
   Calculate MMR for this rule:  
   In round with 9 players 3 citizens were voted  
   Citizens will get -2 MMR points (without first killed)  
   Mafias will get +2 MMR to points  
   
   Points for this rule (`constants.py`):  
   `BONUS_FOR_VOTED_THREE_CITIZEN_TO_MAFIA` for mafias bonus  
   `BONUS_FOR_VOTED_THREE_CITIZEN_TO_CITIZEN` for citizen  
 - e.t.c.
