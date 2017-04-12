import strategies, random, utils, os, pickle, plot, bisect
from pprint import pprint
from collections import namedtuple, OrderedDict
from path import path
from namedlist import namedlist 
from operator import itemgetter
#from recordtype import *
#from utils import make_path

#constants
N_AGENTS_ACR = N_AGENTS_DOWN = 25
total_agents = N_AGENTS_ACR * N_AGENTS_DOWN
IT_PER_ROUND = 40
win_width = 4 + N_AGENTS_ACR
win_height = 4 + N_AGENTS_DOWN
num_strats = len(strategies.ALL)
#payoffs
MUTUAL_C = 3
MUTUAL_D = 1
SCREWER = 5
SCREWED = 0
BREEDERS=36
#admin
TIME0UT_RATE = 100 #milliseconds between frames
N_ROUNDS = 500
MEM=['CCCCCC','CCCCCD','CCCCDC','CCCCDD','CCCDCC','CCCDCD','CCCDDC','CCCDDD','CCDCCC','CCDCCD','CCDCDC','CCDCDD','CCDDCC','CCDDCD','CCDDDC','CCDDDD','CDCCCC','CDCCCD','CDCCDC','CDCCDD','CDCDCC','CDCDCD','CDCDDC','CDCDDD','CDDCCC','CDDCCD','CDDCDC','CDDCDD','CDDDCC','CDDDCD','CDDDDC','CDDDDD','DCCCCC','DCCCCD','DCCCDC','DCCCDD','DCCDCC','DCCDCD','DCCDDC','DCCDDD','DCDCCC','DCDCCD','DCDCDC','DCDCDD','DCDDCC','DCDDCD','DCDDDC','DCDDDD','DDCCCC','DDCCCD','DDCCDC','DDCCDD','DDCDCC','DDCDCD','DDCDDC','DDCDDD','DDDCCC','DDDCCD','DDDCDC','DDDCDD','DDDDCC','DDDDCD','DDDDDC','DDDDDD']



NEIGHBORS = 4

iteration_count = 0 # 0 == first iteration of the round of iterations
rounds_played = 0 

Edge = namedtuple('Edge', ['agent0','agent1','moves0','moves1'])

POINTS = {
	('C','C'):(MUTUAL_C, MUTUAL_C),
	('D','D'):(MUTUAL_D, MUTUAL_D),
	('D','C'): (SCREWER, SCREWED),
	('C','D'): (SCREWED, SCREWER),
	}
		
class Agent():
	def __init__(self):
		self.points = float(1)
		
		self.neighborhood = [self]
		self.denominator = SCREWER * IT_PER_ROUND * NEIGHBORS
		
		self.meta=[]
		self.SEQ = [random.choice(['C','D']) for i in range(64)]
		for i in range(len(self.SEQ)): self.meta.append([0,0])
		self.strat=genalg
		self.gns=namedlist('gns',OrderedDict(zip(MEM,self.SEQ)))
		self.genes=self.gns()
		self.doinit=0
		
		
	def __repr__(self):
		return 'Agent: %s' %(self.points)
		
	def fitness(self): self.fitness=self.points/self.denominator

	def calcScore(self):
		score = float(self.points) 
		return score
		
	def mutate(self):
	'''eventually i want this to be "smart" in that there's some way of seeing which thing to switch: 
		and additionally, making the change differently if mutating or breeding. '''
		self.changed=[]
		self.fitness=[]
		for i in range(len(MEM)):
			if self.meta[i][0] != 0: self.fitness.append([self.meta[i][1]/self.meta[i][0],i])
			else: self.fitness.append([0,i])
		
		templist=sorted(self.fitness,key=itemgetter(0))
		
		tobechanged=MEM[templist[next(i for i, x in enumerate(templist) if x[0]!=0)][1]]
		self.changed.append(tobechanged)
		if getattr(self.genes,tobechanged)=='C': setattr(self.genes,tobechanged,'D')
		else: setattr(self.genes,tobechanged,'C')
		
		
		
	
		

def createAgents():
	agents = [ [Agent() for y in range(N_AGENTS_DOWN)] \
		for x in range(N_AGENTS_ACR) ]
	return agents

def createNetworks(agents):
	conx_acr = len(agents) - 1; conx_down = len(agents[0]) - 1
	hz_network = []
	vt_network = []
	for network, horiz, vert, mod_x, mod_y in (
		(hz_network, conx_acr,  N_AGENTS_DOWN, 1, 0),
		(vt_network, N_AGENTS_ACR,  conx_down, 0, 1),
	):
		for x in range(horiz):
			newlist = []
			network.append(newlist)
			for y in range(vert):
				agent0 = agents[x][y]
				agent1 = agents[x+mod_x][y+mod_y]
				rist=str()
				rist=rist.join(random.choice(['C','D']) for _ in range(6))
				edge = Edge(agent0=agent0, agent1=agent1, moves0=rist, moves1=rist[1]+rist[0]+rist[3]+rist[2]+rist[5]+rist[4])
				newlist.append(edge)
				agent0.neighborhood.append(agent1)
				agent1.neighborhood.append(agent0)
	return hz_network, vt_network	
	
