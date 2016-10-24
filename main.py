import pickle
import copy
import json
import random
import re
import sys
from enum import Enum


class Orientation(Enum):
    horizontal = 0
    vertical = 1

class GameData():
    def __init__(self, **entries):
        self.last_coordinates = ""
        self.player1_turn = True
        self.ships_player1 = {"aircraftcarrier":{"start":"", "end":"", "orientation":Orientation.horizontal, "hits":[]},\
                    "battleship": {"coords": [], "orientation": Orientation.horizontal, "hits":[]},\
                    "cruiser": {"coords": [], "orientation": Orientation.horizontal, "hits":[]},\
                    "destroyer1": {"coords": [], "orientation": Orientation.horizontal, "hits":[]},\
                    "destroyer2": {"coords": [], "orientation": Orientation.horizontal, "hits":[]},\
                    "submarine1": {"coords": [], "orientation": Orientation.horizontal, "hits":[]},\
                    "submarine2": {"coords": [], "orientation": Orientation.horizontal, "hits":[]}\
                    }

        self.ships_player2 = {"aircraftcarrier":{"coords": [], "orientation":Orientation.horizontal, "hits":[]},\
                    "battleship": {"coords": [], "orientation": Orientation.horizontal, "hits":[]},\
                    "cruiser": {"coords": [], "orientation": Orientation.horizontal, "hits":[]},\
                    "destroyer1": {"coords": [], "orientation": Orientation.horizontal, "hits":[]},\
                    "destroyer2": {"coords": [], "orientation": Orientation.horizontal, "hits":[]},\
                    "submarine1": {"coords": [], "orientation": Orientation.horizontal, "hits":[]},\
                    "submarine2": {"coords": [], "orientation": Orientation.horizontal, "hits":[]}\
                    }
        self.player1_coordinates = []
        self.player2_coordinates = []
        self.player1_board = []
        self.player2_board = []
        self.availableCoordsP1 = []
        self.availableCoordsP2 = []
        self.botMode = False
        self.tasksMode = False
        self.octopusCount = 10
        self.numOfSeaMines = 5
        self.seaMineCoordinates = []
        self.ready = False
        self.__dict__.update(entries)

"""
A Custom JSONEncoder used to encode the GameData class
"""
class GameDataJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, GameData):
            return obj.__dict__
        if isinstance(obj, Enum):
            return obj.value
        else:
            return json.JSONEncoder.default(self, obj)

"""Python dictionaries are unsorted by default, if you have to sort the Keys see def board(coordinates)
"""
coordinates = {'A1':' ', 'A2':' ', 'A3':' ', 'A4':' ', 'A5':' ',\
               'A6':' ', 'A7':' ', 'A8':' ', 'A9':' ', 'A0': ' ',\
               'B1':' ', 'B2':' ', 'B3':' ', 'B4':' ', 'B5':' ',\
               'B6':' ', 'B7':' ', 'B8':' ', 'B9':' ', 'B0': ' ',\
               'C1':' ', 'C2':' ', 'C3':' ', 'C4':' ', 'C5':' ',\
               'C6':' ', 'C7':' ', 'C8':' ', 'C9':' ', 'C0': ' ',\
               'D1':' ', 'D2':' ', 'D3':' ', 'D4':' ', 'D5':' ',\
               'D6':' ', 'D7':' ', 'D8':' ', 'D9':' ', 'D0': ' ',\
               'E1':' ', 'E2':' ', 'E3':' ', 'E4':' ', 'E5':' ',\
               'E6':' ', 'E7':' ', 'E8':' ', 'E9':' ', 'E0': ' ',\
               'F1':' ', 'F2':' ', 'F3':' ', 'F4':' ', 'F5':' ',\
               'F6':' ', 'F7':' ', 'F8':' ', 'F9':' ', 'F0': ' ',\
               'G1':' ', 'G2':' ', 'G3':' ', 'G4':' ', 'G5':' ',\
               'G6':' ', 'G7':' ', 'G8':' ', 'G9':' ', 'G0': ' ',\
               'H1':' ', 'H2':' ', 'H3':' ', 'H4':' ', 'H5':' ',\
               'H6':' ', 'H7':' ', 'H8':' ', 'H9':' ', 'H0': ' ',\
               'I1':' ', 'I2':' ', 'I3':' ', 'I4':' ', 'I5':' ',\
               'I6':' ', 'I7':' ', 'I8':' ', 'I9':' ', 'I0': ' ',\
               'J1':' ', 'J2':' ', 'J3':' ', 'J4':' ', 'J5':' ',\
               'J6':' ', 'J7':' ', 'J8':' ', 'J9':' ', 'J0': ' '\
               }

