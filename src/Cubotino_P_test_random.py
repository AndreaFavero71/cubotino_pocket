#!/usr/bin/python
# coding: utf-8

"""
#############################################################################################################
# Andrea Favero 26 January 2024
# 
# Script to virtually solve random generated Rubik's cube 2x2x2 status, by the by CUBOTino_P
#
# The cbe status, categorized by dept, is made as per: https://github.com/ImportMathRepositories/2x2_Depth
# Because there are 3674160 different permutations, these are generated and analysed one at the time.
# Each permutation is sent to the Kociemba solver, that returns the optimal solution.
# The solver might return multiples solutions, having the same quantity of (humans) movements.
# Each solution is sent to the robot solver.
# The robot solver estimates the servos solving time per each solution, and fastest is returned.
# The selected robot solution is applied to a virtual manipulator, that applies the CUBOTino movements.
# The cube status is updated after each virtual cube manipulation (Flip, Spin or Rotate).
# The final cube status, after last manipulation, is verified if it looks like a solved cube
#
#############################################################################################################
"""



################  setting argparser for robot remote usage, and other settings  #################
import argparse

# argument parser object creation
parser = argparse.ArgumentParser(description='Test random cube status via a virtual cube manipulator')


# --debug argument is added to the parser
parser.add_argument("-d", "--debug", action='store_true',
                    help="Activates printout of settings, variables and info for debug purpose")

# --print argument is added to the parser
parser.add_argument("-p", "--print", action='store_true',
                    help="Print to terminals some info related to the simulation")

# --runs argument is added to the parser
parser.add_argument("-r", "--runs", type=int,
                    help="Input the number of random cubes to test")

# --plot argument is added to the parser
parser.add_argument("--plot", action='store_true',
                    help="Enables a graphical animation")

args = parser.parse_args()   # argument parsed assignement
# ###############################################################################################




def imports(plot):
    global np, math, time, rm, servo
    
    import numpy as np
    import math
    import time
    import Cubotino_P_moves as rm    # custom library, traslates the cuber solution string in robot movements string
    import Cubotino_P_servos as servo    # custom library for the servos control
    if plot:
        global cv2
        import cv2


def clear_terminal():
    """ Clears the terminal and positions the cursors on top left; Still possible to scroll up in case of need"""
    print("\x1b[H\x1b[2J")  # escape sequence



def import_solver():
    # importing Kociemba solver
    global sv, cubie
    import os.path, pathlib                               # library to check file presence            
    folder = pathlib.Path().resolve()                     # active folder (should be home/pi/cube)  
    fname = os.path.join(folder,'solver2x2x2','solver.py') # active folder + Solver2x2x2 + solver name
    solver_found = False                                  # boolean to track the import the copied solver in subfolder
    if os.path.exists(fname):                             # case the solver exists in 'Solver2x2x2' subfolder
        import solver2x2x2.solver as sv                   # import Kociemba solver copied in sub-folder
        import solver2x2x2.cubie as cubie                 # import cubie function from Kociemba solver
        return True                                       # boolean to track the  import the copied solver in subfolder
    else:
        return False                                      # boolean to track the import the copied solver in subfolder



def scramble():
    cc = cubie.CubieCube()          # cube in cubie reppresentation
    cc.randomize()                  # randomized cube in cubie reppresentation 
    random_cube_string = str(cc.to_facelet_cube())   # randomized cube in facelets string reppresentation
    return random_cube_string




def cube_facelets_permutation(cube_status, move_type, direction):
    """Function that updates the cube status, according to the move type the robot does
       The 'ref' tuples provide the facelet current reference position to be used on the updated position.
       As example, in case of flip, the resulting facelet 0 is the one currently in position 23 (ref[0]).
       The initial cube orientation is not the one the robos has after the scanning process."""
    
    if move_type == 'flip':      # case the robot move is a cube flip (complete cube rotation around L-R horizontal axis) 
        ref=(23,22,21,20,5,7,4,6,0,1,2,3,8,9,10,11,18,16,19,17,15,14,13,12)
    
    elif move_type == 'spin':    # case the robot move is a spin (complete cube rotation around vertical axis)
        if direction == '1':     # case spin is CW
            ref=(1,3,0,2,8,9,10,11,16,17,18,19,14,12,15,13,20,21,22,23,4,5,6,7)
        elif direction == '3':   # case spin is CCW
            ref=(2,0,3,1,20,21,22,23,4,5,6,7,13,15,12,14,8,9,10,11,16,17,18,19)
    
    elif move_type == 'rotate':  # case the robot move is a rotation (lowest layer rotation versus mid and top ones) 
        if direction == '1':     # case 1st layer rotation is CW
            ref=(0,1,2,3,4,5,10,11,8,9,18,19,14,12,15,13,16,17,22,23,20,21,6,7)
        elif direction == '3':   # case 1st layer rotation is CCW
            ref=(0,1,2,3,4,5,22,23,8,9,6,7,13,15,12,14,16,17,10,11,20,21,18,19)
    
    new_status={}                # empty dict to generate the cube status, updated according to move_type and direction
    for i in range(24):                    # iteration over the 54 facelets
        new_status[i]=cube_status[ref[i]]  # updated cube status takes the facelet from previous status at ref location
    
    return new_status                      # updated cube status is returned





