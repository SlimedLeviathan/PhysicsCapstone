import pygame as pg
import classes

pg.init()

pg.time.set_timer(pg.USEREVENT + 1, 1)

boxColor = [125, 125, 125]

window = pg.display.set_mode() # should be fullscreen

running = True

box = classes.Box(100, 200)

# box.forceObjects.append(classes.Thrusters(60 * classes.gravity, 135))

classes.Platform(0, 600, 900, 100)

while (running == True):

    # fills the screen with a light blue that represents the sky
    window.fill([135, 206, 235])

    for platform in classes.platforms:
        pg.draw.polygon(window, [0, 255, 0], platform.points)

    for box in classes.boxes:
        # draw the boxes arrows first, so they are under the box
        box.drawForces(window)

        # then draw the box
        pg.draw.polygon(window, boxColor, box.points)

    for evt in pg.event.get():
        if (evt.type == pg.USEREVENT + 1): # every millisecond
            for box in classes.boxes:
                box.move()

        if (evt.type == pg.KEYDOWN):
            if (evt.key == pg.K_ESCAPE):
                running = False

            if evt.key == pg.K_SPACE:
                classes.Box(100, 200)

        if (evt.type == pg.QUIT):
            running = False

    pg.display.flip() # writes things to the screen

pg.quit()