"""Do NOT change any lines of this function!
 Use following symbols:
 ship: ◯ (U+25EF)
 hit: ╳  (U+2573)
 miss: ≈ (U+2248)
"""
def board(coordinates):
    printboard = ("   ┌───┬───┬───┬───┬───┬───┬───┬───┬───┬───┐\n")

    last_key = "A"
    line = " "
    line = line + last_key
    line = line + " │"
    keylist = list(coordinates.keys())

    for key in sorted(keylist):
        if key[0] == last_key:
            line = line + " " + coordinates[key] + " " + "│"
        else:
            printboard += line
            printboard += "\n   ├───┼───┼───┼───┼───┼───┼───┼───┼───┼───┤\n"
            line = " "
            last_key = key[0]
            line = line + last_key
            line = line + " │"
            line = line + " " + coordinates[key] + " " + "│"
    printboard += line
    printboard += "\n   └───┴───┴───┴───┴───┴───┴───┴───┴───┴───┘"
    printboard += "\n     0   1   2   3   4   5   6   7   8   9   "

    return printboard

"""
Prints all error messages of player
"""
def printErrorMessage(message):
    if gameData.player1_turn == True:
        print(message)

"""
Saves hole gameData object as a binary file
"""
def saveGame():
    if gameData.ready:
        pickle.dump(gameData, open("gameData.txt", "wb"))
        print("Game saved.")
    else:
        print("Game cannot be saved before all ships are placed.")

"""
Loads hole gameData object from a binary file
"""
def loadGame():
    global gameData
    try:
        gameData = pickle.load(open("gameData.txt", "rb"))
        startGame()
        print("Game loaded.")
    except FileNotFoundError:
        print("No saved game could be found.")

"""
Check if entered coordinate(s) is/are valid
"""
def isCoordInputValid(str, numOfFields):
    if gameData.tasksMode:
        if str == "save":
            saveGame()
            return False
        if str == "load":
            loadGame()
            return False
    if numOfFields > 1:
        if str.count(' ') != 1:
            printErrorMessage("Please specify 2 coordinates.")
            return False
        else:
            result = re.match(r'([A-J][0-9][ ][A-J][0-9])', str)
    else:
        if str.count(' ') != 0:
            printErrorMessage("Please specify 1 coordinate.")
            return False
        else:
            result = re.match(r'([A-J][0-9])', str)
    if result is None:
        printErrorMessage("You entered an invalid coordinate.");
        return False
    else:
        if " ".join(result.groups()) != str:
            printErrorMessage("You entered an invalid coordinate.");
            return False
        else:
            return True

"""
Calculates the distance in fields between the entered coordinatess
"""
def distanceBetweenCoords(x, y):
    if x[0] != y[0]:
        if ord(x[0]) < ord(y[0]):
            result = ord(y[0]) - ord(x[0])
        elif ord(x[0]) > ord(y[0]):
            result = ord(x[0]) - ord(y[0])
    else:
        if ord(x[1]) < ord(y[1]):
            result = ord(y[1]) - ord(x[1])
        elif ord(x[1]) > ord(y[1]):
            result = ord(x[1]) - ord(y[1])
    return result + 1

"""
Checks if the second entered coordinate is valid
"""
def isEndCoordValid(coords, numOfFields):
    if numOfFields > 1:
        coordX = list(coords[0])
        coordY = list(coords[1])
        if (coordX[0] != coordY[0] and coordX[1] != coordY[1]) or distanceBetweenCoords(coordX, coordY) != numOfFields:
            printErrorMessage("Your end coordinate is invalid.")
            return False
        else:
            return True