def genalg(iteration_count, player, oppo, player_moves, oppo_moves):
	"""3-memory per opponent (via edge defn), gives 64 possible (ordered) outcomes of last 3 games, string is the play for each."""
	#THIS WORKS DIFFERENTLY THAN THE OTHER STRATEGIES!!!!!!!!!
	past3=player_moves[-6:]
	return getattr(player.genes,past3)
	
	
def playPrisonersDilemma(edge):
	'''one iteration of the prisoner's dilemma between 
	two neighboring agents -- agents C or D'''
	agent0, agent1, moves0, moves1 = edge
	move0 = genalg(iteration_count, agent0, agent1,
				moves0, moves1)
	move1 = genalg(iteration_count, agent1, agent0,
				moves1, moves0)
	edge.moves0+=move0+move1
	edge.moves0=edge.moves0[-6:]
	edge.moves1+=move1+move0
	edge.moves1=edge.moves1[-6:]
	points0, points1 = POINTS[(move0, move1)]
	agent0.points += points0
	agent1.points += points1
	agent0.meta[agent0.genes._fields.index(moves0[-6:])][0]+=1
	agent0.meta[agent0.genes._fields.index(moves0[-6:])][1]+=points0
	agent1.meta[agent1.genes._fields.index(moves1[-6:])][0]+=1
	agent1.meta[agent1.genes._fields.index(moves1[-6:])][1]+=points1
	
def findMoves(agent0, agent1):
	move0 = genalg(iteration_count=iteration_count,
		opponent=agent1,player=agent0)
	move1 = genalg(iteration_count=iteration_count,
		opponent=agent0,player=agent1)
	return move0, move1

class Simulation():	
	def __init__(self, figs):
		self.agents = createAgents()
		self.networks = createNetworks(self.agents)
		self.figpath = path(figs)
		if self.figpath.exists():
			self.figpath.move(make_path(self.figpath))
		if not self.figpath.exists():
			self.figpath.mkdir()
		for file in self.figpath.files():
			file.remove()
		self.flat_list_of_agents = [agent for lineofagents in self.agents \
			for agent in lineofagents]
		
	def playOneIteration(self):
		for network in self.networks:
			for listofedges in network:
				for edge in listofedges:
					playPrisonersDilemma(edge)
	def playOneRound(self):
		global iteration_count
		for iteration_count in range(IT_PER_ROUND):
			print('.')
			self.playOneIteration()
		print
		
		
			
	def breed(self):
		total=sum([agent.points for agent in self.flat_list_of_agents])
		probs=[agent.points/total for agent in self.flat_list_of_agents]
		#normed=zip(self.flat_list_of_agents, probs)
		#normed=sort(normed, key=itemgetter(1), reverse=True)
		BINS=[sum(probs[0:i]) for i in range(len(self.flat_list_of_agents)-1)]
		randumb=[random.random() for i in range(BREEDERS)]
		parents=[bisect.bisect_left(BINS,randumb[i]) for i in range(BREEDERS-1)]
		pairs=[]
		random.shuffle(parents)
		for i in range(int(BREEDERS/2)): 
			pair=[parents[0],parents[1]]
			for i in range(1): parents.remove(pair[i])
			pairs.append(pair)
		for i in range(len(pairs)):
			agent0=self.flat_list_of_agents[pairs[i][0]]
			agent1=self.flat_list_of_agents[pairs[i][1]]
			SEQ0=agent0.SEQ
			SEQ1=agent1.SEQ
			crossover=random.randint(0,63)
			SEQ00=SEQ0[0:crossover]+SEQ1[crossover:]
			SEQ10=SEQ1[0:crossover]+SEQ0[crossover:]
			agent0.SEQ=SEQ00
			agent1.SEQ=SEQ10
			agent0.genes=agent0.gns()
			agent1.genes=agent1.gns()
			agent0.doinit+=1
			agent1.doinit+=1
			rist=str()
			rist=rist.join(random.choice(['C','D']) for _ in range(6))
			edge = Edge(agent0=agent0, agent1=agent1, moves0=rist, moves1=rist[1]+rist[0]+rist[3]+rist[2]+rist[5]+rist[4])
			
			
			
			
	def printView(self):
		plot.plotAgents(self.agents)
		self.save()
		
	def prepareNextRound(self):
		for agent in self.flat_list_of_agents:
			agent.points = float(1)

	def save(self):
		plot.savefig(self.figpath.joinpath('%05d.png' % rounds_played))

	def pickle(self):
		pickle.dump(self.agents, open(self.picklepth.joinpath('%05d.p' % rounds_played),'w'))
	
	def mainLoop(self):
		global rounds_played
		for rounds_played in range(N_ROUNDS):
			print(rounds_played)
			self.breed()
			self.playOneRound()
			mutants=[random.randint(0,len(self.flat_list_of_agents)-1) for i in range(50)]
			for i in range(50):
				self.flat_list_of_agents[mutants[i]].mutate()
			self.printView()
			self.prepareNextRound()


if __name__ == '__main__':
	simulation = Simulation('figs')
	simulation.mainLoop()
