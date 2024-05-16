import copy, random
from tetra import *
from direction import *
from rotation import *

class Board:
    _lineScores = (0, 1, 3, 5, 8)

    def emptyGrid(self):
        self.grid = {}
        self.emptyRow = []
        for x in range(self.width):
            self.emptyRow.append(0)
        for rowCount in range(self.height):
            gridRow = {rowCount : copy.copy(self.emptyRow)}
            self.grid.update(gridRow)

    def __init__(self, colour = "Gray"):
        self.colour = colour
        self.width = 10
        self.height = 21
        self.heldPiece = None
        self.startInterval = 1000
        self.score = 0
        self.linesCleared = 0
        self.level = 1
        self.levelScore = 0 
        self.emptyGrid()
        self.holeCount = None
        self.pieceList = []

    def setHeldPiece(self, tetra):
        self.heldPiece = Tetra(tetra.shape, tetra.rotations, tetra.colour)

    def isHeldPieceEmpty(self):
        return (self.heldPiece == None)

    def swapWithHeldPiece(self, tetra):
        copyTetromino = copy.deepcopy(tetra)
        tetra = copy.deepcopy(self.heldPiece)
        self.centrePiece(tetra)
        tetra.incrementCoords(copyTetromino.xOffset, copyTetromino.yOffset)
        self.setHeldPiece(copyTetromino)
        return (tetra)

    def centrePiece(self, tetra):
        tetra.centre[0] = tetra.centre[0] + (self.width/2) - 2
        for coord in tetra.vertexCoords:
            coord[0] += (self.width/2) - 2
        for coord in tetra.blockCoords:
            coord[0] += (self.width/2) - 2 
        
    def generatePiece(self):
        if (len(self.pieceList) == 0):
            self.pieceList = list(Tetra._allShapes.keys())
            random.shuffle(self.pieceList)
        tetra = Tetra(self.pieceList.pop())
        self.centrePiece(tetra)
        return (tetra)

    def isOutOfBounds(self, tetra):
        minX = tetra.getMinXCoord()
        maxX = tetra.getMaxXCoord()
        minY = tetra.getMinYCoord()
        maxY = tetra.getMaxYCoord()
        if (minX < 0) or (minY < 0) or (maxX > self.width) or (maxY > self.height):
            return True
        else:
            return False

    def moveOrLockPiece(self, tetra, direction, count = 1):
        x = direction.value[0]
        y = direction.value[1]
        for i in range(count):
            tetra.incrementCoords(x, y)
            if (self.isOutOfBounds(tetra) or self.isGridBlocked(tetra)):
                tetra.incrementCoords(-x,-y)
                if (y > 0):
                    self.lockPieceOnGrid(tetra)
                    clearedRowCount = self.clearFullRows()
                    self.updateScores(clearedRowCount)
                    return True
        return False

    def updateScores(self, clearedRowCount):
        self.linesCleared += clearedRowCount
        self.score += (self._lineScores[clearedRowCount] * self.level)
        if (self.level < 15):
            self.level = (self.linesCleared // 10) + 1

    def getDropInterval(self):
        scale = pow(0.8, self.level)
        dropInterval = int(self.startInterval * scale)
        return dropInterval

    def isGridBlocked(self, tetra):
        for coord in tetra.blockCoords:
            y = int(coord[1])
            x = int(coord[0])
            if self.grid[y][x] != 0:
                return True
        return False

    def lockPieceOnGrid(self, tetra):
        for coord in tetra.blockCoords:
            y = int(coord[1])
            x = int(coord[0])
            self.grid[y][x] = copy.copy(tetra.colour)
    
    def clearFullRows(self):
        fullRowCount = 0
        y = self.height - 1
        while (y > 0):
            emptyBlocks = 0
            for x in range(self.width):
                if self.grid[y][x] == 0:
                    emptyBlocks +=1
            if emptyBlocks == self.width:
                return fullRowCount
            elif emptyBlocks == 0:
                fullRowCount += 1
                self.grid[y] = copy.copy(self.emptyRow)
                for i in range (y, 1, -1):
                    self.grid[i] = copy.deepcopy(self.grid[i-1])
                y += 1
            y-=1
        return fullRowCount
         
    def rotatePiece(self, tetra, rotation = None, count = 1):
        for i in range(count):
            tetra.rotateCoords(rotation)
            if (self.isOutOfBounds(tetra) or self.isGridBlocked(tetra)):
                tetra.rotateCoords(-rotation)
                break

    def newPieceOrGameOver(self, tetra):
        if (tetra.xOffset == 0) and (tetra.yOffset == 0):
            return None
        else:
            tetra = self.generatePiece()
            return tetra
    
    def dropAndLockPiece(self, tetra):
        isLocked = False
        while (not isLocked):
            isLocked = self.moveOrLockPiece(tetra,Direction.DOWN)

    def dropPieceWithoutLock(self, tetra):
            while not ((self.isOutOfBounds(tetra) or self.isGridBlocked(tetra))):
                tetra.incrementCoords(0, 1)
            tetra.incrementCoords(0, -1)
    
    def moveLeftAndLockPiece(self, tetra, count):
        self.moveOrLockPiece(tetra, Direction.LEFT, count)
        self.dropAndLockPiece(tetra)