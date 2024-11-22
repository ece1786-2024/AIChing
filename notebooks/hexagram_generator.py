import json
import random


def get_altered_hexagram(hexagram_index, alter_list):
    # Load index_to_lines.json and lines_to_index.json
    with open("../data/index_to_lines.json", "r", encoding="utf-8") as infile:
        index_to_lines = json.load(infile)

    with open("../data/lines_to_index.json", "r", encoding="utf-8") as infile:
        lines_to_index = json.load(infile)

    with open("../data/index_to_name.json", "r", encoding="utf-8") as infile:
        index_to_name = json.load(infile)

    # Get the original string representation of the hexagram
    original_lines = index_to_lines[str(hexagram_index)]

    # Convert the original string to a list to modify it
    altered_lines = list(original_lines)

    # Apply the alterations based on the alter_list
    for pos in alter_list:
        # Adjust for 1-based index by subtracting 1
        index = pos - 1
        # Flip 'P' to 'N' or 'N' to 'P'
        altered_lines[index] = "P" if altered_lines[index] == "N" else "N"

    # Join the altered lines back into a string
    altered_lines_string = "".join(altered_lines)

    # Get the altered hexagram index from lines_to_index.json
    altered_hexagram_index = lines_to_index[altered_lines_string]

    altered_hexagram_name = index_to_name[altered_hexagram_index]

    return altered_lines_string, altered_hexagram_index, altered_hexagram_name


def process():
    # get the first hexagram
    first_hexagram_index = random.randint(1, 64)
    with open("../data/index_to_name.json", "r", encoding="utf-8") as infile:
        index_to_name = json.load(infile)
    first_hexagram_name = index_to_name[str(first_hexagram_index)]

    # get the lines to altered in a list
    # Randomly determine the number of elements in the list (0 to 6)
    num_elements = random.randint(0, 6)

    # Generate a list of unique random integers between 1 and 6
    alter_list = random.sample(
        range(1, 7), num_elements
    )  # range(1, 7) generates numbers 1 through 6

    # get the second hexagram
    altered_string, second_hexagram_index, second_hexagram_name = get_altered_hexagram(
        first_hexagram_index, alter_list
    )

    return (
        str(first_hexagram_index),
        first_hexagram_name,
        alter_list,
        str(second_hexagram_index),
        second_hexagram_name,
    )