def robot_set_servo(debug):
    """ The robot uses a couple of servos; This functions positions the servos to the start position."""
    
    # servos are initialized, and set to their starting positions
    ret, timer = servo.init_servo(debug, start_pos = 'read', f_to_close_mode=True)
    return ret, timer




def cube_sketch_coordinates(x_start, y_start, edge):
    """ Generates a list and a dict with the top-left coordinates of each facelet, as per the URFDLB order.
    These coordinates are later used to draw a cube sketch
    The cube sketch (overall a single rectangle with all the facelets in it) starts at x_start, y_start
    Each facelet on the sketch has a square side dimention = edge, defined at start_up() function."""
    
    square_start_pt=[]   # lits of all the top-left vertex coordinate for the 24 facelets
    
    # the six cube faces are noted from 0 to 5.
    # the top left corner coordinate is defined as function of x_start, y_start and d (=distance)
    starts={0:(x_start+2*edge, y_start),
            1:(x_start+4*edge, y_start+2*edge),
            2:(x_start+2*edge, y_start+2*edge),
            3:(x_start+2*edge, y_start+4*edge),
            4:(x_start,     y_start+2*edge),
            5:(x_start+6*edge, y_start+2*edge)}      # dict with the top-left coordinate of each face (not facelets !)
    
    for value in starts.values():                          # iteration over the 6 faces
        x_start=value[0]                                   # x coordinate fo the face top left corner
        y_start=value[1]                                   # y coordinate fo the face top left corner
        y = y_start                                        # y coordinate value for the first 3 facelets
        for i in range(2):                                 # iteration over rows
            x = x_start                                    # x coordinate value for the first facelet
            for j in range(2):                             # iteration over columns
                square_start_pt.append([x, y])             # x and y coordinate, as list, for the top left vertex of the facelet is appendended
                x = x+edge                                    # x coordinate is increased by square side
                if j == 1: y = y+edge                         # once at the second column the row is incremented
    
#     facelets_start = {k:tuple(square_start_pt[k]) for k in range(24)}  # dictionary is made with tuples of top-left coordinates
    
    facelets_start={}
    inner_points={}
    d=edge-2                                              # square edge is reduced by 2 pixels 
    for i in range(24):
        coordinate = tuple(square_start_pt[i])
        x = coordinate[0]+1                                 # top left x coordinate is shifted by 1 pixel to the right
        y = coordinate[1]+1                                 # top left y coordinate is shifted by 1 pixel to the bottom
        pts = np.array([(x,y),(x+d,y),(x+d,y+d),(x,y+d)])   # array with tupples of square coordinates, shifted by 1 pixel toward the inside
        facelets_start[i] = coordinate
        inner_points[i] = pts                               # array with the 4 square inner vertex coordinates
    
    return facelets_start, inner_points






def plot_interpreted_colors(wait, cube_status, ref_colors_BGR, startup=False, kill=False):
    """ Based on the detected cube status, a sketch of the cube is plot with bright colors on the pictures collage."""
    
    if startup:
        global assigned_colors, sketch, frame, start_points, inner_points
        
        assigned_colors = {'U':(ref_colors_BGR[0]), 'R':(ref_colors_BGR[1]), 'F':(ref_colors_BGR[2]),
                           'D':(ref_colors_BGR[3]), 'L':(ref_colors_BGR[4]), 'B':(ref_colors_BGR[5])}
        cv2.namedWindow('cube')                            # create the cube window
        cv2.moveWindow('cube', 0,0)                        # move the window to (0,0)
        sketch = np.zeros([350, 450, 3],dtype=np.uint8)    # empty array
        sketch.fill(230)                                   # array is filled with light gray
        
        x_start=20      # top lef corner of the rectangle where all the cube's faces are plot
        y_start=20       # top lef corner of the rectangle where all the cube's faces are plot
        d = 50           # edge lenght for each facelet reppresentation
        facelets_start, inner_points = cube_sketch_coordinates(x_start, y_start, d)  # dict with the top-left coordinates for each of the 54 facelets
        for i in range(24):                                            # iteration over the 24 facelets interpreted colors
            cv2.rectangle(sketch, tuple(facelets_start[i]), (facelets_start[i][0]+d, facelets_start[i][1]+d), (0, 0, 0), 1) # square black frame
        frame = sketch.copy()
        cv2.imshow("cube", sketch)
        cv2.waitKey(100)                     # refresh time

    ######### interpreted cube #################    
    for i, color in enumerate(cube_status):                 # iteration over the 24 facelets interpreted colors
        B,G,R = assigned_colors[color]                               # BGR values of the assigned colors for the corresponding detected color
        cv2.fillPoly(frame, pts = [inner_points[i]], color=(B,G,R))  # inner square is colored with bright color of the interpreted one      
    
    cv2.imshow("cube", frame)
    cv2.waitKey(wait)                         # refresh time
    
    if kill:
        cv2.destroyAllWindows()               # all the windows are closed