"""
Checks if the coordinate is horizontal or vertical
"""
def getDirection(coords):
    coordX = list(coords[0])
    coordY = list(coords[1])
    if coordX[0] != coordY[0]:
        return Orientation.vertical
    else:
        return Orientation.horizontal

"""
Input valid coordinates
"""
def inputCoordinates(inputText, numOfFields):
    userInput = input(inputText)
    if isCoordInputValid(userInput, numOfFields) == True:
        if numOfFields > 1:
            coords = userInput.split(" ")
            if isEndCoordValid(coords, numOfFields):
                return coords;
        else:
            return userInput

"""
Sets ship on specific field
"""
def setShip(coords, numOfFields, playerCoordinates):
    if coords is not None:
        if numOfFields > 1:
            for coord in coords:
                playerCoordinates[coord] = '◯'
        else:
            playerCoordinates[coords] = '◯'

"""
Get all coordinates as a list which are in the given range
"""
def getCoordsRange(coords, numOfFields):
    coordsRange = []
    if coords is not None:
        coord1 = list(coords[0])
        coord2 = list(coords[1])
        orientation = getDirection(coords)
        if orientation == Orientation.horizontal:
            number = int(coord1[1])
            for x in range(numOfFields):
                coordsRange.append(coord1[0] + str(number))
                number = number + 1
        else:
            character = coord1[0]
            for x in range(numOfFields):
                coordsRange.append(character + coord1[1])
                if coord1[0] < coord2[0]:
                    character = chr(ord(character) + 1)
                else:
                    character = chr(ord(character) - 1)
    return coordsRange

"""
Get all surrounded coordinates of a ship
"""
def getSurroundingCoords(coords, numOfFields):
    surroundingCoords = []
    if numOfFields > 1:
        surroundingCoords.append(coords[0])
        surroundingCoords.append(coords[1])
        orientation = getDirection(coords)
        iterations = 1
        for coord in coords:
            y = coord[0]
            x = coord[1]
            if orientation == Orientation.vertical:
                if int(x) > 0:
                    surroundingCoords.append(y + str((int(x) - 1)))
                if int(x) < 9:
                    surroundingCoords.append(y + str((int(x) + 1)))
                if iterations == 1:
                    if y > 'A':
                        surroundingCoords.append(chr(ord(y) - 1) + x)
                        if int(x) > 0:
                            surroundingCoords.append(chr(ord(y) - 1) + str((int(x) - 1)))
                        if int(x) < 9:
                            surroundingCoords.append(chr(ord(y) - 1) + str((int(x) + 1)))
                if iterations == len(coords):
                    if y < 'J':
                        surroundingCoords.append(chr(ord(y) + 1) + x)
                        if int(x) > 0:
                            surroundingCoords.append(chr(ord(y) + 1) + str((int(x) - 1)))
                        if int(x) < 9:
                            surroundingCoords.append(chr(ord(y) + 1) + str((int(x) + 1)))
            else:
                if y > 'A':
                    surroundingCoords.append(chr(ord(y) - 1) + x)
                if y < 'J':
                    surroundingCoords.append(chr(ord(y) + 1) + x)
                if iterations == 1:
                    if int(x) > 0:
                        surroundingCoords.append(y + str((int(x) - 1)))
                        if y > 'A':
                            surroundingCoords.append(chr(ord(y) - 1) + str((int(x) - 1)))
                        if y < 'J':
                            surroundingCoords.append(chr(ord(y) + 1) + str((int(x) - 1)))
                if iterations == len(coords):
                    if int(x) < 9:
                        surroundingCoords.append(y + str((int(x) + 1)))
                        if y > 'A':
                            surroundingCoords.append(chr(ord(y) - 1) + str((int(x) + 1)))
                        if y < 'J':
                            surroundingCoords.append(chr(ord(y) + 1) + str((int(x) + 1)))
            iterations = iterations + 1
    else:
        surroundingCoords.append(coords)
        y = coords[0]
        x = coords[1]
        if y > 'A':
            surroundingCoords.append(chr(ord(y) - 1) + x)
            if int(x) > 0:
                surroundingCoords.append(chr(ord(y) - 1) + str((int(x) - 1)))
            if int(x) < 9:
                surroundingCoords.append(chr(ord(y) - 1) + str((int(x) + 1)))
        if y < 'J':
            surroundingCoords.append(chr(ord(y) + 1) + x)
            if int(x) > 0:
                surroundingCoords.append(chr(ord(y) + 1) + str((int(x) - 1)))
            if int(x) < 9:
                surroundingCoords.append(chr(ord(y) + 1) + str((int(x) + 1)))
        if int(x) > 0:
            surroundingCoords.append(y + str((int(x) - 1)))
        if int(x) < 9:
            surroundingCoords.append(y + str((int(x) + 1)))

    return surroundingCoords

