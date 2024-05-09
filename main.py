import pygame as pg
import classes

pg.init()

pg.time.set_timer(pg.USEREVENT + 1, 10)

boxColor = [125, 125, 125]

window = pg.display.set_mode() # should be fullscreen

classes.setGround(window)

running = True

box = classes.Box(400, 200)

selectedBox = None

# box.forceObjects.append(classes.Thrusters(50 * classes.gravity, 0))
box.forceObjects.append(classes.Thrusters(100, 270))

# this button allows the user to switch between free body diagram and energies
switchBtn = pg.rect.Rect(window.get_width() - 210, 10, 200, 100)

paused = False

userMag = 1000

while (running == True):

    mousePos = pg.mouse.get_pos()

    # fills the screen with a light blue that represents the sky
    window.fill([135, 206, 235])

    for platform in classes.platforms:
        pg.draw.polygon(window, [0, 255, 0], platform.points)

    for box in classes.boxes:
        # draw the boxes arrows first, so they are under the box
        if (classes.showEnergies == True):
            pg.draw.polygon(window, boxColor, box.points)
            
            box.drawEnergies(window)
        else:
            pg.draw.polygon(window, boxColor, box.points)
            
            box.drawForces(window)


    # green for free body, yellow for energies
    insideSwitchColor = pg.Color(0, 200, 0)
    borderSwitchColor = pg.Color(100, 255, 100)

    if (classes.showEnergies):
        insideSwitchColor = pg.Color(200, 200, 0)
        borderSwitchColor = pg.Color(255, 255, 100)

    # place the button at the end in order to put it on top
    pg.draw.rect(window, borderSwitchColor, switchBtn, 0, 10)
    pg.draw.rect(window, insideSwitchColor, switchBtn, 10, 10)

    if (paused == True):
        # show a paused symbol in the top left

        pg.draw.rect(window, pg.Color(255, 255, 255), [10, 10, 20, 100])
        pg.draw.rect(window, pg.Color(255, 255, 255), [50, 10, 20, 100])

    keys = pg.key.get_pressed()

    if selectedBox != None:
        if  keys[pg.K_LEFT]:
            selectedBox.addForce(classes.Force(userMag, "i", 270))

        elif keys[pg.K_DOWN]:
            selectedBox.addForce(classes.Force(userMag, "i", 0))

        elif keys[pg.K_UP]:
            selectedBox.addForce(classes.Force(userMag, "i", 180))

        elif keys[pg.K_RIGHT]:
            selectedBox.addForce(classes.Force(userMag, "i", 90))

    for evt in pg.event.get():
        if (evt.type == pg.USEREVENT + 1 and paused == False): # every millisecond
            for box in classes.boxes:
                box.move()

        if (evt.type == pg.KEYDOWN):
            if (evt.key == pg.K_ESCAPE):
                running = False

            elif evt.key == pg.K_SPACE:
                classes.Box(mousePos[0] - (classes.boxSize / 2), mousePos[1] - (classes.boxSize / 2))

            elif evt.key == pg.K_p:
                paused = not paused

            elif evt.key == pg.K_r:
                classes.boxes.clear()


        if (evt.type == pg.MOUSEBUTTONUP):
            if (switchBtn.collidepoint(mousePos)):
                classes.showEnergies = not classes.showEnergies

            else:
                for b in classes.boxes:
                    if (b.rect.collidepoint(mousePos)):
                        selectedBox = b
                        break

        if (evt.type == pg.QUIT):
            running = False

    pg.display.flip() # writes things to the screen

pg.quit()
