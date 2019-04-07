
# GravitySimulator-Computer-Graphics-

The Gravity Simulator Engine is used to model n-body 3-dimensiaonal gravitatinal interactions. 
The engine allows the user to choose the number of objects, their initial positions, velocities, mass and radius.
By carefully modelling the system, almost any case can be simulated on the engine.
The engine demonstrates the gravitaional interactions between the bodies and their resulting trajectories.

To install the requirements - 

####              pip3 install -r requirements.txt
              
To execute -

###             python3 -m nbody 

After executing the above command a window appears which represents the initial positions of the particles where the observer is at the X-axis.

The model can be zoomed in or out by scrolling
The position of the observer can be changed by click-and-drag operation on the window. The projection is such that the origin is always at the centre of the window.

The input is given to the engine by the input file input.txt

The format is as follows: 

1st line: Number_of_particles(N)

Next N lines: Initial position of N particles as a 3-d coordinate Xi,Yi,Zi (eg- 0 15 21) 

Next N lines: Initial velocity of N particles as a 3-d vectors Vx,Vy,Vz (eg- 0 15 21)

Next N lines: Mass of N particles

Next N lines: Radius of N particles


Sample input:
      3

      0 0 0
      
      20 0 0
      
      -20 0 0
      
      0 0 0
      
      0 8 0
      
      0 -8 0
      
      10
      
      10
      
      10
      
      5
      
      5
      
      5
      
The correspondind model for this input: 

![example](https://github.com/namansinghal98/GravitySimulator-Computer-Graphics-/blob/master/Screenshot%20from%202019-04-07%2022-47-36.png)
