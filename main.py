#VERSION 0.2.2
import random
from copy import deepcopy
import pygame, sys
from collections import defaultdict

class MancalaGame():
    def __init__(self, stones_in_each_spot=4, spots_on_each_side=6):
        self.stones_in_each_spot=stones_in_each_spot
        self.spots_on_each_side=spots_on_each_side
        self.turn=0 #who goes first
        self.state0=[stones_in_each_spot for _ in range (spots_on_each_side)] #player 0 state
        self.state1=[stones_in_each_spot for _ in range (spots_on_each_side)] #player 1 state
        self.gameState=[self.state0,self.state1,0,0] #game stате
        self.skipped=False #if current turn is skipped
        # self.history=[]

    def getPossMoves(self): #of the form "skip", 0, 1, 2, 3,...
        if self.skipped:
            return [-1] #skip
        return [spot[0] for spot in enumerate(self.gameState[self.turn]) if spot[1]!=0]

    def enemy(self, turn):
        return (turn+1)%2

    def makeMove(self, move): #makes a move.
        def increment(hand, loc, side): #calculates where to put the stone next
            hand-=1
            loc+=1
            if loc>=self.spots_on_each_side:
                if side==self.turn:
                    loc=-1
                    side=self.enemy(side)
                else:
                    loc=0
                    side=self.enemy(side)
            return hand, loc, side
            
        self.skipped=False
        if move!=-1: #if this turn is not skipped
            self.history.append(deepcopy(self.gameState))
            hand=self.gameState[self.turn][move] #how many stones in hand
            self.gameState[self.turn][move]=0 #take all stones out
            side=self.turn #which side of board we are on
            loc=move #location of where to put stone
            while hand: #while you have stones in hand
                hand, loc, side = increment(hand, loc, side)
                if loc==-1: #if you are over the score spot
                    self.gameState[2+self.turn]+=1
                else: #add stone to normal spot
                    self.gameState[side][loc]+=1
            if side==self.turn and self.gameState[side][loc]==1: #if turn ends on an empty spot on own side
                self.gameState[2+self.turn]+=self.gameState[self.enemy(side)][self.spots_on_each_side-1-loc] #add to own score
                self.gameState[self.enemy(side)][self.spots_on_each_side-1-loc]=0 #remove opposite stones across
            if loc==-1: #if you end in your score spot
                self.skipped=True #skip next turn
        self.turn=self.enemy(self.turn) #switch turn

    def isWin(self, possMoves):
        if not possMoves:
            scoreTurn=self.gameState[2+self.turn]
            scoreEnemy=self.stones_in_each_spot*self.spots_on_each_side*2-scoreTurn
            if scoreTurn>scoreEnemy: #turn wins
                return self.turn
            elif scoreTurn<scoreEnemy: #enemy wins
                return self.enemy(self.turn)
            else: #draw
                return 0.5
        return -1 #not end of game

class CUI():
    def __init__(self):
        self.ai0=MiniMaxAI(10)
        self.ai1=MiniMaxAI(10)
        self.game=MancalaGame(3,4)
        looping=True
        while looping:
            self.printBoard()
            possMoves=self.game.getPossMoves()
            sPossMoves=[str(move) for move in possMoves]
            isWin=self.game.isWin(possMoves)
            if isWin==1:
                print("1 won")
                print(self.ai0.getScoreWin(self.game))
                looping=False
            elif isWin==0:
                print("0 won")
                print(self.ai0.getScoreWin(self.game))
                looping=False
            elif isWin==0.5:
                print("draw")
                print(self.ai0.getScoreWin(self.game))
                looping=False
            else:
                if self.game.turn==0:
                    inp=str(self.ai0.getMove(self.game, possMoves))
                else:
                    #inp=random.choice(sPossMoves) ##
                    #inp=input() ##
                    inp=str(self.ai1.getMove(self.game, possMoves)) ##
            if inp=="end":
                looping=False
            elif inp in sPossMoves:
                self.game.makeMove(int(inp))
            elif inp=="poss":
                print(possMoves)
            elif inp=="turn":
                print(self.game.turn)
    def printBoard(self):
        print()
        print(self.game.turn)
        for spot in self.game.state1[::-1]:
            print(spot, end=" ")
        print()
        print(self.game.gameState[3],end="         ")
        print(self.game.gameState[2])
        for spot in self.game.state0:
            print(spot, end=" ")
        print()

