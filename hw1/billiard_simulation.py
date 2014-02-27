#!/usr/bin/python

import math
import time

# Code related to GUI
from Tkinter import *

root = Tk()
root.title("Billiards")
root.resizable(0, 0)

frame = Frame(root, bd=5, relief=SUNKEN)
frame.pack()

# Define constants
ball_radius = 5 # In cm
ball_slowdown_constant = 0.1 # Ball loses 10% of its velocity per second
cutoff_velocity = 0.1 # If velocity falls below this, it is set to 0 
simulation_step = 0.0001 # In seconds. Max velocity of 1000 cm/s means the ball will move a max of 0.1cm per simulation step

# GUI related parameters
gui_scale = 2
draw_rate = 500

# Define our ball class, to store our x and y positions, and velocities
class Ball:
    def __init__(self,x_position, y_position, x_velocity, y_velocity):
        self.x = x_position
        self.y = y_position
        self.x_velocity = x_velocity
        self.y_velocity = y_velocity

# Checks position of all balls, computes new velocities if there is a collision
# Width = width of table, length = length of table, ball_list is a list of all balls
def collision_detect(width, length, ball_list):	
    # Detect collision with balls
    collision = False
    for i in range(0,len(ball_list)):
        for j in range(i+1,len(ball_list)):
            # Compute x and y distance between balls 
            x_distance = ball_list[j].x - ball_list[i].x
            y_distance = ball_list[j].y - ball_list[i].y
            # Compute total distance
            distance = math.sqrt(x_distance * x_distance + y_distance * y_distance)

            # First, simulate what happens if we do nothing
            # Compute the new distance (experimental_distance) between the two balls on the next simulation step
            # If this value (experimental_distance) is less than the current distance AND the balls are
            # currently overlapping, we know that the collision was supposed to occur.
            experiment_x_distance = (ball_list[j].x + ball_list[j].x_velocity * simulation_step) - (ball_list[i].x + ball_list[i].x_velocity * simulation_step)
            experiment_y_distance = (ball_list[j].y + ball_list[j].y_velocity * simulation_step) - (ball_list[i].y + ball_list[i].y_velocity * simulation_step)
            experiment_distance =  math.sqrt(experiment_x_distance ** 2 + experiment_y_distance ** 2)

            if (distance < 2 * ball_radius and (experiment_distance < distance)):
                # Collision detected
                normal_v = [x_distance / distance, y_distance / distance]
                tangent_v = [-1 * normal_v[1], normal_v[0]]

                # Project x and y vectors onto normal and tangent (first ball)
                dot_product_n = normal_v[0] * ball_list[i].x_velocity + normal_v[1] * ball_list[i].y_velocity
                first_normal_v = [dot_product_n * normal_v[0] , dot_product_n * normal_v[1]]
                dot_product_t = tangent_v[0] * ball_list[i].x_velocity + tangent_v[1] * ball_list[i].y_velocity
                first_tangent_v = [dot_product_t * tangent_v[0] , dot_product_t * tangent_v[1]]

                # Project x and y vectors onto normal and tangent (second ball)
                dot_product_n = normal_v[0] * ball_list[j].x_velocity + normal_v[1] * ball_list[j].y_velocity
                second_normal_v = [dot_product_n * normal_v[0] , dot_product_n * normal_v[1]]
                dot_product_t = tangent_v[0] * ball_list[j].x_velocity + tangent_v[1] * ball_list[j].y_velocity
                second_tangent_v = [dot_product_t * tangent_v[0] , dot_product_t * tangent_v[1]]

                # Swap the normal vectors
                temp = first_normal_v
                first_normal_v = second_normal_v
                second_normal_v = temp

                # Combine back to x and y
                ball_list[i].x_velocity = first_normal_v[0] + first_tangent_v[0]
                ball_list[i].y_velocity = first_normal_v[1] + first_tangent_v[1]
                ball_list[j].x_velocity = second_normal_v[0] + second_tangent_v[0]
                ball_list[j].y_velocity = second_normal_v[1] + second_tangent_v[1]

    # Detect collision with walls
    # We first check if the ball is overlapping with the wall
    # We then check if the ball is moving towards the wall
    # If both conditions are right, we need to reflect the ball
    for ball in ball_list:
        # Left or Right wall collision, reverse X velocity
        if (((ball.x - ball_radius) < 0 and ball.x_velocity < 0) or ((ball.x + ball_radius)  > length and ball.x_velocity > 0)):
            ball.x_velocity = -1 * ball.x_velocity
        # Up or Down wal collision, reverse Y velocity
        if (((ball.y - ball_radius) < 0 and ball.y_velocity < 0) or ((ball.y + ball_radius)  > width and ball.y_velocity > 0)):
            ball.y_velocity = -1 * ball.y_velocity
    return ball_list