def cube_solution(cube_string, printout, informative):

    """ Calls the Hegbert Kociemba solver, and returns the solution's moves
    from: https://github.com/hkociemba/Rubiks2x2x2-OptimalSolver 
    The solver returns the optimal solution.
    More solutions could be returned, having the same quantity of cube movements; In this case
    it is chosen the faster solution for the robot."""
    
    simulation = True
    
    solutions = sv.solve(cube_string)       # solver is called
    solutions = solutions.splitlines()      # solver return is plit by lines
    
    s = solutions[0]                        # the first solution is taken
    solution_Text = s[s.find('(')+1:s.find(')')-1]+' moves  '+ s[:s.find('(')]  # manipulated string, used in Cubotino
    s = s[:s.find('(')]                     # solution capture the sequence of manoeuvres
    if debug or printout:                   # case debug or printout variable is set True 
        print("Solution returned by the solver:", s)  # feedback is printed to the terminal
        
    if s[:5] =='Error':                     # case solution error (incoherent cube string sent to the solver)
        solution_Text = 'Error'             # 'Error' string is assigned to solution_Text variable
    
    if solution_Text != 'Error':            # case the solver does not returns errors
        _, robot_moves, total_robot_moves, opt = rm.robot_required_moves(s, solution_Text, simulation, informative) # string with robot movements, and total movements
        est_time = servo.estimate_time(robot_moves, timer, slow_time=0)  # estimation servos time for the single solution    

    if debug and solution_Text != 'Error':  # case debug variable is set True
        print("Estimated time for the servos:", est_time, "secs")  # feedback is printed to Terminal
    
    return s, solution_Text, robot_moves, total_robot_moves, est_time, opt




def solved_status_check(cube_status):
    """Checks is a cube status string is a solved cube.
        The test is performed on 5 faces, that if ok it also means the 6th face is ok.
        Funtion returns 1 for a solved cube, otherwise 0.
    """
    cube = ((0,1,2,3),(4,5,6,7),(8,9,10,11),(12,13,14,15),(16,17,18,19))
    if len(cube_status) == 24:
        for face in cube:
            for i in range(3):
                if cube_status[face[i+1]] != cube_status[face[0]]:
                    return 0
        return 1