class MiniMaxAI():
    def __init__(self, depth=0):
        self.depth=depth
    def getMove(self, game, possMoves):
        if len(possMoves)==1:
            return possMoves[0]
        move=possMoves.pop(random.randint(0,len(possMoves)-1))
        temp_game=deepcopy(game)
        temp_game.makeMove(move)
        bestScore=self.minimax(temp_game, self.depth, temp_game.turn, temp_game.getPossMoves(), -1000000, 1000000)
        bestMove=move
        for move in possMoves:
            temp_game=deepcopy(game)
            temp_game.makeMove(move)
            temp_score=self.minimax(temp_game, self.depth, temp_game.turn, temp_game.getPossMoves(), -1000000, 1000000)
            if game.turn==0:
                if temp_score>bestScore:
                    bestMove=move
                    bestScore=temp_score
            elif game.turn==1:
                if temp_score<bestScore:
                    bestMove=move
                    bestScore=temp_score
        return bestMove
    
    def minimax(self, game, depth, turn, possMoves, alpha, beta): #returns minimax score with alpha-beta pruning
        # print(str(depth)+" deep")
        if game.isWin(possMoves)==0:
            score=1000*self.getScoreWin(game)
            # print(str(score)+str(game.gameState))
            return score
        elif game.isWin(possMoves)==1:
            score=1000*self.getScoreWin(game)
            # print(str(score)+str(game.gameState))
            return score
        elif game.isWin(possMoves)==0.5:
            score=0
            # print(str(score)+str(game.gameState))
            return score
        if depth == 0:
            score=self.getScore(game)
            # print(str(score)+str(game.gameState))
            return score
        if turn==0:
            score = -10000000
            for move in possMoves:
                # print(str(move)+" sub")
                temp_game=self.altDeepcopy(game)
                temp_game.makeMove(move)
                score = max(score, self.minimax(temp_game, depth-1, 1, temp_game.getPossMoves(), alpha, beta))
                alpha=max(alpha,score)
                # for some reason this part of pruning doesn't work
                if beta <= alpha: 
                    break
            return score
        else: #turn=1
            score = 10000000
            for move in possMoves:
                # print(str(move)+" sub")
                temp_game=self.altDeepcopy(game)
                temp_game.makeMove(move)
                score = min(score, self.minimax(temp_game, depth-1, 0, temp_game.getPossMoves(), alpha, beta))
                beta=min(beta,score)
                if beta <= alpha:
                    break
            return score
    
    def altDeepcopy(self, game): #chaper version of deepcopy
        new=MancalaGame(game.stones_in_each_spot, game.spots_on_each_side)
        new.turn=game.turn
        new.state0=game.state0[:]
        new.state1=game.state1[:]
        new.gameState=[new.state0,new.state1,game.gameState[2],game.gameState[3]]
        new.skipped=game.skipped
        return new


    def getScore(self, game):
        return game.gameState[2]-game.gameState[3]+(sum(game.gameState[0])-sum(game.gameState[1]))*0.01
    
    def getScoreWin(self, game):
        return game.gameState[2]-game.gameState[3]+(sum(game.gameState[0])-sum(game.gameState[1]))*1

