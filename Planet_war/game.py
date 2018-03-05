import math
from EnemyAlgorithm import Enemy
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QFont, QImage
from PyQt5.QtCore import Qt, QBasicTimer, QRect


def associateNodes(node1, node2):
    if node1 == node2:
        return
    edgeFrom1To2 =Edge(node1.coord[0], node1.coord[1], node2)
    edgeFrom2To1 =Edge(node2.coord[0], node2.coord[1], node1)
    node1.edgeMass.append(edgeFrom1To2)
    node1.edgeMassTo.append(edgeFrom2To1)
    node2.edgeMass.append(edgeFrom2To1)
    node2.edgeMassTo.append(edgeFrom1To2)

def transformToColour( string):
    if string == 'blue':return Qt.blue
    elif string == 'red':return Qt.red
    elif string == 'green':return Qt.green
    return  Qt.black

class MoveSoldier:
    def __init__(self, colour, image , startPoint):
        self.colour = colour
        self.image = image
        self.moveTime = startPoint

class Edge:
    def __init__(self, x1, y1, toNode ):
        self.lineX = toNode.coord[0] - x1
        self.lineY = toNode.coord[1] - y1
        self.lineLength = math.sqrt(self.lineX ** 2 + self.lineY ** 2)
        self.coord = [x1, y1]
        self.soldiers = []
        self.toNode = toNode

    def moveFunction(self, movementTime):
        return (movementTime / self.lineLength * self.lineX, movementTime / self.lineLength * self.lineY)

    def timerSteep(self , speedFactor):
        i = 0
        while i < len(self.soldiers):
            self.soldiers[i].moveTime += 0.25*speedFactor
            if self.soldiers[i].moveTime + self.toNode.radius > self.lineLength:
                self.attakNode(self.soldiers[i].colour)
                del self.soldiers[i]
            else:
                i += 1

    def attakNode(self, soldierColour ):
        if self.toNode.colour == soldierColour:
            self.toNode.soldierAmount += 1
            if not(self.toNode.isActive) and self.toNode.soldierAmount >= self.toNode.soldierToActive:
                self.toNode.isActive = True
        elif self.toNode.soldierAmount > 0:
            self.toNode.soldierAmount -= 1
        else:
            self.toNode.soldierAmount = 1
            self.toNode.isActive = False
            self.toNode.colour = soldierColour

class Node:
    def __init__(self, coord, radius, colour, imageStorage, isActive = False, solderAmount = 0, solderCreateRate=500, solderSendRate = 80, soldierToActive =10):
        self.coord = coord
        self.radius = radius
        self.colour = colour
        self.imageStorage = imageStorage
        self.soldierAmount = solderAmount
        self.soldierCreateRate = solderCreateRate
        self.sendRate = solderSendRate
        self.edgeMass = []
        self.edgeMassTo = []
        self.sendEdge = NotImplemented
        self.isActive = isActive
        self.soldierToActive = soldierToActive

    def checkMouseClick(self, x, y, sizeFactor):
        return (self.coord[0] * sizeFactor - x) ** 2 + (
                self.coord[1] * sizeFactor - y) ** 2 < self.radius * self.radius * sizeFactor * sizeFactor

    def sendArmyToNode(self, node):
        for edge in self.edgeMass:
            if edge.toNode == node:
                self.sendEdge = edge

    def timerSteep(self, time , speedFactor):
        if self.isActive:
            if time % int(self.soldierCreateRate / speedFactor) == 0:
                self.soldierAmount += 1
            if (self.sendEdge != NotImplemented) and (self.soldierAmount >= 1) and (time % int(self.sendRate/ speedFactor) == 0):
                self.soldierAmount -= 1
                self.sendEdge.soldiers.append(MoveSoldier(self.colour, self.imageStorage.getImage(self.isActive, self.colour, True) , self.radius))
        for edge in self.edgeMass:
            edge.timerSteep(speedFactor)

    def drawNode(self, qp, sizeFactor):
        qp.setPen(QPen(QBrush(self.colour) , 4))
        qp.setBrush(self.colour)
        if self.sendEdge != NotImplemented :
            qp.drawLine(self.coord[0]*sizeFactor ,
                        self.coord[1] *sizeFactor,
                        (self.coord[0] + self.sendEdge.moveFunction(self.radius*2)[0])*sizeFactor ,
                        (self.coord[1] + self.sendEdge.moveFunction(self.radius*2)[1])*sizeFactor      )
        rect = QRect((self.coord[0] - self.radius) * sizeFactor, (self.coord[1] - self.radius) * sizeFactor, self.radius * 2 * sizeFactor, self.radius * 2 * sizeFactor)
        qp.drawImage(rect, self.imageStorage.getImage(self.isActive, self.colour, False))
        if self.isActive:
            qp.setPen(Qt.black)
        else:
            qp.setPen(self.colour)
        if self.soldierAmount == 0 and not self.isActive :
            return
        qp.setFont(QFont("Cleo", self.radius * sizeFactor * 3.0 / 4.0, QFont.Bold, False))
        qp.drawText(rect, Qt.AlignCenter, str(self.soldierAmount))

    def drawSoldiers(self, qp, sizeFactor):
        for edge in self.edgeMass:
            for soldier in edge.soldiers:
                solderCoord = edge.moveFunction(soldier.moveTime)
                rect = QRect((self.coord[0] + solderCoord[0] - 5) * sizeFactor, (self.coord[1] + solderCoord[1] - 5) * sizeFactor, 10 * sizeFactor, 10 * sizeFactor)
                qp.drawImage(rect, soldier.image)

