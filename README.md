# Estimating_Credit_Rating_Transition_Matrices_Hazard_Vs_Cohort_Method
Estimating Credit Rating Transition Matrices in Python using Hazard and Cohort Methods

In this Python notebook, we use two estimation procedures, the cohortcohort approach and the hazardhazard approach to build historical credit risk transition matrices.
The  cohortcohort  approach is the traditional technique, much easier to develop. However, it can lead to some transition probabilities being equal to zero!
This might cause a problem, if you are looking to price a particular credit derivative with payoff linked to this event.
In addition, the cohort approach does not allow to calculate the transitions between periods.

The hazardhazard approach uses the timing and sequencing of transitions within the period.
One consequence is that events so rare in real credit history which are seldom observed empirically, are still given probabilities different from zero. So with this approach we are able to price the above credit derivative.

Its most important benefit is that, under certain conditions, it allows to create transition probabilities for any period of time.

The Cohort and Hazard methods are implemented as a class "TransitionClass", which, in turn, uses several pandas objects to construct the transition events and their times.

Please note I have also saved in the folder a very good paper, "Finding Generators for Markov Chains via Empirical Transition Matrices, with Applications to Credit Ratings, by Robert B. Israel, Jeffrey S. Rosenthal and Jason Z. Wei", which explores those conditions.
