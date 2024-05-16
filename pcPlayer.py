import copy
from tetra import *
from board import *
from direction import *

class PcPlayer:

    def clearPositionScores(self, board):
        self.positionScores = {}
        self.emptyRow = []
        for x in range(board.width):
            self.emptyRow.append(0)
        for rotationCount in range(4):
            dictRow = {rotationCount : copy.copy(self.emptyRow)}
            self.positionScores.update(dictRow)

    def __init__(self, board, holeWeight = 3, heightWeight = 9, columnWeight = 5):
        self.holeWeight = holeWeight
        self.heightWeight = heightWeight
        self.columnWeight = columnWeight
        self.columnHeightLimit = 3
        self.clearPositionScores(board)

    def moveFarLeft(self, board, tetra):
        while not (board.isOutOfBounds(tetra) or board.isGridBlocked(tetra)):
            tetra.incrementCoords(-1)
        tetra.incrementCoords(1)
    
    def scoreAllPositions(self, board, tetra):
        board.holeCount = self.getHoleAndColumnCount(board.grid)[0]
        board.columnCount = self.getHoleAndColumnCount(board.grid)[1]
        copyTet = copy.deepcopy(tetra)
        copyBoard = copy.deepcopy(board)
        for rotationCount in range(0, 4):
            for xPos in range(board.width):
                copyBoard.rotatePiece(copyTet, Rotation.CLOCKWISE, rotationCount)
                self.moveFarLeft(board, copyTet)
                copyBoard.moveOrLockPiece(copyTet, Direction.RIGHT, xPos)
                copyBoard.dropPieceWithoutLock(copyTet)
                copyBoard.moveLeftAndLockPiece(copyTet, 2)
                score = self.getPositionScore(board, copyTet)
                self.positionScores[rotationCount][xPos] = copy.copy(score)
                copyBoard = copy.deepcopy(board)
                copyTet = copy.deepcopy(tetra)
        
    def choosePieceAndPosition(self, board, tetra):
        swapPiece = False
        #Score the active tetra piece
        self.scoreAllPositions(board, tetra)
        tetMin = self.getMinScoreAndPosition()
        self.clearPositionScores(board)
        #Move a copy of the heldpiece into position and score
        heldPiece = copy.deepcopy(board.heldPiece)
        board.centrePiece(heldPiece)
        heldPiece.incrementCoords(tetra.xOffset, tetra.yOffset)
        self.scoreAllPositions(board, heldPiece)
        heldPieceMin = self.getMinScoreAndPosition()
        self.clearPositionScores(board)
        #Compare
        if (heldPieceMin[0] < tetMin[0]):
            position = (heldPieceMin[1], heldPieceMin[2])
            swapPiece = True
        else:
            position = (tetMin[1], tetMin[2])
        return (swapPiece, position)

    def getMinScoreAndPosition(self): 
        minScore = self.positionScores[0][0]
        width = len(self.positionScores[0])
        minScoreRotation = 0
        minScoreXPos = 0
        for rotation in self.positionScores.keys():
            for xPos in range(width):
                if (self.positionScores[rotation][xPos] < minScore):
                        minScore = self.positionScores[rotation][xPos]
                        minScoreRotation = rotation
                        minScoreXPos = xPos
        return (minScore, minScoreRotation, minScoreXPos)

    def getPositionScore(self, board, tetra):
        (holeScore, columnScore) = self.getHoleAndColumnScore(board, tetra)
        heightScore = self.getHeightScore(board, tetra)
        positionScore = holeScore + heightScore + columnScore
        return positionScore

    def getHeightScore(self, board, tetra):
        positionHeight = board.height - tetra.getMinYCoord()
        heightScore = (positionHeight / board.height) * self.heightWeight
        return heightScore

    def getHoleAndColumnScore(self, board, tetra):
        grid = copy.deepcopy(board.grid)
        for coord in tetra.blockCoords:
            y = int(coord[1])
            x = int(coord[0])
            grid[y][x] = 1
        (newHoleCount, newColumnCount) = self.getHoleAndColumnCount(grid)
        holeScore = ((newHoleCount - board.holeCount)) * self.holeWeight
        columnScore = ((newColumnCount - board.columnCount)) * self.columnWeight
        return (holeScore, columnScore)

    def getHoleAndColumnCount(self, grid):
        gridHeight = len(grid.keys())
        gridWidth = len(grid[0])
        holeCount = 0
        columnCount = 0
        columnList = [None] * gridWidth
        for x in range(gridWidth):
            emptyCount = 0
            for y in range(gridHeight-1, 0, -1):
                if (grid[y][x] == 0):
                    emptyCount += 1
                else:
                    holeCount += emptyCount
                    emptyCount = 0
            columnList[x] = emptyCount
        if columnList[0] >= (columnList[1] + self.columnHeightLimit):
            columnCount += 1
        if columnList[gridWidth-1] >= (columnList[gridWidth-2]+self.columnHeightLimit):
            columnCount += 1
        for i in range(1, gridWidth-2, 1):
            if ((columnList[i] >= (columnList[i-1] + self.columnHeightLimit)) and (columnList[i] >= (columnList[i+1] + self.columnHeightLimit))):
                columnCount += 1          
        return (holeCount, columnCount)

    def makeMove(self, board, tetra, position, draw):
        rotationCount = position[0]
        xPos = position[1]
        board.rotatePiece(tetra, Rotation.CLOCKWISE, rotationCount)
        draw.refreshScreen(board, tetra)
        self.moveFarLeft(board, tetra)
        board.moveOrLockPiece(tetra, Direction.RIGHT, xPos)
        board.dropPieceWithoutLock(tetra)
        board.moveLeftAndLockPiece(tetra, 2)
        draw.refreshScreen(board, tetra)