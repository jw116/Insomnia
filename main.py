#name: Jingjie Wang
#andrewID: jingjiew
############################################################
############################################################

from cmu_graphics import *
import random
import math
from PIL import Image
import os, pathlib
import sys

# PIL image import path is weird so we always use absolute path
def openImage(fileName):
    return Image.open(os.path.join(pathlib.Path(__file__).parent,fileName))

############################################################
# Start Screen
############################################################

def start_redrawAll(app):
    drawImage(app.insomnia, 0, 0)
    drawGlowingText(app, '- click to proceed -',
                app.width//2, app.height//11*10, 44)
    if app.goToSleep:
        drawRect(0, 0, app.width, app.height, fill='black',
                 opacity=min(100,app.eyeOpacity))
        if app.eyeOpacity > 100:
            drawImage(app.bedroom, 0, 0)
            drawGlowingText(app, "- press [space] to sleep -",
                        app.width//2, app.height//11*10, 36)
            drawEye(app)
            
def start_onMousePress(app, mouseX, mouseY):
    if 0 < mouseX < app.width and 0 < mouseY < app.height\
       and app.goToSleep == False:
        app.goToSleep = True
        app.eyeTransition = 'closing'
  
def start_onKeyPress(app, key):
    if key == 'space':
        setActiveScreen('game')
        app.eyeOpacity = 0
        app.eyeTransition = 'closing'

def start_onStep(app):
    eyeTransition(app)
    app.glowing = 36 + int(24 * math.sin(app.glowingStepCount * 0.1))
    app.glowingStepCount += 1


############################################################
# onAppStart
############################################################

def onAppStart(app):
    
    app.height = app.width // 16 * 9
    app.stepsPerSecond = 24
    
    app.insomnia = CMUImage(openImage('./insomnia.png'))
    app.bedroom = CMUImage(openImage('./bedroom.png'))
    app.dream = CMUImage(openImage('./dream.jpg'))
    app.making = CMUImage(openImage('./making.png'))
    app.prop_temp = CMUImage(openImage('./prop_temp.png'))
    
    app.L0 = CMUImage(openImage('./0L.png'))
    app.R0 = CMUImage(openImage('./0R.png'))
    app.leftImages = app.L0
    app.rightImages = app.R0
        
    app.eye = CMUImage(openImage('./eye.png'))
    app.eyeHeight = app.height
    app.eyeOpacity = 0
    app.eyeTransition = ''

    app.glowingStepCount = 0
    app.glowing = 9
    
    app.goToSleep = False
    app.guidingTexts = ["What is this?",
                        "A paper crane...?",
                        "It's so... familiar.",
                        "I need to catch it.",
                        "Oh no, it seems that I cannot catch it in my dream.",
                        "- press [space] to open your eyes -",
                        "",
                        ""]
    app.curText = 0
    app.guiding = True
    
    app.cheating = False
    
    app.birdSound = Sound("ES_Bird.mp3")

    app.play = Play(app)
    app.play.setup(app)


############################################################
# Bird
############################################################
        
class Bird:
    def __init__(self, app, x, y, dx, dy, trajectory, size,
                 leftImages, rightImages, isFirstBird):
        self.x = x
        self.y = y
        self.baseX = random.choice([app.width//4, app.width//2, app.width//4*3])
        self.baseY = y
        self.dx = dx
        self.dy = dy
        self.trajectory = trajectory
        self.size = size
        self.angle = random.randint(0, 2) * math.pi
        self.frequency = random.randint(8, 12) * 0.01
        self.amplitude = self.dy * random.randint(22, 25)
        self.isCaught = False
        self.leftImages = leftImages
        self.rightImages = rightImages
        self.curImg = 0
        
        self.stepsPerFrame = 5
        self.stepCounter = 0
        
        self.flyDelay = 0 if isFirstBird else random.randint(30, 90)
        self.radius = 20
        self.linearEntry = True
        
        self.sound = Sound("ES_Bird.mp3")
        
    def distance(self, other):
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5
    
    def fly(self, width, height):
        if self.linearEntry:
            if self.x < 0:
                self.x += abs(self.dx)
            elif self.x > width:
                self.x -= abs(self.dx)
            self.y += self.dy
            if self.size <= self.x <= width-self.size:
                self.linearEntry = False
                    
        if self.trajectory == 'linear':
            self.x += self.dx
            self.y += self.dy
        
        elif self.trajectory == 'sine':
            if self.flyDelay > 0:
                self.flyDelay -= 1
                return
            self.x += self.dx
            self.angle += self.frequency
            self.y = self.baseY + math.sin(self.angle) * self.amplitude
        
        elif self.trajectory == 'spiral':          
            self.angle += 0.05 * random.randint(1, 5)
            self.radius *= 0.98
            self.x = self.baseX + math.cos(self.angle) * self.radius * 15
            self.y = self.baseY + math.sin(self.angle) * self.radius * 5
            if self.radius < 20:
                self.radius = 20
        
        ##to remain within boundaries    
        if self.x <= 0 + self.size and self.dx < 0 \
           or self.x >= width - self.size and self.dx > 0:
            self.dx = -self.dx
            #handling spiral movement
            self.angle += math.pi
        
        #handling sine movement
        if self.baseY <= self.size:
            self.baseY = self.size
        elif self.baseY >= height - self.size:
            self.baseY = height - self.size
        
        if self.y <= 0 + self.size and self.dy < 0 \
           or self.y >= height - self.size and self.dy > 0:
            self.dy = -self.dy
            self.angle += math.pi
        
        #handle direction
        self.stepCounter += 1
        if self.stepCounter % self.stepsPerFrame == 0:
             self.curImg = (self.curImg +1) % 2
                
    def draw(self):
        if not self.isCaught:
            if self.dx > 0:
                img = self.rightImages
            else:
                img = self.leftImages
            drawImage(img, self.x, self.y, align='center')

        #for the sake of testing
        #else:
        #    drawCircle(self.x, self.y, self.size, fill='gray')
    
    def catch(self, x, y):
        return ((self.x - x) ** 2 + (self.y - y) ** 2) ** 0.5 \
               <= self.size
                
    def sing(self):
        self.sound.play()
        if self.isCaught:
            self.sound.pause()


############################################################
# Level
############################################################   
class Level: 
    def __init__(self, numBirds, trajectory, speed, size, leftImages, rightImages):
        self.numBirds = numBirds
        self.trajectory = trajectory
        self.speed = speed
        self.size = size
        self.birds = []
        
    def setup(self, app):
        self.birds = []
        positions = []
        for i in range(self.numBirds):
            while True:
                x = random.choice([-self.size, app.width+self.size])
                y = random.randint(100, app.height-100)
                dx = random.choice([-self.speed, self.speed])
                dy = random.choice([-self.speed, self.speed])
           
                overlap = False
                for (px, py) in positions:
                    distance = ((x-px)**2 + (y-py)**2 ) ** 0.5
                    if distance < self.size * 2:
                        overlap = True
                        break
                    
                if not overlap:
                    isFirstBird = (i == 0)
                    self.birds.append(Bird(app, x, y, dx, dy,
                                           self.trajectory, self.size,
                                           app.leftImages, app.rightImages,
                                           isFirstBird))
                    positions.append((x, y))
                    break
    
    def get0Bird(self):
        if self.birds:
            return self.birds[0].x, self.birds[0].y
        return None, None
    
    def update(self, app):
        for bird in self.birds:
            bird.fly(app.width, app.height)
            bird.sing()
        
    def draw(self):
        for bird in sorted(self.birds, key=lambda bird: bird.y):
            bird.draw()                


############################################################
# Play
############################################################   
class Play: 
    def __init__(self, app):
        self.levels = [Level(1, "linear", 5, 77, app.leftImages, app.rightImages),
                       Level(4, "spiral", 6, 77, app.leftImages, app.rightImages),
                       Level(3, "linear", 5.2, 77, app.leftImages, app.rightImages), 
                       Level(5, "sine", 4.9, 77, app.leftImages, app.rightImages)]
        self.cur = 0
        self.curLevel = self.levels[self.cur]
        self.isDreaming = True
        self.caughtBirds = 0
        
    def setup(self, app):
        self.curLevel.setup(app)
        
    def switchState(self, app):
        if app.play.isDreaming:
            app.eyeTransition = 'opening'
            app.eyeHeight = app.height//2
            app.eyeOpacity = 100
        else:
            app.eyeTransition = 'closing'
            app.eyeHeight = app.height
            app.eyeOpacity = 0            
        self.isDreaming = not self.isDreaming

    def catchBird(self, x, y):
        self.curLevel.birds.sort(key=lambda bird: bird.y, reverse=True)
        for bird in self.curLevel.birds:
            if bird.catch(x, y) and not bird.isCaught:
                bird.isCaught = True
                self.caughtBirds += 1
                break
                    
    def update(self, app):
        self.curLevel.update(app)
        self.completion(app)
            
    def draw(self, app):
        if self.isDreaming:
            drawImage(app.dream, 0, 0)
            if app.eyeTransition == '':
                self.curLevel.draw()
        else:
            drawImage(app.bedroom,0,0)
            if app.cheating == True:
                self.curLevel.draw()            
    
    def completion(self, app):
        if self.caughtBirds >= self.curLevel.numBirds:
            self.caughtBirds = 0
            self.cur += 1
            if self.cur < len(self.levels):
                self.curLevel = self.levels[self.cur]
                self.isDreaming = True
                self.setup(app)
                setActiveScreen('levelUp')
            else:
                setActiveScreen('propUnlocking')

############################################################
# Game Screen (sleep + awake)
############################################################

def game_onKeyPress(app, key):
    if app.play.cur == 0:
        level0_onKeyPress(app, key)
    else:
        if key == 'space':
            app.play.switchState(app)
        elif key == 'c':
            app.cheating = not app.cheating

def game_onMousePress(app, mouseX, mouseY):
    if app.play.cur == 0:
        level0_onMousePress(app, mouseX, mouseY)
        if not app.play.isDreaming and \
           app.curText >= len(app.guidingTexts) - 2:
            app.play.catchBird( mouseX, mouseY)            
    elif not app.play.isDreaming:
        app.play.catchBird(mouseX, mouseY)
                
def game_onStep(app):
    eyeTransition(app)
    app.play.update(app)
    
    app.glowing = 32 + int(18 * math.sin(app.glowingStepCount * 0.1))
    app.glowingStepCount += 1

def game_redrawAll(app):
    if app.play.cur == 0:
        level0_redrawAll(app)
    else:
        app.play.draw(app)
        drawEye(app)


############################################################
# Level 0 Guidance
############################################################

def level0_onMousePress(app, mouseX, mouseY):
    if app.curText < len(app.guidingTexts) - 1:
        app.curText += 1
    else:
        app.guiding = False
        
def level0_onKeyPress(app, key):
    if key == 'space':
        app.play.switchState(app)
        if app.curText < len(app.guidingTexts) - 2:
            app.curText += 1
        
def level0_redrawAll(app):
    app.play.draw(app)
    
    if app.guiding and app.eyeTransition == '':
        drawLabel(app.guidingTexts[app.curText],
                  app.width//2, app.height//11*10,
                  size=36, fill='white', font='Comic Sans MS')
        
    if app.curText == 6:
        drawGlowingText(app,
                        "- use [space] key to toggle between states to observe -",
                        app.width//2, app.height//11*10, 36)
    elif app.curText > 6:
        drawGlowingText(app, "- try to catch the bird with your mouse -",
                        app.width//2, app.height//11*10, 36)
    
    if app.curText >= len(app.guidingTexts) - 2 \
       and not app.play.isDreaming \
       and app.eyeTransition == '':
        x, y = app.play.curLevel.get0Bird()
        if x and y:
            drawCircle(x, y, 77, fill=None, opacity=52,
                       border='lemonChiffon', borderWidth=3)
                        
    drawEye(app)


############################################################
# Level Up Screen
############################################################

def levelUp_redrawAll(app):
    drawImage(app.making, 0, 0)
    drawLabel("We used to be folding paper cranes a lot...",
              app.width//2, app.height//8*7,
              font='Comic Sans MS', size=36, fill='white')
    
def levelUp_onMousePress(app, mouseX, mouseY):
    if 0 < mouseX < app.width and 0 < mouseY < app.height:
        setActiveScreen('game')


############################################################
# Prop Unlocking Screen
############################################################
        
def propUnlocking_redrawAll(app):
    drawImage(app.prop_temp, 0, 0)
    drawGlowingText(app, "More to come as development continues...",
                    app.width//2.4, app.height//3, size=52)
    
def propUnlocking_onStep(app):
    app.glowing = 32 + int(18 * math.sin(app.glowingStepCount * 0.1))
    app.glowingStepCount += 1


############################################################

###############################
#Eye Transition helper function
###############################
def eyeTransition(app):
    if app.eyeTransition == 'closing':
        if app.eyeHeight > 42:
            app.eyeHeight -= 42
            app.eyeOpacity += 4
        else:
            app.eyeHeight = 1
            app.eyeOpacity = 255
            app.eyeTransition = ''
            
    elif app.eyeTransition == 'opening':
        if app.eyeHeight < app.height - 42:
            app.eyeHeight += 42
            app.eyeOpacity -= 4
        else:
            app.eyeHeight = app.height
            app.eyeOpacity = 0
            app.eyeTransition = ''
            
def drawEye(app):
    dark = rgb(26, 26, 26)
    if app.eyeTransition != '':
        drawImage(app.eye, -100, (app.height-app.eyeHeight)//2,
                  width=app.width+200, height=app.eyeHeight)
        
        rectHeight = max(1, (app.height - app.eyeHeight) // 2)

        drawRect(0, 0, app.width, rectHeight,
                 fill=dark)
        drawRect(0, app.height, app.width, rectHeight,
                 fill=dark, align='left-bottom')

        drawRect(0, 0, app.width, app.height,
                 fill='black', opacity=app.eyeOpacity)


###############################
#Text Glowing helper function
###############################
def drawGlowingText(app, text, x, y, size):
    
    offsets = [(1.8, 0), (-1.8, 0), (0, 1.8), (0, -1.8)]
    
    for dx, dy in offsets:
        drawLabel(text, x+dx, y+dy, fill='white', opacity=app.glowing,
                  size=size, font='Comic Sans MS')
    
    drawLabel(text, x, y, fill='lemonChiffon', opacity=app.glowing+33,
              size=size, font='Comic Sans MS')

#
def onJoyPress(app, button, joystick):
    if button == '5':
        sys.exit(0)

############################################################
# Main
############################################################
def main():
    runAppWithScreens(initialScreen='start', width=1456)
    
main()