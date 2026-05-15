#! /usr/bin/python
#-*- coding: utf-8 -*-

from robot import Robot # Importa a classe base Robot

class RoboESEGInicial(Robot): # Cria um Robot
    
    def init(self): # NECESSÁRIO PARA O JOGO Inicializa o robô
        # Altera a cor do tanque
        self.setColor(0, 200, 100)
        self.setGunColor(200, 200, 0)
        self.setRadarColor(255, 60, 0)
        self.setBulletsColor(0, 200, 100)

        # Pega o tamanho do Mapa
        #size = self.getMapSize()  # NÃO RETIRE ESSA LINHA DE CÓDIGO
        
    def run(self): # NECESSÁRIO PARA O JOGO 
        """ Loop principal para comandar o robô """
      
      
    def sensors(self): # NECESSÁRIO PARA O JOGO
        """Tick a cada quadro para obter dados sobre o jogo"""

        
    def onHitByRobot(self, robotId, robotName):  # NECESSÁRIO PARA O JOGO
        """Quando sou atingido por outro robô"""


    def onHitWall(self):  # NECESSÁRIO PARA O JOGO
        """Quando meu robô colide com uma parede"""


    def onRobotHit(self, robotId, robotName): # NECESSÁRIO PARA O JOGO
        """Quando meu robô colide com outro"""

       
    def onHitByBullet(self, bulletBotId, bulletBotName, bulletPower): # NECESSÁRIO PARA O JOGO
        """Quando sou atingido por uma bala"""


    def onBulletHit(self, botId, bulletId): # NECESSÁRIO PARA O JOGO
        """Quando minha bala acerta um robô"""
        

        
    def onBulletMiss(self, bulletId): # NECESSÁRIO PARA O JOGO
        """Quando minha bala acerta uma parede"""
         # Pausa o robô por 10 quadros
        

        
    def onRobotDeath(self): # NECESSÁRIO PARA O JOGO
        """Quando meu robô morre"""
    
    def onTargetSpotted(self, botId, botName, botPos): # NECESSÁRIO PARA O JOGO
        "Quando o robô vê outro"
        