"""
Checks if the placement of the ship is valid
"""
def isPlacementValid(coords, playerCoordinates):
    for coord in coords:
        if playerCoordinates[coord] != ' ':
            return False
    return True

"""
Get random coordinate(s) where characters are A-J and numbers are 0-9
"""
def getRandomCoords(numOfFields):
    coords = []
    orientation = random.randint(0,1)
    coordY = random.choice("ABCDEFGHIJ")
    coordX = random.randint(0, 9)
    if orientation == Orientation.horizontal.value:
        coords.append(coordY + str(coordX))
        if numOfFields > 1:
            coords.append(coordY + str(coordX + (numOfFields - 1)))
    else:
        coords.append(coordY + str(coordX))
        if numOfFields > 1:
            coords.append(chr(ord(coordY) + (numOfFields - 1)) + str(coordX))
    return coords

"""
Get valid coordinates from user/bot
"""
def getCoordsFromPlayer(text, numOfFields, shipType, prevShipType, playerCoordinates):
    success = False
    while success == False:
        if gameData.player1_turn and gameData.botMode == False:
            coords = inputCoordinates(text, numOfFields)
        else:
            coords = getRandomCoords(numOfFields)
            if numOfFields > 1:
                coordsAsString = ' '.join(coords)
            else:
                coordsAsString = coords[0]
                coords = coordsAsString
            if isCoordInputValid(coordsAsString, numOfFields) == False:
                coords = None
        if coords is not None:
            if numOfFields > 1:
                coordsRange = getCoordsRange(coords, numOfFields)
                if isPlacementValid(getSurroundingCoords(coordsRange, numOfFields), playerCoordinates):
                    setShip(coordsRange, numOfFields, playerCoordinates)
                    success = True
                else:
                    printErrorMessage("Ship overlaps or adjoins " + prevShipType + ". Reposition " + shipType + ".")
            else:
                if isPlacementValid(getSurroundingCoords(coords, numOfFields), playerCoordinates):
                    setShip(coords, numOfFields, playerCoordinates)
                    success = True
                else:
                    printErrorMessage("Ship overlaps or adjoins " + prevShipType + ". Reposition " + shipType + ".")
    if gameData.player1_turn:
        if numOfFields > 1:
            gameData.ships_player1[shipType]["coords"] = coordsRange
            gameData.ships_player1[shipType]["orientation"] = getDirection(coords)
        else:
            coordsArray = []
            coordsArray.append(coords)
            gameData.ships_player1[shipType]["coords"] = coordsArray
    else:
        if numOfFields > 1:
            gameData.ships_player2[shipType]["coords"] = coordsRange
            gameData.ships_player2[shipType]["orientation"] = getDirection(coords)
        else:
            coordsArray = []
            coordsArray.append(coords)
            gameData.ships_player2[shipType]["coords"] = coordsArray

"""
Set sea mines
"""
def setSeaMines():
    availableCoorinates = copy.deepcopy(coordinates)
    for x in range(0, gameData.numOfSeaMines):
        coord = random.choice(list(availableCoorinates.keys()))
        gameData.seaMineCoordinates.append(coord)

"""
Check if coordinate is a sea mine
"""
def isSeaMine(coord):
    for seaMine in gameData.seaMineCoordinates:
        if coord == seaMine:
            return True
    return False

