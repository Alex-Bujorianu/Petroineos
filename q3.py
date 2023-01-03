from math import dist

# Note: this function assumes Python >= 3.10
def move_robot(instructions: list) -> float:
    #@param instructions: a list of tuples, with the first item a string, representing the instruction, and second item a number
    #@return: the Euclidean distance between the final position of the robot and the point (0, 0)
    # Left is negative, right is positive, up is positive and down negative
    start = [0, 0]
    final_position = [0, 0]
    for item in instructions:
        if item[0] == "STOP":
            return dist(start, final_position)
        else:
            match item[0]:
                case "LEFT":
                    final_position[0] = final_position[0] - item[1]
                case "RIGHT":
                    final_position[0] = final_position[0] + item[1]
                case "DOWN":
                    final_position[1] = final_position[1] - item[1]
                case "UP":
                    final_position[1] = final_position[1] + item[1]
    # If this statement is executed, you probably made a mistake when calling the function
    return dist(start, final_position)

assert move_robot([("STOP")]) == 0
assert move_robot([("RIGHT", 3), ("UP", 4), ("STOP")]) == 5