# Update x and y coords of all balls based on velocities
def update_vectors(ball_list):
    for ball in ball_list:
        # New position = Position + Velocity * Time. Compute for both X and Y
        ball.x = ball.x + ball.x_velocity * simulation_step
        ball.y = ball.y + ball.y_velocity * simulation_step

        # Based on v_new = v_old + constant_factor*acceleration*time
        # New velocity = Velocity - Velocity * ball_slowdown_constant * simulation_step
        # If velocity is less than cutoff_velocity, set it to 0
        velocity_magnitude = math.sqrt(ball.x_velocity ** 2 + ball.y_velocity ** 2)
        #print "%f %f %f" % (velocity_magnitude, ball.x_velocity, ball.y_velocity)
        if (velocity_magnitude < cutoff_velocity):
            ball.x_velocity = 0
            ball.y_velocity = 0
        else:
            ball.x_velocity = ball.x_velocity - ball_slowdown_constant * ball.x_velocity * simulation_step
            ball.y_velocity = ball.y_velocity - ball_slowdown_constant * ball.y_velocity * simulation_step

    return ball_list

# Check if the balls are moving. This is how we detect when the simulation is complete
def detect_movement(ball_list):
    for ball in ball_list:
        # If the ball has non-zero x or y velocity, we detect movement
        if (abs(ball.x_velocity) > 0 or abs(ball.y_velocity) > 0):
            return True
    return False

# This function draws the balls in a GUI
def update_gui(width, length, ball_list):
    canvas.create_rectangle(0, 0, gui_scale*length, gui_scale*width, fill="white")
    for ball in ball_list:
        canvas.create_oval(gui_scale*(ball.x - ball_radius), gui_scale*(ball.y - ball_radius), gui_scale*(ball.x + ball_radius), gui_scale*(ball.y + ball_radius), fill="blue")
    root.update_idletasks() # redraw
    root.update() # process events 

# This is the main simulation loop. It runs until all balls stop
def simulate(width, length, ball_list):
    x = 0
    while (detect_movement(ball_list)):
        collision_detect(width, length, ball_list) # Update velocities on collision 
        update_vectors(ball_list) # Compute new positions and velocities
        # Draw the data to the GUI. Limited the amount of draws to speed up program execution
        if (x >= draw_rate):
            update_gui(width, length, ball_list)
            x = 0
        x = x +1
        # End GUI code
    return ball_list

def main:
    
    ball_list = []
    
    # Read and process input, flag bad input and exit
    try:
        file_name = sys.argv[1]
        input_file = open("test_inputs/"+file_name, "r")
        length = int(input_file.readline()) # First line
        width = int(input_file.readline()) # Second line
    
        num_balls = int(input_file.readline()) # Third line
        assert(length > 0 and width > 0), "Length and width must be greater than 0"
        assert(num_balls >= 0), "Number of balls must be positive"
        line = 3
    
    # Next num_balls lines will have 4 integers separated by commas. Make a ball object for each, and store in ball_list
    # FORMAT: x position, y position, x velocity, y velocity
        for b in xrange(0,num_balls):
            line = line + 1
            line_array = input_file.readline().split(",")
            line_array = map(float, line_array)
            assert (len(line_array) == 4), "Line %d: Each ball must have exactly 4 values, separated by commas" % line
            ball = Ball(line_array[0], line_array[1], line_array[2], line_array[3])
            assert (ball.x - ball_radius >= 0 and ball.x + ball_radius <= length), "Line %d: Ball must be on the table" % line
            assert (ball.y - ball_radius >= 0 and ball.y + ball_radius <= width), "Line %d: Ball must be on the table" % line
            ball_list.append(ball)
        input_file.close()
    except ValueError:
        print "Error: Bad input file: Non-numerical value specified"
        sys.exit(-1)
    except IOError as e:
        print "I/O error: Input file does not exist in test_inputs"
        sys.exit(-1)
    except AssertionError, e:
        print "Error: {0}".format( e.args[0] )
        sys.exit(-1)
    except:
        print "Error: Bad input file"
        sys.exit(-1)
    
    # Code Related To GUI
    canvas = Canvas(frame, width=gui_scale*length, height=gui_scale*width, bd=0, highlightthickness=0)
    canvas.pack()
    root.update() 
    
    # Begin the simulation
    ball_list = simulate(width, length, ball_list)
    
    # Simulation is done, write out the output file in same format as input file
    try:
        output_file = open("test_outputs/"+file_name, "w")
        output_file.write(str(length) + "\n" + str(width) + "\n" + str(num_balls) + "\n")
        for ball in ball_list:
            output_file.write(str(ball.x) + "," + str(ball.y) + "," + str(ball.x_velocity) + "," + str(ball.y_velocity) + "\n")
        output_file.close()
    except:
        print "Cannot write output file to test_outputs/{0}".format(file_name)

if __name__ == "__main__":
    main()
