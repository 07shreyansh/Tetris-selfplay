import pygame
from tetra import *
from display import *
from board import *
from pcPlayer import *
from direction import *
from rotation import *

#Bools that control game state
isOpen = True
newGame = True
gameOver = False
paused = False
selfPlay = False
locked = False

#Create game window and clock
window = Window()
draw = Draw(window)
draw.createScreen()
clock = pygame.time.Clock()

while isOpen:
    #Draw new Frame
    pygame.display.update()
    #Clear screen
    draw.screen.fill("Black")

    #reset board
    if newGame:
        board = Board()
        pcPlayer = PcPlayer(board)
        tetra = board.generatePiece()
        timeCount = 0
        draw.drawStartScreen(board)

    #newGame screen loop
        while newGame:
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    newGame = False
                    isOpen = False
                keyInput = pygame.key.get_pressed()
                if keyInput[pygame.K_p]:
                    newGame = False
                    selfPlay = False
                if keyInput[pygame.K_b]:
                    selfPlay = True
                    newGame = False

    #Pause / Start screen loop
    while paused:
        draw.drawPauseScreen()
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                paused = False 
                isOpen = False
            keyInput = pygame.key.get_pressed()
            if keyInput[pygame.K_ESCAPE]:
                paused = False
            if keyInput[pygame.K_n]:
                newGame = True
                paused = False
 
    gameFlags = [newGame, gameOver, paused, (not isOpen)]

    #gamePlay Loop
    while (not any(gameFlags)):
        
        #Draw game elements to screen
        draw.refreshScreen(board, tetra)
    
        #pcPlayer code
        if (selfPlay):
            if (board.isHeldPieceEmpty()):
                board.setHeldPiece(tetra)
            tetra = board.generatePiece()
            draw.refreshScreen(board, tetra)
            locked = board.moveOrLockPiece(tetra, Direction.DOWN)
            draw.refreshScreen(board, tetra)
            if (locked):
                tetra = board.newPieceOrGameOver(tetra)
                if tetra == None:
                    gameOver = True
                    break
            (swapPiece, position) = pcPlayer.choosePieceAndPosition(board, tetra)
            if (swapPiece):
                tetra = board.swapWithHeldPiece(tetra)
            draw.refreshScreen(board, tetra)
            pcPlayer.makeMove(board, tetra, position, draw)
            tetra = board.newPieceOrGameOver(tetra)
            draw.refreshScreen(board, tetra)
            if tetra == None:
                gameOver = True
                break

        #Step game forward
        timeCount += clock.get_rawtime()
        clock.tick()
        if (timeCount >= board.getDropInterval()):
            timeCount = 0
            locked = board.moveOrLockPiece(tetra, Direction.DOWN)
            if (locked):
                tetra = board.newPieceOrGameOver(tetra)
                if tetra == None:
                    gameOver = True
                    break
            draw.refreshScreen(board, tetra)

        #Check for user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                isOpen = False
            keyInput = pygame.key.get_pressed()
            if keyInput[pygame.K_ESCAPE]:
                paused = True
            if keyInput[pygame.K_n]:
                newGame = True
            #Game controls only if not bot
            if (not selfPlay):
                if keyInput[pygame.K_LCTRL] or keyInput[pygame.K_RCTRL]:
                    board.rotatePiece(tetra, Rotation.ANTICLOCKWISE)
                if keyInput[pygame.K_UP]:
                    board.rotatePiece(tetra, Rotation.CLOCKWISE)
                if keyInput[pygame.K_RIGHT]:
                    board.moveOrLockPiece(tetra, Direction.RIGHT)
                if keyInput[pygame.K_LEFT]:
                    board.moveOrLockPiece(tetra, Direction.LEFT)
                if keyInput[pygame.K_DOWN]:
                    locked = board.moveOrLockPiece(tetra, Direction.DOWN)
                    if (locked):
                        tetra = board.newPieceOrGameOver(tetra)
                        if tetra == None:
                            gameOver = True
                if keyInput[pygame.K_RETURN]:
                    board.dropAndLockPiece(tetra)
                    tetra = board.newPieceOrGameOver(tetra)
                    if tetra == None:
                        gameOver = True
                if keyInput[pygame.K_LSHIFT] or keyInput[pygame.K_RSHIFT]:
                    if (board.isHeldPieceEmpty()):
                        board.setHeldPiece(tetra)
                        tetra = board.generatePiece()
                    else:
                        tetra = board.swapWithHeldPiece(tetra)

        gameFlags = [newGame, gameOver, paused, (not isOpen)]

    #Game over screen loop
    while gameOver:
        draw.drawGameOver(board)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                gameOver = False
                isOpen = False
            keyInput = pygame.key.get_pressed()
            if keyInput[pygame.K_n] or keyInput[pygame.K_ESCAPE]:
                newGame = True
                gameOver = False
           