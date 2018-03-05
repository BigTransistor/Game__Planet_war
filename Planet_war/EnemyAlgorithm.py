class Enemy:
    def __init__(self, color, playerColor):
        self.__color = color
        self.__playerColor = playerColor

    def timerSteep(self, nodeMass):
        enemyNodeMass = []
        for node in nodeMass:
            if node.colour == self.__color and node.isActive:
                enemyNodeMass.append(node)
        findPlayer = False
        findPassiveNode = False
        for node in enemyNodeMass:
            node.danger = 0
            node.wayToPlayer = NotImplemented
            node.wayToPassiveNode = NotImplemented
            for edge in node.edgeMass:
                if edge.toNode.colour == self.__playerColor:
                    node.danger += edge.toNode.soldierAmount
                    node.wayToPlayer = 0
                    findPlayer = True
                elif not edge.toNode.isActive:
                    node.wayToPassiveNode = 0
                    findPassiveNode = True
        if findPlayer:
            notAllFindWay = True
            i = 0
            while notAllFindWay and i < len(enemyNodeMass):
                i += 1
                notAllFindWay = False
                for node in enemyNodeMass:
                    for edge in node.edgeMass:
                        if edge.toNode.colour == self.__color and edge.toNode.isActive and edge.toNode.wayToPlayer != NotImplemented and (
                                node.wayToPlayer == NotImplemented or edge.toNode.wayToPlayer < node.wayToPlayer):
                            node.wayToPlayer = edge.toNode.wayToPlayer + 1
                    if node.wayToPlayer == NotImplemented:
                        notAllFindWay = True

        if findPassiveNode:
            notAllFindWay = True
            i = 0
            while notAllFindWay and i < len(enemyNodeMass):
                notAllFindWay = False
                i += 1
                for node in enemyNodeMass:
                    for edge in node.edgeMass:
                        if edge.toNode.colour == self.__color and edge.toNode.isActive and edge.toNode.wayToPassiveNode != NotImplemented and (
                                node.wayToPassiveNode == NotImplemented or edge.toNode.wayToPassiveNode + 1 < node.wayToPassiveNode):
                            node.wayToPassiveNode = edge.toNode.wayToPassiveNode + 1
                    if node.wayToPassiveNode == NotImplemented:
                        notAllFindWay = True
        for node in enemyNodeMass:
            if (node.wayToPassiveNode == NotImplemented or node.wayToPassiveNode != 0) and (
                    node.wayToPlayer == NotImplemented or node.wayToPlayer != 0):
                self.supportProtocol(node, findPlayer, findPassiveNode)
            else:
                self.attackProtocol(node)
                self.defanceProtocol(node)

    def supportProtocol(self, node, findPlayer, findPassiveNode):
        node.sendEdge = NotImplemented
        for edge in node.edgeMass:
            if edge.toNode.realSoldierAmount < 0 and (
                    node.sendEdge == NotImplemented or edge.toNode.realSoldierAmount < node.sendEdge.toNode.realSoldierAmount):
                node.sendEdge = edge
        if node.sendEdge != NotImplemented:
            return
        if findPlayer:
            for edge in node.edgeMass:
                if edge.toNode.colour == self.__color and edge.toNode.isActive:
                    if node.sendEdge == NotImplemented or edge.toNode.wayToPlayer < node.sendEdge.toNode.wayToPlayer:
                        node.sendEdge = edge
        elif findPassiveNode:
            for edge in node.edgeMass:
                if edge.toNode.colour == self.__color and edge.toNode.isActive:
                    if node.sendEdge == NotImplemented or edge.toNode.wayToPassiveNode < node.sendEdge.toNode.wayToPassiveNode:
                        node.sendEdge = edge

    def attackProtocol(self, node):
        node.sendEdge = NotImplemented
        for edge in node.edgeMass:
            if (not edge.toNode.isActive) or (edge.toNode.colour != node.colour):
                if node.sendEdge == NotImplemented:
                    node.sendEdge = edge
                else:
                    playerSoldierOnEdge = None
                    if edge.toNode.isActive:
                        playerSoldierOnEdge = edge.toNode.realSoldierAmount
                    elif edge.toNode.colour == self.__color:
                        playerSoldierOnEdge = edge.toNode.soldierToActive - edge.toNode.realSoldierAmount
                    else:
                        playerSoldierOnEdge = edge.toNode.soldierToActive + edge.toNode.realSoldierAmount
                    playerSoldierOnSendEdge = None
                    if node.sendEdge.toNode.isActive:
                        playerSoldierOnSendEdge = node.sendEdge.toNode.realSoldierAmount
                    elif node.sendEdge.toNode.colour == self.__color:
                        playerSoldierOnSendEdge = node.sendEdge.toNode.soldierToActive - node.sendEdge.toNode.realSoldierAmount
                    else:
                        playerSoldierOnSendEdge = node.sendEdge.toNode.soldierToActive + node.sendEdge.toNode.realSoldierAmount

                    if playerSoldierOnSendEdge <= 0:
                        node.sendEdge = edge
                    elif playerSoldierOnEdge > 0 and playerSoldierOnEdge < playerSoldierOnSendEdge:
                        node.sendEdge = edge

    def defanceProtocol(self, node):
        danger = 0
        for edge in node.edgeMass:
            if edge.toNode.colour != self.__color and edge.toNode.isActive:
                danger = edge.toNode.soldierAmount
        if node.realSoldierAmount < danger / 4:
            node.sendEdge = NotImplemented