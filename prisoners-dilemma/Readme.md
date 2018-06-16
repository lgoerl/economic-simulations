## The Prisoner's Dilemma

The classic prisoner's dilemma is the dilemma that two co-consipirators face when being interrogated: do they betray their accomplice to receive a reduced sentence, or do they remain loyal, lying to the authorities and receiving no sentence. Of course, if they both betray one another, they maximum sentence will be issued to each.

The iterated prisoner's dilemma in these simulations is setup to create agents on a grid, which determines their neighbors and who they compete against (only those adjacent to themeselves). Each round the agents play a single game against each neighbor. In the original simulation, the agents have the opportunity to switch strategies. 

### Genetic algorithm
The simulation implementing a genetic algorithm to determine the behavior of the agents does not allow for the option of using any other strategy. Agents are randomly assigned a strategy, receive points for winning which contributes to their `fitness` score, and procreate if their score is above some threshold. In addition to genetic variance through offspring, there are genetic mutations. 

At each 10 steps a heatmap plot is created. 