"""
Destroy all surrounding filds
"""
def destroyAllSurroundingFields(coord, playerCoordinates, playerBoard, playerShips, availableCoords):
    coordsToDestroy = []
    coordsToDestroy.append(coord)
    coordsToDestroy.append(chr(ord(coord[0]) - 1) + coord[1])
    coordsToDestroy.append(coord[0] + str(int(coord[1]) + 1))
    coordsToDestroy.append(chr(ord(coord[0]) + 1) + coord[1])
    coordsToDestroy.append(coord[0] + str(int(coord[1]) - 1))
    coordsToDestroy.append(chr(ord(coord[0]) + 1) + str(int(coord[1]) + 1))
    coordsToDestroy.append(chr(ord(coord[0]) + 1) + str(int(coord[1]) - 1))
    coordsToDestroy.append(chr(ord(coord[0]) - 1) + str(int(coord[1]) + 1))
    coordsToDestroy.append(chr(ord(coord[0]) - 1) + str(int(coord[1]) - 1))
    for c in coordsToDestroy:
        if c in list(availableCoords.keys()):
            if isHit(c, playerCoordinates):
                ship = getShip(c, playerShips)
                ship["hits"].append(c)
                if len(ship["hits"]) == len(ship["coords"]):
                    print("Sea mine sank " + ship["shipType"] + " (" + c + ").")
                else:
                    print("Sea mine hit " + ship["shipType"] + " (" + c + ").")
                playerBoard[c] = '╳'
                playerCoordinates[c] = '╳'
            else:
                print("Sea mine hit the water (" + c + ").")
                playerBoard[c] = '≈'
                playerCoordinates[c] = '≈'
            del availableCoords[c]


"""
Inits game and sets all necessary game data
"""
def initGame():
    gameData.player1_coordinates = copy.deepcopy(coordinates)
    gameData.player2_coordinates = copy.deepcopy(coordinates)
    gameData.player1_board = copy.deepcopy(coordinates)
    gameData.player2_board = copy.deepcopy(coordinates)
    gameData.availableCoordsP1 = copy.deepcopy(coordinates)
    gameData.availableCoordsP2 = copy.deepcopy(coordinates)
    print(board(gameData.player1_coordinates))
    print("Please place your ships...")
    """
    Read player 1 (User) coordinates
    """
    getCoordsFromPlayer("set coordinates for aircraftcarrier (5 fields): ", 5, "aircraftcarrier", "", gameData.player1_coordinates)
    print(board(gameData.player1_coordinates))
    getCoordsFromPlayer("set coordinates for battleship (4 fields): ", 4, "battleship", "aircraftcarrier", gameData.player1_coordinates)
    print(board(gameData.player1_coordinates))
    getCoordsFromPlayer("set coordinates for cruiser (3 fields): ", 3, "cruiser", "battleship", gameData.player1_coordinates)
    print(board(gameData.player1_coordinates))
    getCoordsFromPlayer("set coordinates for destroyer1 (2 fields): ", 2, "destroyer1", "cruiser", gameData.player1_coordinates)
    print(board(gameData.player1_coordinates))
    getCoordsFromPlayer("set coordinates for destroyer2 (2 fields): ", 2, "destroyer2", "destroyer1", gameData.player1_coordinates)
    print(board(gameData.player1_coordinates))
    getCoordsFromPlayer("set coordinate for submarine1 (1 field): ", 1, "submarine1", "destroyer2", gameData.player1_coordinates)
    print(board(gameData.player1_coordinates))
    getCoordsFromPlayer("set coordinate for submarine2 (1 field): ", 1, "submarine2", "submarine1", gameData.player1_coordinates)
    print(board(gameData.player1_coordinates))
    print("Bot opponent is placing ships...")
    """
    Switch player to bot
    """
    gameData.player1_turn = False
    """
    Read player 2 (bot) coordinates
    """
    getCoordsFromPlayer("", 5, "aircraftcarrier", "", gameData.player2_coordinates)
    getCoordsFromPlayer("", 4, "battleship", "aircraftcarrier", gameData.player2_coordinates)
    getCoordsFromPlayer("", 3, "cruiser", "battleship", gameData.player2_coordinates)
    getCoordsFromPlayer("", 2, "destroyer1", "cruiser", gameData.player2_coordinates)
    getCoordsFromPlayer("", 2, "destroyer2", "destroyer1", gameData.player2_coordinates)
    getCoordsFromPlayer("", 1, "submarine1", "destroyer2", gameData.player2_coordinates)
    getCoordsFromPlayer("", 1, "submarine2", "submarine1", gameData.player2_coordinates)

    if gameData.tasksMode:
        setSeaMines()

