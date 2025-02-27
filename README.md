# Plinko-Balls
[play online](https://jareddilley.itch.io/plinko)

Python: 3.12.0, pygame-ce: 2.5.1, numpy: 2.2.3, matplotlib: 3.10.0
<br><br><b>Or run locally -</b>
<br> - download [plinko_balls.py](plinko_balls.py) and [sounds](sounds)
<br> - install [Python 3.12.0](https://www.python.org/downloads/release/python-3120/)
<br> - install packages (cmd): pip install pygame-ce numpy matplotlib
<br> - run (cmd): python plinko_balls.py

[YouTube Video](https://www.youtube.com/watch?v=E59LsTyOdmo) <br>
This pygame is a recreation of the Stake's Plinko gambling game. I built the game with the Pygame Python module to break down the functionality and mechanics of the game and possibly wrinkle your and fellow gamblers' brains. The gambler drops balls in the hopes that they hit one of the high multipliers for a high return. The house, however, has set it up so that most of the balls go to the middle, and the gambler loses money.
![image](media/full-game.gif)

# Scripts
Main game: [plinko_balls.py](plinko_balls.py)
<br>Physics Demos: [demos](demos/)
<br>Different stages of game: [scripts](scripts/)

# Physics & Mechanics
Dampening in the y-direction does two things. It gives the ball gravity physics and it reduces the randomness of the path of the ball. The more the ball can bounce the more the ball can go where we don't want it to.
<br>![image](media/y-dampening.gif)
<br>In addition, to dampen the ball's bounce due to gravity we can also do an additional dampen on the x-direction to get the ball to go more up than out. With the balls starting in the middle, ideally, we want the balls to go straight down from the house's perspective.
<br>![image](media/x-dampening.gif)
<br>Now that the ball is more predictable we want to add bias in the x direction that the ball is not in the middle. We can do this by adding to the x-component of the ball's vector. We will add a small vector that points toward the middle, this way if the ball lands on the outside of a pin on the outside of the pyramid it will act like it hit the inside of the pin. 
<br>![image](media/x-biasing.gif)