class ImageStorage:
    def __init__(self , passiveNodeImage , activeNodeImageMap):
        self.passiveNodeImage = passiveNodeImage
        self.activeNodeImageMap =activeNodeImageMap
    def getImage(self, isActiveNode , nodeColour , forSoldier):
        if not isActiveNode:
            return self.passiveNodeImage
        return self.activeNodeImageMap[nodeColour][int(forSoldier)]

class Game(QWidget):
    def __init__(self, filePatch , menu):
        super().__init__()

        self.menu = menu
        file = open(filePatch+"\\gameSettings.txt")
        gameSettings = file.read().split(' ')
        file.close()
        self.sizeFactor = 1
        self.startSize = int(gameSettings[2])
        self.setGeometry(int(gameSettings[0]), int(gameSettings[1]), int(gameSettings[2]), int(int(gameSettings[2]) * 101 / 192))
        self.playerColor = transformToColour(gameSettings[3])
        self.enemyColor = transformToColour(gameSettings[4])
        self.show()
        imageInfo = open(filePatch+"\\imageStorage.txt").read().split('\n')
        passiveNodeImage = QImage(imageInfo[0])
        self.background = QImage(imageInfo[1])
        activeNodeImageMap = {}
        for i in range (3,3 + int(imageInfo[2])):
            patchInfo = imageInfo[i].split(' ')
            activeNodeImageMap.update({transformToColour( patchInfo[0]):[QImage(patchInfo[1]) , QImage(patchInfo[2])] } )
        self.imageStorage = ImageStorage(passiveNodeImage , activeNodeImageMap)

        self.nodeMass = []
        nodeMassInfo = open(filePatch+"\\nodeMass.txt").read().split('\n')
        for i in range (1 , int(nodeMassInfo[0]) +1):
            nodeInfo = nodeMassInfo[i].split(' ')
            self.nodeMass.append(Node([int(nodeInfo[0]) , int(nodeInfo[1]) ] , int(nodeInfo[2]) , transformToColour(nodeInfo[3]) , self.imageStorage , bool(nodeInfo[4]=='True') , int(nodeInfo[5]) ))
            
        edgeMassInfo = open(filePatch+"\\edgeMass.txt").read().split('\n')
        for i in range (1 , int(edgeMassInfo[0]) +1):
            edgeInfo = edgeMassInfo[i].split(' ')
            associateNodes(self.nodeMass[int(edgeInfo[0])] , self.nodeMass[int(edgeInfo[1])] )
        self.enemy = Enemy(self.enemyColor, self.playerColor)
        self.selectedNode = NotImplemented
        self.soldierCurrentSum = [0 ,0]
        self.endGame = False
        self.timerSteep = 10
        self.speedFactor = 2
        self.maxTimerSpeedFactor = 5
        self.time = 0
        self.timer = QBasicTimer()
        self.soldierAmount()
        self.show()

    def resizeEvent(self, event):
        self.sizeFactor = event.size().width() / self.startSize
        self.setFixedHeight(event.size().width() * 101 / 192)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.menu.show()
            self.close()
        else:
            if event.key() == Qt.Key_Space:
                if self.timer.isActive():
                    self.timer.stop()
                    self.repaint()
                elif not self.endGame :
                    self.timer.start(self.timerSteep , self)
                else:
                    self.menu.show()
                    self.close()
            elif event.key() == Qt.Key_Down and self.speedFactor > 1:
                    self.speedFactor -=1
                    self.repaint()
            elif event.key() == Qt.Key_Up and self.speedFactor < self.maxTimerSpeedFactor:
                    self.speedFactor +=1
                    self.repaint()

    def mousePressEvent(self, event):
        for node in self.nodeMass:
            if node.checkMouseClick(event.pos().x(), event.pos().y(), self.sizeFactor) and (self.selectedNode != NotImplemented or node.colour == self.playerColor):
                if self.selectedNode == NotImplemented:
                    self.selectedNode = node
                elif self.selectedNode == node:
                    self.selectedNode.sendEdge = NotImplemented
                    self.selectedNode = NotImplemented
                else:
                    self.selectedNode.sendArmyToNode(node)
                    self.selectedNode = NotImplemented
                self.repaint()

    def timerEvent(self, event):
        self.time += 1
        for node in self.nodeMass:
            node.timerSteep(self.time , self.speedFactor)
        self.soldierAmount()
        self.checkEndGame()
        self.enemy.timerSteep(self.nodeMass)
        self.repaint()

    def soldierAmount(self):
        self.soldierCurrentSum = [0,0]
        for node in self.nodeMass:
            node.realSoldierAmount = node.soldierAmount
            if node.colour == self.playerColor : self.soldierCurrentSum[0] += node.soldierAmount
            elif node.colour == self.enemyColor : self.soldierCurrentSum[1] += node.soldierAmount
            for edge in node.edgeMassTo:
                for soldier in edge.soldiers :
                    if soldier.colour == node.colour :node.realSoldierAmount += 1
                    else:node.realSoldierAmount -= 1
                    if soldier.colour == self.playerColor:self.soldierCurrentSum[0] += 1
                    elif soldier.colour == self.enemyColor:self.soldierCurrentSum[1] += 1

    def checkEndGame(self):
        if self.soldierCurrentSum[0] <= 0 or self.soldierCurrentSum[1] <=0:
            self.endGame = True
            self.timer.stop()

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        qp.drawImage(event.rect(), self.background)
        qp.setFont(QFont("Cleo", self.startSize * self.sizeFactor / 48, QFont.Bold, False))

        playerSoldierAmountRect = QRect(self.startSize * self.sizeFactor * 15 / 16,
                                             self.startSize * self.sizeFactor * 38 / 192,
                                             self.startSize * self.sizeFactor / 16,
                                             self.startSize * self.sizeFactor / 16)
        enemySoldierAmountRect = QRect(self.startSize * self.sizeFactor * 15 / 16,
                                            self.startSize * self.sizeFactor * 50 / 192,
                                            self.startSize * self.sizeFactor / 16,
                                            self.startSize * self.sizeFactor / 16)
        speedRect = QRect(self.startSize * self.sizeFactor * 15 / 16, self.startSize * 89 / 192 * self.sizeFactor,
                               self.startSize * self.sizeFactor / 16, self.startSize * self.sizeFactor / 16)
        speedRectValue = QRect(self.startSize * self.sizeFactor * 15 / 16,
                                   self.startSize * 95 / 192 * self.sizeFactor,
                                   self.startSize * self.sizeFactor / 16, self.startSize * self.sizeFactor / 32)


        qp.setBrush(QBrush(self.playerColor, Qt.Dense5Pattern))
        qp.drawRect(playerSoldierAmountRect)
        qp.drawText(playerSoldierAmountRect, Qt.AlignCenter, str(self.soldierCurrentSum[0]))

        qp.setBrush(QBrush(self.enemyColor, Qt.Dense5Pattern))
        qp.drawRect(enemySoldierAmountRect)
        qp.drawText(enemySoldierAmountRect, Qt.AlignCenter, str(self.soldierCurrentSum[1]))

        qp.setFont(QFont("Cleo", self.startSize * self.sizeFactor / 80, QFont.Bold, False))
        qp.setBrush(QBrush(Qt.darkGray, Qt.Dense5Pattern))
        qp.drawRect(speedRect)
        qp.drawText(speedRect, Qt.AlignTop, str("Speed"))
        qp.drawText(speedRectValue, Qt.AlignCenter, str( self.speedFactor ))

        for node in self.nodeMass:
            for edge in node.edgeMass:
                qp.drawLine(edge.coord[0] * self.sizeFactor, edge.coord[1] * self.sizeFactor,(edge.coord[0] + edge.lineX) * self.sizeFactor, (edge.coord[1] + edge.lineY) * self.sizeFactor)
        for node in self.nodeMass:
            node.drawSoldiers(qp, self.sizeFactor)
        if self.selectedNode != NotImplemented:
            qp.setPen(QPen(QBrush(Qt.NoBrush), 0))
            qp.setBrush(QBrush(Qt.darkCyan, Qt.Dense4Pattern))
            qp.drawEllipse((self.selectedNode.coord[0] - self.selectedNode.radius * 5.0 / 4.0) * self.sizeFactor,
                           (self.selectedNode.coord[1] - self.selectedNode.radius * 5.0 / 4.0) * self.sizeFactor,
                           (self.selectedNode.radius * 5.0 / 2.0) * self.sizeFactor,
                           (self.selectedNode.radius * 5.0 / 2.0) * self.sizeFactor)
        for node in self.nodeMass:
            node.drawNode(qp, self.sizeFactor)

        if not self.timer.isActive():
            qp.setFont(QFont("Cleo", self.startSize * self.sizeFactor / 16, QFont.Bold, False))
            if not self.endGame:
                qp.drawText(event.rect() , Qt.AlignCenter, "Pause")
            elif self.soldierCurrentSum[0] == 0:
                qp.setPen(self.enemyColor)
                qp.drawText(event.rect(), Qt.AlignCenter, "Enemy Win")
            else:
                qp.setPen(self.playerColor)
                qp.drawText(event.rect(), Qt.AlignCenter, "Player Win")
        qp.end()