"""
Checks if specific coordinate is a hit
"""
def isHit(coord, playerCoordinates):
    for key in playerCoordinates:
        if key == coord:
            if playerCoordinates[key] == '◯':
                return True
            else:
                return False

"""
Get the ship by any coordinate of the ship
"""
def getShip(coord, ships):
    for key, value in ships.items():
        for c in value["coords"]:
            if c == coord:
                value["shipType"] = key
                return value

"""
Checks if a player has won by comparing all coordinates with the hits of all ships
"""
def hasWon(ships):
    won = True
    for key, value in ships.items():
        if len(value["hits"]) != len(value["coords"]):
            won = False
    return won

"""
Starts the real gameplay
"""
def startGame():
    gameData.ready = True
    gameData.player1_turn = True
    print("Match starts...")
    print(board(gameData.player1_coordinates))
    print(board(coordinates))
    roundNumber = 0
    hasPlyer1Won = False
    hasPlyer2Won = False
    validCoord = True
    checkWinner = False
    player2LastHit = ''
    player2LastHitCounter = 0
    while hasPlyer1Won == False and hasPlyer2Won == False:
        if gameData.player1_turn:
            if gameData.botMode:
                coord = random.choice(list(gameData.availableCoordsP1.keys()))
                print("Enter target coordinate: " + coord)
                del gameData.availableCoordsP1[coord]
            else:
                coord = inputCoordinates("Enter target coordinate: ", 1)
                if coord in list(gameData.availableCoordsP1.keys()):
                    del gameData.availableCoordsP1[coord]
                else:
                    validCoord = False
                    if coord is not None:
                        print("Coordinate has already been selected. Please select another coordinate.")
            if coord is not None and validCoord:
                if isHit(coord, gameData.player2_coordinates):
                    ship = getShip(coord, gameData.ships_player2)
                    ship["hits"].append(coord)
                    if len(ship["hits"]) == len(ship["coords"]):
                        print("You sank " + ship["shipType"] + ".")
                    else:
                        print("You hit a ship.")
                    gameData.player1_board[coord] = '╳'
                    gameData.player2_coordinates[coord] = '╳'
                else:
                    print("You only hit the water.")
                    gameData.player1_board[coord] = '≈'
                    gameData.player2_coordinates[coord] = '≈'
                if gameData.tasksMode and isSeaMine(coord):
                    print("You hit a sea mine (" + coord + ").")
                    destroyAllSurroundingFields(coord, gameData.player1_coordinates, gameData.player2_board, gameData.ships_player1, gameData.availableCoordsP2)
                gameData.player1_turn = False
                roundNumber = roundNumber + 1
        else:
            if player2LastHit != '':
                if player2LastHitCounter == 0:
                    coord = chr(ord(player2LastHit[0]) - 1) + player2LastHit[1]
                    if coord not in gameData.availableCoordsP2:
                        player2LastHitCounter = player2LastHitCounter + 1
                if player2LastHitCounter == 1:
                    coord = player2LastHit[0] + str(int(player2LastHit[1]) + 1)
                    if coord not in gameData.availableCoordsP2:
                        player2LastHitCounter = player2LastHitCounter + 1
                if player2LastHitCounter == 2:
                    coord = chr(ord(player2LastHit[0]) + 1) + player2LastHit[1]
                    if coord not in gameData.availableCoordsP2:
                        player2LastHitCounter = player2LastHitCounter + 1
                if player2LastHitCounter == 3:
                    coord = coord[0] + str(int(player2LastHit[1]) - 1)
                    if coord not in gameData.availableCoordsP2:
                        coord = random.choice(list(gameData.availableCoordsP2.keys()))
                    player2LastHit = ''
                    player2LastHitCounter = 0
                player2LastHitCounter = player2LastHitCounter + 1
            else:
                coord = random.choice(list(gameData.availableCoordsP2.keys()))
            del gameData.availableCoordsP2[coord]
            if isHit(coord, gameData.player1_coordinates):
                player2LastHit = coord
                player2LastHitCounter = 0
                ship = getShip(coord, gameData.ships_player1)
                ship["hits"].append(coord)
                if len(ship["hits"]) == len(ship["coords"]):
                    print("Bot sank " + ship["shipType"] + " (" + coord + ").")
                else:
                    print("Bot hit a ship (" + coord + ").")
                gameData.player2_board[coord] = '╳'
                gameData.player1_coordinates[coord] = '╳'
            else:
                print("Bot only hit the water (" + coord + ").")
                gameData.player2_board[coord] = '≈'
                gameData.player1_coordinates[coord] = '≈'
            if gameData.tasksMode and isSeaMine(coord):
                print("Bot hit a sea mine (" + coord + ").")
                destroyAllSurroundingFields(coord, gameData.player2_coordinates, gameData.player1_board, gameData.ships_player2, gameData.availableCoordsP1)
            gameData.player1_turn = True
            roundNumber = roundNumber + 1
            checkWinner = True
        if roundNumber % gameData.octopusCount == 0 and roundNumber != 0 and gameData.tasksMode:
            setAvailableCoordsP1 = set(gameData.availableCoordsP1.keys())
            setAvailableCoordsP2 = set(gameData.availableCoordsP2.keys())
            resultAvailableCoords = list(setAvailableCoordsP1.intersection(setAvailableCoordsP2))
            if len(resultAvailableCoords) > 0:
                coord = random.choice(resultAvailableCoords)
                if coord is not None:
                    print("Octopus appeard on field " + coord + ".")
                    if isHit(coord, gameData.player1_coordinates):
                        ship = getShip(coord, gameData.ships_player1)
                        ship["hits"].append(coord)
                        if len(ship["hits"]) == len(ship["coords"]):
                            print("Octopus sank your " + ship["shipType"] + " (" + coord + ").")
                        else:
                            print("Octopus hit your ship (" + coord + ").")
                        gameData.player1_coordinates[coord] = '+'
                        gameData.player1_board[coord] = '+'
                    else:
                        print("Octopus hit the water on your field (" + coord + ").")
                        gameData.player1_coordinates[coord] = '-'
                        gameData.player1_board[coord] = '-'
                    del gameData.availableCoordsP1[coord]
                    if isHit(coord, gameData.player2_coordinates):
                        ship = getShip(coord, gameData.ships_player2)
                        ship["hits"].append(coord)
                        if len(ship["hits"]) == len(ship["coords"]):
                            print("Octopus sank bot's " + ship["shipType"] + ".")
                        else:
                            print("Octopus hit bot's ship (" + coord + ").")
                        gameData.player2_coordinates[coord] = '+'
                        gameData.player2_board[coord] = '+'
                    else:
                        print("Octopus hit the water on bot's field (" + coord + ").")
                        gameData.player2_coordinates[coord] = '-'
                        gameData.player2_board[coord] = '-'
                    del gameData.availableCoordsP2[coord]
                    checkWinner = True
        if checkWinner:
            print(board(gameData.player1_coordinates))
            print(board(gameData.player1_board))
            if hasWon(gameData.ships_player2):
                hasPlyer1Won = True
            if hasWon(gameData.ships_player1):
                hasPlyer2Won = True
            if hasPlyer1Won and hasPlyer2Won:
                print("The match ended in a draw.")
            elif hasPlyer1Won == True and hasPlyer2Won == False:
                print("Congratulations! You won the match.")
            elif hasPlyer1Won == False and hasPlyer2Won == True:
                print("Your opponent won the match.")

        validCoord = True
        checkWinner = False
    userInput = input("Do you want to play a rematch? [y/n] ")
    if userInput == "y":
        main()
    else:
        print("Exiting the game. Goodbye.")

"""
Main method will be called at the beginning of the program
"""
def main():
    global gameData
    gameData = GameData()

    if sys.argv is not None:
        if "-b" in sys.argv:
            gameData.botMode = True
        if "-t" in sys.argv:
            gameData.tasksMode = True

    initGame()
    startGame()

if __name__ == "__main__":
    main()