class GUI():
    def __init__(self):
        self.backgroundColor=(153, 102, 51)
        self.spotColor=(115, 77, 38)
        self.unit=70
        pygame.init()
        self.clock = pygame.time.Clock()
        self.WIN_WIDTH = 800
        self.WIN_HEIGHT = 600
        self.winCenter=(self.WIN_WIDTH//2,self.WIN_HEIGHT//2)
        self.boardCenter=self.winCenter
        self.win = pygame.display.set_mode((self.WIN_WIDTH, self.WIN_HEIGHT))
        self.pressedButtons=defaultdict(lambda: False)
        pygame.display.set_caption("Mancala")
        self.introLoop()
        pygame.quit()
        sys.exit()

    def introLoop(self): #loop for intro
        self.mode="PvP"
        self.startBlankGame()
        self.spotDict=self.makeSpotDict()
        gameOn = True 
        while gameOn:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            self.win.fill((255,255,255))
            self.createText("Welcome to Mancala",self.WIN_WIDTH//2,self.WIN_HEIGHT*1//3,45,(0,0,0))
            self.createButton("new", "New Game",180,350,150,70, (170,170,170), (140,140,140), 20, self.loopReturn, "mode_select")
            #self.createButton("rules", "Rules",470,350,150,70, (170,170,170), (140,140,140), 20, self.loopReturn, "rules_from_intro")
            pygame.display.update()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

    def modeSelectLoop(self):
        looping = True 
        while looping:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            self.win.fill((255,255,255))
            self.createText("Please select game mode",self.WIN_WIDTH//2,self.WIN_HEIGHT//4,45,(0,0,0))
            self.createButton("back", "back", self.WIN_WIDTH-100,0,100,30, (170,170,170), (140,140,140), 20, self.loopReturn, "intro")
            self.createButton( "pvp", "Human vs. Human", 200,200,400,60, (170,170,170), (140,140,140), 20, self.loopReturn, "play")
            self.createButton("pvai","Human vs. Computer", 200,270,400,60, (170,170,170), (140,140,140), 20, self.loopReturn, "ai_select_in_pvai")
            self.createButton("aivp","Computer vs. Human", 200,340,400,60, (170,170,170), (140,140,140), 20, self.loopReturn, "ai_select_in_aivp")
            self.createButton("aivai", "Computer vs. Computer",  200,410,400,60, (170,170,170), (140,140,140), 20, self.loopReturn, "ai_select_in_aivai")
            pygame.display.update()
            self.clock.tick(60)
        return

    def aiDiffSelectLoop(self):
        looping = True 
        while looping:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            self.win.fill(self.backgroundColor)
            self.createText("Please select computer difficulty",self.WIN_WIDTH//2,self.WIN_HEIGHT//4,45,(0,0,0))
            self.createButton("back", "back", self.WIN_WIDTH-100,0,100,30, (170,170,170), (140,140,140), 20, self.loopReturn, "mode_select")
            self.createButton( "easy", "Easy", 200,200,400,60, (170,170,170), (140,140,140), 20, self.loopReturn, "playEasy")
            self.createButton("ok", "Okay", 200,270,400,60, (170,170,170), (140,140,140), 20, self.loopReturn, "playMedium")
            self.createButton("decent","Decent", 200,340,400,60, (170,170,170), (140,140,140), 20, self.loopReturn, "playHard")
            self.createButton("expert", "Expert",  200,410,400,60, (170,170,170), (140,140,140), 20, self.loopReturn, "playExpert")
            pygame.display.update()
            self.clock.tick(60)
        return

    def loopReturn(self, loop): #cotrols which loop to run
        if loop=="intro":
            self.introLoop()
        # elif loop=="rules_from_intro":
        #     self.rulesLoop("intro")
        # elif loop=="rules_from_move":
        #     self.rulesLoop("play")
        elif loop=="mode_select":
            self.modeSelectLoop()
        elif loop=="ai_select":
            self.aiDiffSelectLoop()
        elif loop=="ai_select_in_pvai":
            self.mode="PvAI"
            self.aiDiffSelectLoop()
        elif loop=="ai_select_in_aivp":
            self.mode="AIvP"
            self.aiDiffSelectLoop()
        elif loop=="ai_select_in_aivai":
            self.mode="AIvAI"
            self.aiDiffSelectLoop()
        elif loop=="playEasy":
            self.ai=MiniMaxAI(1)
            self.playLoop()
        elif loop=="playMedium":
            self.ai=MiniMaxAI(5)
            self.playLoop()
        elif loop=="playHard":
            self.ai=MiniMaxAI(8)
            self.playLoop()
        elif loop=="playExpert":
            self.ai=MiniMaxAI(10)
            self.playLoop()
        elif loop=="play":
            self.playLoop()
        else:
            print("ERROR: not a loop")
    
    def playLoop(self):
        looping=True
        while looping:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            self.win.fill(self.backgroundColor)
            self.drawBoard()
            self.drawPieces()
            pygame.display.update()
            self.clock.tick(60)

            possMoves= self.game.getPossMoves()
            isWin=self.game.isWin(possMoves)
            if isWin==1:
                print("1 won")
                self.clock.tick(1)
                pygame.quit()
                sys.exit()
            elif isWin==0:
                print("0 won")
                # print(self.game.history)
                self.clock.tick(1)
                pygame.quit()
                sys.exit()
            elif isWin==0.5:
                print("draw")
                self.clock.tick(1)
                pygame.quit()
                sys.exit()
            if self.game.turn==0:
                if self.mode in {"AIvAI", "AIvP"}:
                    move=self.ai.getMove(self.game, possMoves)
                    self.game.makeMove(move)
                else:
                    move=self.waitForMoveLoop(possMoves)
                    self.game.makeMove(move)
            else: #turn =1
                if self.mode in {"AIvAI", "PvAI"}:
                    move=self.ai.getMove(self.game, possMoves)
                    self.game.makeMove(move)
                else:
                    move=self.waitForMoveLoop(possMoves)
                    self.game.makeMove(move)
 
    def waitForMoveLoop(self, possMoves): #SHOULD return the move that the human wants to make
        def getSpot(mouse, possMoves):
            for possMove in possMoves:
                location=self.spotDict[(self.game.turn,possMove)]
                if -self.unit//2<location[0]-mouse[0]<self.unit//2 and -self.unit//2<location[1]-mouse[1]<self.unit//2:
                    print("move: "+str(possMove))
                    return possMove
            return "Not Valid"
        if possMoves==[-1]:
            return -1
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse = pygame.mouse.get_pos()
                    spot=getSpot(mouse, possMoves)
                    if spot!="Not Valid":
                        return spot

            self.createButton("chmod","Change Mode", 5,5,145,30, (170,170,170), (140,140,140), 20, self.loopReturn, "mode_select")
            if self.mode!="PvP":
                self.createButton("chdiff","Change Difficulty", 155,5,185,30, (170,170,170), (140,140,140), 20, self.loopReturn, "ai_select")
            self.drawBoard()
            self.drawPieces()
            pygame.display.update()
            self.clock.tick(60)

    def startBlankGame(self): #starts a blank game
        self.game=MancalaGame()

    def createText(self, text, x, y, size, color): #creates a line of text
        font = pygame.font.Font('freesansbold.ttf',size)
        TextSurf, TextRect = self.text_objects(text, font, color)
        TextRect.center = (x,y)
        self.win.blit(TextSurf,TextRect)

    def createButton(self, name, text, left, top, width, height, inactiveColor, activeColor, fontSize, action=None, arg=None): #creates a clickable button, calls action on release
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        if left<mouse[0]<left+width and top<mouse[1]<top+height:
            self.drawRoundedRect(self.win, activeColor, (left,top,width,height), 7) #if mouse is over button
            if click[0]==1 and action!=None:
                self.pressedButtons[name]=True
            if click[0]==0 and action!=None and self.pressedButtons[name]==True:
                self.pressedButtons[name]=False
                if arg!=None:
                    action(arg)
                else:
                    action()
        else:
            self.drawRoundedRect(self.win, inactiveColor, (left,top,width,height),7)  #if mouse not over button
            self.pressedButtons[name]=False
        self.createText(text, left+width//2, top+height//2, fontSize, (0,0,0))#draw button
    
    def text_objects(self, text, font, color): #creates a pair for text objects
        textSurface = font.render(text, True, color)
        return textSurface, textSurface.get_rect()

    def drawRoundedRect(self, win, color, dims, radius): #draws a rounded rectangle; dims: (left,top,width,height)
        pygame.draw.rect(win, color, (dims[0]+radius, dims[1]+radius, dims[2]-2*radius, dims[3]-2*radius))
        for spot in [(dims[0]+radius,dims[1]+radius),(dims[0]+radius,dims[1]+dims[3]-radius),(dims[0]+dims[2]-radius,dims[1]+radius),(dims[0]+dims[2]-radius,dims[1]+dims[3]-radius)]:
            pygame.draw.circle(win, color, spot, radius)
        for pair in [[(dims[0]+radius-1,dims[1]+radius-1),(dims[0]+radius-1,dims[1]+dims[3]-radius)],[(dims[0]+radius-1,dims[1]+radius-1),(dims[0]+dims[2]-radius,dims[1]+radius-1)],[(dims[0]+dims[2]-radius,dims[1]+radius-1),(dims[0]+dims[2]-radius,dims[1]+dims[3]-radius)],[(dims[0]+dims[2]-radius,dims[1]+dims[3]-radius),(dims[0]+radius-1,dims[1]+dims[3]-radius)]]:
            pygame.draw.line(win, color, pair[0], pair[1], radius*2)

    def drawBoard(self): #draws the game board
        margin=5
        for side in range(2):
            for spot in range(self.game.spots_on_each_side):
                loc=self.spotDict[(side,spot)]
                dims=(loc[0]-self.unit//2+margin,loc[1]-self.unit+margin,self.unit-margin*2,self.unit*2-margin*2)
                self.drawRoundedRect(self.win, self.spotColor, dims, 7)

        loc=self.spotDict["score0"]
        dims=(loc[0]-self.unit//2+margin,loc[1]-self.unit*2+margin,self.unit-margin*2,self.unit*4-margin*2)
        self.drawRoundedRect(self.win, self.spotColor, dims, 7)
        loc=self.spotDict["score1"]
        dims=(loc[0]-self.unit//2+margin,loc[1]-self.unit*2+margin,self.unit-margin*2,self.unit*4-margin*2)
        self.drawRoundedRect(self.win, self.spotColor, dims, 7)
        

    def drawPieces(self): #draws the pieces of a given game
        for spot in range(self.game.spots_on_each_side): #player 0
            loc=self.spotDict[(0,spot)]
            self.createText(str(self.game.gameState[0][spot]),loc[0],loc[1],45,(0,0,0))
        for spot in range(self.game.spots_on_each_side): #player 1
            loc=self.spotDict[(1,spot)]
            self.createText(str(self.game.gameState[1][spot]),loc[0],loc[1],45,(0,0,0))
        loc=self.spotDict["score0"]
        self.createText(str(self.game.gameState[2]),loc[0],loc[1],45,(0,0,0))
        loc=self.spotDict["score1"]
        self.createText(str(self.game.gameState[3]),loc[0],loc[1],45,(0,0,0))

    def makeSpotDict(self): #creates dict with all the spots
        dic={}
        backStart=self.unit*(self.game.spots_on_each_side-1)//2
        for spot in range(self.game.spots_on_each_side):
            dic[(0,spot)]=(self.boardCenter[0]-backStart+self.unit*spot,self.boardCenter[1]+self.unit)
        for spot in range(self.game.spots_on_each_side):
            dic[(1,spot)]=(self.boardCenter[0]+backStart-self.unit*spot,self.boardCenter[1]-self.unit)
        dic["score0"]=(self.boardCenter[0]+backStart+self.unit,self.boardCenter[1])
        dic["score1"]=(self.boardCenter[0]-backStart-self.unit,self.boardCenter[1])
        return dic

if __name__=="__main__":
    GUI()




