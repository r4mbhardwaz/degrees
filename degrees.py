import csv
import sys

from util import Node, StackFrontier, QueueFrontier

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}


def load_data(directory):
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass


def main(directory="large"):
    if len(sys.argv) > 2:
        sys.exit("Usage: python degrees.py [directory]")
    directory = sys.argv[1] if len(sys.argv) == 2 else directory

    # Load data from files into memory
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")

    source = person_id_for_name(input("Name: "))
    if source is None:
        sys.exit("Person not found.")
    target = person_id_for_name(input("Name: "))
    if target is None:
        sys.exit("Person not found.")

    path = shortest_path(source, target)

    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        path = path
        path = list(reversed(path))
        print(f"{degrees-1} degrees of separation.")
        # print(path)
        person2, person1 = None, None
        for i in range(degrees):
            if person2:
                person1 = person2
            person2 = people[path[i][1]]["name"]
            # print(person1, person2)
            movie_data = movies.get(path[i][0])
            movie = None
            if movie_data:
                movie = movie_data.get("title")
                # print(f'in movie {movie}')
            if movie:
                print(f"{i}: {person1} and {person2} starred in {movie}")

def shortest_path(source, target):
    """
    Returns the shortest list of (movie_id, person_id) pairs
    that connect the source to the target.

    If no possible path, returns None.
    """
    # TODO
    fr = QueueFrontier() # frontier
    explored = [] # Explored stack
    start_node = Node(state=source, parent=None, action=(None, source))
    fr.add(start_node)
    node = None
    while 1:
        if fr.empty(): # frontier is empty
            print('No Solution')
            break
        node = fr.remove()
        if node.state == target:
            print("found solution")
            break
        # print(node.state)
        for neighbor in neighbors_for_person(node.state):
            # print(neighbor)
            if neighbor[1] not in explored:
                nd = Node(state=neighbor[1], parent=node, action=neighbor)
                fr.add(nd)
                explored.append(neighbor[1])
    print()
        # print(f'''
# Explored: {explored}
        # ''')
    # for making it to a list of (movie_id, person)
    if node:
        data = []
        path = node
        while 1:
            if not path:
                break
            data.append(path.action)
            if path.action:
                if not path.action[0]:
                    break
                path = path.parent
            else:
                break
        return data
        # return list(reversed(data)) # reversed order of the list
    return []


def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]


def neighbors_for_person(person_id):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = set()
    for movie_id in movie_ids:
        for person_id in movies[movie_id]["stars"]:
            neighbors.add((movie_id, person_id))
    return neighbors


if __name__ == "__main__":
    main()
