#RULES  
This module package has a lot of rules for calculating MMR for games  
List of this rules:  

 - Game win:  
   Calculate MMR for this rule:  
   **If:**  
   * rating <= 1700:  
   bonus win: 9, lose: -6  

   * rating <= 1800:  
   bonus win: 8, lose: -6  

   * rating <= 1900:  
   bonus win: 7, lose: -7  

   After every +100 MMR bonus down by 1 for win  
   After every +200 MMR bonus down by 1 for lose  

 - Miss:  
   Calculate MMR for this rule:  
   If mafia lose game and had misses - mafias players will get -3 points MMR  

   Points for this rule (`constants.py`):  
   `CORRELATION_FOR_MISS_FROM_MAFIA` for miss from mafia  

 - Devise:
   Calculate MMR for this rule (only for citizens):   

   If device is right and team win -> big bonus  
   If device is right and team loose -> small bonus  
   If device is wrong and team loose -> big minus  
   If device is wrong and team win -> small minus  

   Points for this rule (`constants.py`):  
   `[LOW|BIG]_BONUS_FOR_CORRECT_DEVISE_FOR_[3|2|1]` bonuses for correct devises  
   `[LOW|BIG]_CORRELATION_FOR_WRONG_DEVISE_FOR_[3|2|1]` correlations for uncorrect devises  

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
   `CORRELATION_FOR_VOTED_THREE_CITIZEN_TO_CITIZEN` for citizen  

 - Wrong Break:  
   Calcalute MMR for this rule:  
   If player break into player with his team  
   And his team didn't win   
   He will get -3 bonus MMR points  

   Points for this rule (`constants.py`):  
   `CORRELATION_FOR_WRONG_BREAK` for wrong break  

 - Best Player:  
   Calculate MMR for this rule:  
   If player get 3 and more bonuses from other player  
   He will get 1 point bonus to his MMR  

   Points for this rule (`constants.py`):  
   `BONUS_FOR_BEST_PLAYER` for 3 bonuses from other  

 - Hand of mafia:  
   Calculate MMR for this rule:  
   If player was hand of mafia - he will get -2 points MMR  

   `CORRELATION_FOR_BEING_HAND_OF_MAFIA` for hand of mafia  

 - Sheriff play:  
   Calculate MMR for this rule:  
   If sheriff player won game - he will get 1 point MMR bonus  

   Points for this rule (`constants.py`):  
   `BONUS_FOR_SHERIFF_PLAY` for sheriff play  

 - Disqualifield:  
   Calculate MMR for this rule:  
   If player was disqualifield from game - he will get -5 MMR points  

   Points for this rule (`constants.py`):  
   `CORRELATION_FOR_DISQUALIFIELD_PLAYER` for disqualifield player  

 - Sheriff version play:  
   Calculate MMR bonus for this rule:  
   If mafia play like sheriff and her team win - he will get 1 mmr point  

   Points for this rule (`constants.py`):  
   `BONUS_FOR_PLAYING_LIKE_SHERIFF` for playing and winning   

 - Bonus heading:  
   Calculate MMR for this rule:  
   If player got 0.1 - 0.2 points from heading - we will get 1 point MMR  
   Else if player got 0.3 - 0.4 points from heading - we will get 2 point MMR  
   Else if player got more than 0.5 points from heading - we will get 3 point MMR  

   Points for this rule (`constants.py`):  
   `LOW_BONUS_FROM_HEADING` for 0.1-0.2 points  
   `MIDDLE_BONUS_FROM_HEADING` for 0.3-0.4 points  
   `HIGH_BONUS_FROM_HEADING` for > 0.5 points    
