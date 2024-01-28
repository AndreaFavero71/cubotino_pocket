#!/usr/bin/python
# coding: utf-8

"""
#############################################################################################################
# Andrea Favero 26 January 2024
# 
# Script to virtually test all the possible 2x2x2 Rubik's cube status in CUBOTino_P
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

#####################  setting argparser ###################################################
import argparse

# argument parser object creation
parser = argparse.ArgumentParser(description='Test all the cube status via a virtual cube manipulator')

# --stop argument is added to the parser
parser.add_argument("-s", "--stop", type=int,
                    help="Input max number of permutation to test")

args = parser.parse_args()   # argument parsed assignement
# ##########################################################################################




############################################################################################
#####################   part to generate all the cube permutations  ########################
############################################################################################

# Takes a position and returns a list of all the permutations that arise from performing every move
def get_moves(pos):
    return [F1(pos), F3(pos), F2(pos),
            R1(pos), R3(pos), R2(pos),
            U1(pos), U3(pos), U2(pos)]


# Hard coded moves to perform on the cube.
def F1(pos): # Front Quarter Turn Clockwise
    return (pos[0] + pos[1] + pos[19] + pos[17] +
            pos[2] + pos[5] + pos[3] + pos[7] +
            pos[10] + pos[8] + pos[11] + pos[9] +
            pos[6] + pos[4] + pos[14] + pos[15] +
            pos[16] + pos[12] + pos[18] + pos[13] +
            pos[20] + pos[21] + pos[22] + pos[23])

def F3(pos): # Front Quarter Turn Counterclockwise
    return (pos[0] + pos[1] + pos[4] + pos[6] +
            pos[13] + pos[5] + pos[12] + pos[7] +
            pos[9] + pos[11] + pos[8] + pos[10] +
            pos[17] + pos[19] + pos[14] + pos[15] +
            pos[16] + pos[3] + pos[18] + pos[2] +
            pos[20] + pos[21] + pos[22] + pos[23])

def F2(pos): # Front Half Turn
    return (pos[0] + pos[1] + pos[13] + pos[12] +
            pos[19] + pos[5] + pos[17] + pos[7] +
            pos[11] + pos[10] + pos[9] + pos[8] +
            pos[3] + pos[2] + pos[14] + pos[15] +
            pos[16] + pos[6] + pos[18] + pos[4] +
            pos[20] + pos[21] + pos[22] + pos[23])

def R1(pos): # Right Quarter Turn Clockwise
    return (pos[0] + pos[9] + pos[2] + pos[11] +
            pos[6] + pos[4] + pos[7] + pos[5] +
            pos[8] + pos[13] + pos[10] + pos[15] +
            pos[12] + pos[22] + pos[14] + pos[20] +
            pos[16] + pos[17] + pos[18] + pos[19] +
            pos[3] + pos[21] + pos[1] + pos[23])

def R3(pos): # Right Quarter Turn Counterclockwise
    return (pos[0] + pos[22] + pos[2] + pos[20] +
            pos[5] + pos[7] + pos[4] + pos[6] +
            pos[8] + pos[1] + pos[10] + pos[3] +
            pos[12] + pos[9] + pos[14] + pos[11] +
            pos[16] + pos[17] + pos[18] + pos[19] +
            pos[15] + pos[21] + pos[13] + pos[23])

def R2(pos): # Right Half Turn
    return (pos[0] + pos[13] + pos[2] + pos[15] +
            pos[7] + pos[6] + pos[5] + pos[4] +
            pos[8] + pos[22] + pos[10] + pos[20] +
            pos[12] + pos[1] + pos[14] + pos[3] +
            pos[16] + pos[17] + pos[18] + pos[19] +
            pos[11] + pos[21] + pos[9] + pos[23])

def U1(pos): # Up Quarter Turn Clockwise
    return (pos[2] + pos[0] + pos[3] + pos[1] +
            pos[20] + pos[21] + pos[6] + pos[7] +
            pos[4] + pos[5] + pos[10] + pos[11] +
            pos[12] + pos[13] + pos[14] + pos[15] +
            pos[8] + pos[9] + pos[18] + pos[19] +
            pos[16] + pos[17] + pos[22] + pos[23])

def U3(pos):# Up Quarter Turn Counterclockwise
    return (pos[1] + pos[3] + pos[0] + pos[2] +
            pos[8] + pos[9] + pos[6] + pos[7] +
            pos[16] + pos[17] + pos[10] + pos[11] +
            pos[12] + pos[13] + pos[14] + pos[15] +
            pos[20] + pos[21] + pos[18] + pos[19] +
            pos[4] + pos[5] + pos[22] + pos[23])

def U2(pos): # Up Half Turn
    return (pos[3] + pos[2] + pos[1] + pos[0] +
            pos[16] + pos[17] + pos[6] + pos[7] +
            pos[20] + pos[21] + pos[10] + pos[11] +
            pos[12] + pos[13] + pos[14] + pos[15] +
            pos[4] + pos[5] + pos[18] + pos[19] +
            pos[8] + pos[9] + pos[22] + pos[23])
# ##########################################################################################




############################################################################################
######################   part relates to CUBOTino_P  #######################################
############################################################################################

def imports():
    global time, rm, servo    
    import Cubotino_P_moves as rm        # custom library, traslates the cuber solution string in robot movements string
    import Cubotino_P_servos as servo    # custom library for the servos control
    import time



def clear_terminal():
    """ Clears the terminal and positions the cursors on top left; Still possible to scroll up in case of need"""
    print("\x1b[H\x1b[2J")               # escape sequence



def import_solver():
    # importing Kociemba solver
    global sv
    import os.path, pathlib                               # library to check file presence            
    folder = pathlib.Path().resolve()                     # active folder (should be home/pi/cube)  
    fname = os.path.join(folder,'solver2x2x2','solver.py') # active folder + Solver2x2x2 + solver name
    solver_found = False                                  # boolean to track the import the copied solver in subfolder
    if os.path.exists(fname):                             # case the solver exists in 'Solver2x2x2' subfolder
        import solver2x2x2.solver as sv                   # import Kociemba solver copied in sub-folder
        return True                                       # boolean to track the  import the copied solver in subfolder
    else:
        return False                                      # boolean to track the import the copied solver in subfolder




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
    for i in range(24):          # iteration over the 54 facelets
        new_status[i]=cube_status[ref[i]]  # updated cube status takes the facelet from previous status at ref location
    
    return new_status            # updated cube status is returned





def robot_set_servo():
    """ The robot uses a couple of servos; This functions positions the servos to the start position."""
    # servos are initialized, and set to their starting positions
    debug=False
    ret, timer = servo.init_servo(debug, start_pos = 'read', f_to_close_mode=True)
    return ret, timer




def robot_simulator(cube_string):

    """ Calls the Hegbert Kociemba solver, and returns the solution's moves
    from: https://github.com/hkociemba/Rubiks2x2x2-OptimalSolver 
    The solver returns the optimal solution.
    More solutions could be returned, having the same quantity of cube movements; In this case
    it is chosen the faster solution for the robot.
    The cube is virtually manipulated with the movements from the robot solver.
    After the last cube (virtual) manipulation, the resulting cube_status is analized.
    Result analysis is thereturn from this function (1=0 ok, 0=Not Ok).
    """
    
    simulation=True                         # flag for the robot solver to run as simulator
    informative=False                       # when informative is set False there are no prints from the optimizers
    solutions = sv.solve(cube_string)       # solver is called to get the solutions (face rotations)
    solutions = solutions.splitlines()      # solver return is plit by lines (more solutions are often returned)
    solution = {}                           # empty dict to store the solver solution(s)
    
    for i, sol in enumerate(solutions):     # iteration over the returned solutions
        solution[i] = sol[:sol.find('(')]   # sequence of robot manoeuvres are stored per each solver solution

    if len(solution)==1:                    # case there are multiple solutions
        s = solutions[0]                    # the first solution is taken
        solution_Text = s[s.find('(')+1:s.find(')')-1]+' moves  '+ s[:s.find('(')]  # manipulated string, used in Cubotino
        s = s[:s.find('(')]                 # solution capture the sequence of manoeuvres
        if s[:5] =='Error':                 # case solution error (incoherent cube string sent to the solver)
            solution_Text = 'Error'         # 'Error' string is assigned to solution_Text variable
        
        if solution_Text != 'Error':        # case the solver does not returns errors
            
            # string with robot movements, and total movements
            _, robot_moves, total_robot_moves, opt = rm.robot_required_moves(s,solution_Text,simulation,informative)
            est_time = servo.estimate_time(robot_moves, timer, slow_time=0)  # estimation servos time for the single solution
    
    # selecting the solution with lower robot movements
    elif len(solution)>1:                   # case there are multiple solutions
        estimate_time = {}                  # dict to store the solving time taken by the servos
        robot_moves_strings = {}            # dict to store the the robot movement strings
        tot_robot_moves ={}                 # empty dict to store the total robot movements 
        for i, s in solution.items():       # iteration over the solver solutions
            solution_Text = ''              # an empty text is assigned to solution_Text variable  
              
            # string with robot movements, for 'i' solution
            _, robot_moves, total_robot_moves, opt = rm.robot_required_moves(s,solution_Text,simulation,informative)
            estimate_time[i] = servo.estimate_time(robot_moves, timer, slow_time=0)   # estimated time for the robot moves in argument
            robot_moves_strings[i] = robot_moves    # robot movements for the fastest solution
            tot_robot_moves[i] = total_robot_moves  # total quantity of robot movements for the robot moves in argument
        
        best_solution = min(estimate_time, key=estimate_time.get)  # dict index for the fastest solution
        s = solution[best_solution]               # string of the fastest solver solution 
        est_time = estimate_time[best_solution]   # estimation servos time of the fastest solution
        robot_moves = robot_moves_strings[best_solution]   # robot movements for the fastest solution
        total_robot_moves = tot_robot_moves[best_solution]   # total quantity of robot movements for the fastest solution
            
        # solution_text places the amount of moves first, and the solution (sequence of manoeuvres) afterward
        solution_Text = s[s.find('(')+1:s.find(')')-1]+' moves  '+ s[:s.find('(')] 
    
    final_cube_status = robot_virtual_moves(cube_string, robot_moves)
    return solved_status_check(final_cube_status)
    
    


def robot_virtual_moves(cube_status, robot_moves):
    if len(robot_moves)>0:
        for i in range(0, len(robot_moves),2):
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
                    cube_status = ''
                    for i in range(24):
                        cube_status+=new_cube_status[i]
            else:
                new_cube_status = cube_facelets_permutation(cube_status, move_type, direction)
                cube_status = ''
                for i in range(24):
                    cube_status+=new_cube_status[i]
        return cube_status
    else:
        return '' 
        




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
            
        




def test_all_permutations(stop_at):
    """Generates all possible permutations of a 2x2x2 Rubik's cube.
    The permutations are generated from the solved cube status: Cube is more scrambled as the simulation proceeds.
    Each permutation (apart the solved cube) is analysed from the Cubotino_P_moves, and the faster one is selected.
    Each set of robot movements is virtually applied.
    After each of the (virtual) cube manipulation, the cube status is updated to reflect the new status.
    The last cube status is analyzed if conforming to the solved cube.
    The simulation can be limited to a predefined quantity of tests.
    """
    
    start_time = time.time()                             # time reference is assigned 
    solved_cube = 'UUUURRRRFFFFDDDDLLLLBBBB'             # cube_status of the  solved cube   
    test=0                                               # counter for the tests performed
    test_ok_counter = 0                                  # counter for the cube status correctly solved

    dist = [{solved_cube}, set(get_moves(solved_cube))]  # dist holds a list of sets, to track the already tested permutations
    for cube_status in dist[-1]:                         # tests the first 9 permutations applied to the solved cube
        test += 1                                        # test counter is incremented
        test_ok_counter += robot_simulator(cube_status)  # robot solver simulator is called and positive results are added
        print(f"Permutations tested:{test:,}  Errors:{test-test_ok_counter}", end='\r', flush=True)

    while dist[-1]:                                      # looping untill possible to append nes cube statust at dist end
        dist.append(set())                               # and empty set is appended to the dist list
        for pos in dist[-2]:                             # iterating over all the "last added moves"
            for sub_pos in get_moves(pos):               # all the possible moves are applied to each cube status 
                if sub_pos not in dist[-1] and sub_pos not in dist[-2] and sub_pos not in dist[-3]: # case the generated cube status is a new one
                    dist[-1].add(sub_pos)                # new cube status is appended to the set at last dist list position
                    test += 1                            # counter is incremented
                    test_ok_counter += robot_simulator(sub_pos) # robot solver simulator is called and positive results are added
                    print(f"Permutations tested:{test:,}  Errors:{test-test_ok_counter}", end='\r', flush=True)
                    if test >= stop_at:                  # case the simulation has reached a predefined target
                        break                            # for loop is interrupted
            if test >= stop_at:                          # case the simulation has reached a predefined target
                break                                    # for loop is interrupted
        if test >= stop_at:                              # case the simulation has reached a predefined target
            break                                        # for loop is interrupted
    
    tot_time = time.time()-start_time                    # total simulation time is calculated
    print(f"Permutations tested:{test:,} ")              # feedback is printed
    print(f"The virtual movements applied by CUBOTino_P have correctly solved {test_ok_counter:,d} different cubes")
    print(f"The analysis took {round(tot_time,1)} seconds")
    print(f"(average of {round(1000*tot_time/test,2)} millisecs per each cube status)")
    print()
# ##########################################################################################








############################################################################################
################  test all the 2x2x2 permutations in CUBOTino_P  ###########################
############################################################################################

if __name__ == "__main__":
    
    stop = False                     # flag to stop the simulation at a givent quantity of permutations
    if args.stop != None:            # case 'stop' argument exists
        stop_at = args.stop          # stop value is assigned
    else:                            # case 'stop' argument exists
        stop_at = 3674160 + 1        # max possible permutations plus one

    clear_terminal()                 # cleares the terminal
    imports()                        # imports the needed libraries
    
    # cube solver to get the solution per each permutation
    ret = import_solver()            # Kociemba solver is imported
    print("Solver imported:", ret)   # feedback is prionted to terminal

    # servos init to get the servos timers, necessary for searching the fastest robot solution
    robot_init_status, timer = robot_set_servo()  # the robot servo are initialized, to get the servos timers
    print("Timers returned by the robot:", robot_init_status)   # feedback is prionted to terminal
    row = "#"*80                     # string of characters used as separator
    print(row)                       # separator is printed to the terminal  

    test_all_permutations(stop_at)
# ##########################################################################################