def test_random_permutations(runs, plot, debug, printout):
    """Generates random cube status (permutations) of a 2x2x2 Rubik's cube.
    Each random permutation is analysed from the Cubotino_P_moves, and the faster one is selected.
    Each set of robot movements is virtually applied.
    After each of the (virtual) cube manipulation, the cube status is updated to reflect the new status.
    The last cube status is analyzed if conforming to the solved cube.
    The simulation can be limited to a predefined quantity of tests.
    """
    
    start = time.time()
    test_ok_number=0
    estimated_time=[]
    opt1=0
    opt2=0
    opt3=0
        
    if plot:
        ref_colors_BGR = ([185, 206, 173], [29, 32, 185], [35, 144, 0], [30, 216, 195], [34, 117, 236], [100, 65, 0])

    for test in range(1,runs+1):
        if not debug and not printout:
            print(f"Test: {test:,d} (of {runs:,d})", end='\r', flush=True)
        if printout:
            print(f"Test number: {test+1:,d}")
            
        cube_status = scramble()
        if printout:
            print("Random cube_status generated:", cube_status)
        
        # Kociemba solver is called to have the solution string
        solution, solution_Text, robot_moves, total_robot_moves, est_time, opt = cube_solution(cube_status, printout, informative=informative)
        opt1 += opt[0]
        opt3 += opt[1]
        estimated_time.append(est_time)
        if printout:
            print('Robot_moves returned by the robot solver: ', robot_moves)  # nice information to print at terminal
            print("Estimated solving time:",est_time)
        
        if plot:
            if test == 1:
                startup=True
            show_ms = 300
            plot_interpreted_colors(show_ms, cube_status, ref_colors_BGR, startup=True)

        for i in range(0, len(robot_moves),2):
            show_ms = 15
            move_type = robot_moves[i:i+1]
            if move_type == 'F':
                move_type = 'flip'
            elif move_type == 'R':
                move_type = 'rotate'
            elif move_type == 'S':
                move_type = 'spin'
            direction = robot_moves[i+1:i+2]
            if move_type == 'flip':
                for i in range(int(direction)):
                    new_cube_status = cube_facelets_permutation(cube_status, move_type, direction)
                    cube_status=''
                    for i in range(24):
                        cube_status+=new_cube_status[i]
                    if plot:
                        plot_interpreted_colors(show_ms,cube_status,ref_colors_BGR)

            else:
                new_cube_status = cube_facelets_permutation(cube_status, move_type, direction)
                cube_status=''
                for i in range(24):
                    cube_status+=new_cube_status[i]
                if plot:
                    plot_interpreted_colors(show_ms,cube_status,ref_colors_BGR)
        
        if plot:
            show_ms = 300
            if test != runs:
                plot_interpreted_colors(show_ms,cube_status,ref_colors_BGR)
            else:
                plot_interpreted_colors(show_ms, cube_status, ref_colors_BGR, kill=True)
        
        
        # test if the cube status reppresents a solved cube
        test_ok = solved_status_check(cube_status)   # test_ok_counter is incremented by 1
        test_ok_number += test_ok
        
        if printout:
            if test_ok:
                print("Virtual robot solver has solved the cube: OK")
            else:
                print("Virtual robot solver did not solve the cube: Test NOT OK")
            print(row)

    print('\n\n')
    estimated_time = np.array(estimated_time)
    avg_servo_time = round(np.mean(estimated_time),1)
    std_servo_time = round(np.std(estimated_time),3)
    min_servo_time = round(np.min(estimated_time),1)
    max_servo_time = round(np.max(estimated_time),1)
    
    tot_time = time.time()-start


    print(f"Tested {runs} random cube's status with {runs-test_ok_number} failures")
    if plot:
        print(f"The test took {round(tot_time,1)} seconds, being slowed down by the graphical animation")
        print(f"(average of {round(tot_time/test,2)} secs per each cube status)")
    else:
        print(f"The test took {round(time.time()-start,2)} seconds")
        print(f"(average of {round(1000*tot_time/test,2)} millisecs per each cube status)")
    print()
    print("Average estimated solving time (servos):", avg_servo_time)
    print("std on estimated solving time (servos):", std_servo_time)
    print("Min estimated solving time (servos):", min_servo_time)
    print("Max estimated solving time (servos):", max_servo_time)
    print()
    print()
    print("opt1:", opt1)
    print("opt3:", opt3)
    print()
    print()

    fname = 'test.txt'
    np.savetxt(fname, estimated_time, fmt='%10.2f')
    print(f"saved the estimated servo time, for the simulated {runs} runs, to the file {fname}")
    print()
    print()
    
    
    
    
    

############################################### test ###############################################
if __name__ == "__main__":
    
    row = "#"*80                     # string of characters used as separator

    debug = False                    # flag to enable/disable the debug related prints
    if args.debug != None:           # case 'debug' argument exists
        if args.debug:               # case the script has been launched with 'debug' argument
            debug = True             # flag to enable/disable the debug related prints is set True

    printout = False                 # flag to enable/disable the prints related to the simulation prints
    if args.print != None:           # case 'debug' argument exists
        if args.print:               # case the script has been launched with 'printout' argument
            printout = True          # flag to enable/disable the simulation related prints is set True
    
    plot = False                     # flag to enable/disable the graphical animation
    if args.plot != None:            # case 'plot' argument exists
        if args.plot:                # case the script has been launched with 'plot' argument
            plot = True              # flag to enable/disable the graphical animation
    
    runs = 100                       # arbitrary amount of simulation runs, when not overwritten by the argument
    if args.runs != None:            # case 'runs' argument exists
        runs = args.runs             # case the script has been launched with 'runs' argument

    if printout:
        informative = True
    else:
        informative = False
    
    
    clear_terminal()        # cleares the terminal
    imports(plot)           # imports the needed libraries

    # cube solver to get the solution per each permutation
    ret = import_solver()
    print("Solver imported:", ret)

    # servos init to get the servos timers, necessary for searching the fastest robot solution
    robot_init_status, timer = robot_set_servo(debug)               
    print("Timers returned by the robot:", robot_init_status)
    
    
    if args.runs == None:            # case 'runs' argument was not provided
        print('\n',row)              # a row separation is printed to the terminal
        print(row)                   # a row separation is printed to the terminal
        print(f"Not provided --runs argument: Test will stop after {runs} random cube status")
        print(row)                   # a row separation is printed to the terminal
        print(row,'\n')              # a row separation is printed to the terminal
    else:                            # case 'runs' argument was provided
        print(row,'\n')              # a row separation is printed to the terminal
    
    test_random_permutations(runs, plot, debug, printout)

