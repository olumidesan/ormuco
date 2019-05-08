
# Python 3.6+

def overlaps(x,y):
    """
       This function takes in two tuples of x coordinates
       and returns whether they overlap. It works for all
       valid inputs including negative numbers and floats

    """

    overlap = True

    # Sort the input coordinates and assign its minimum and maximum values
    min_x, max_x = sorted(x)
    min_y, max_y = sorted(y)

    if (min_y > min_x) or (max_y > max_x):
        if not (min_y < max_x):
            overlap = False

    elif (min_y < min_x) or (max_y < max_x):
        if not (max_y > min_x):
            overlap = False


    return overlap


def main():
    """Command line program"""

    coordinates_list = []

    for i in range(4):
        while 1:
            x = input(f"Enter the value of coordinate x{i+1}: ")
            # The inputed coordinate must be an integer or a float
            try:    
                x = float(x)
                coordinates_list.append(x)
            except ValueError:
                print("Error: Only floats or integers are allowed as valid coordinates. Try again\n")
                continue
            break
    
    x1, x2, x3, x4 = coordinates_list

    print(f"\nThe coordinates to compare are: {x1, x2} and {x3, x4}\n")

    result = overlaps((x1,x2), (x3,x4))

    solution = 'Result: '
    
    if result:
        return solution + "The coordinates overlap"
    
    return solution + "The coordinates do not overlap"


if __name__ == "__main__":
    print(main())






