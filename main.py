"""Le programe principale responsable de l'affichage"""

"""Import des packages/biblios"""
import pygame as p
import ChessEngine
from collections import OrderedDict
from promotion import promotion
from Move import Move
from SmartMoveFinder import *
# initialisation des modules de pygame
p.init()

"""Les variables globales"""
# Dimension de la fenetre
WIDTH = 720

# la Dimension de l'échiquier
DIMENSION = 8

# la taille d'un carré
SQ_SIZE = WIDTH // DIMENSION

# Le nombre de frame par seconde, nombre du "re-dessin" du contenu de la fenetre
FPS = 60

# Dictionnaire de stockage des images des pieces, préferabe de les stocker comme variable, afinRa d'éviter les lags
IMAGES = {}

"""Les fonctions"""


# fonction qui associe les images aux pieces correspendantes
def load_images(img):
    pieces = ["bR", "bN", "bB", "bQ", "bK", "bP", "wR", "wN", "wB", "wQ", "wK", "wP"]
    for piece in pieces:
        img[piece] = p.transform.smoothscale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))


def load_reverse_images(img):
    pieces = ["bR", "bN", "bB", "bQ", "bK", "bP", "wR", "wN", "wB", "wQ", "wK", "wP"]
    for piece in pieces:
        if piece[0] == "w":
            img["b" + piece[1]] = p.transform.smoothscale(p.image.load(f"./images/{piece}.png"), (SQ_SIZE, SQ_SIZE))
        else:
            img["w" + piece[1]] = p.transform.smoothscale(p.image.load(f"./images/{piece}.png"), (SQ_SIZE, SQ_SIZE))

        # transform.smoothscale adapte l'image à la taille des cases de l'échiquier


# fontion de dessin de l echiquier
def drawBoard(window):
    # couleur on rgb
    global color
    light = (232, 235, 239)
    dark = (125, 135, 150)
    # list des couleurs de l'echequier
    colors = [light, dark]

    # Insérer du texte
    FONT = p.font.Font(None, 23)

    # liste des lettres de marquages de colonnes
    alpha_list = ["a", "b", "c", "d", "e", "f", "g", "h"]
    # alpha_list.reverse()
    # list_num =[i for i in range(1,DIMENSION+1)]

    # dessin des cases de l'échequier
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            # couleur les pair de blanc et l'impair de gris
            color = colors[((r + c) % 2)]

            # dessin des carrés sous forme de rectangle
            # Rect(left, top, width, height)
            p.draw.rect(window, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

            # précise la couleur et la chaine à afficher
            alpha = FONT.render(alpha_list[c], True, colors[c % 2])

            # positionne l'alphabet dans la dernière ligne de l'échiquier
            window.blit(alpha, (SQ_SIZE * (c + 1) - (DIMENSION + 2), WIDTH - 15))
            # blit(source,(colonne,ligne))

        # positionne les nbres dans la premiere case de chaque colonne
        nbr = FONT.render(str(DIMENSION - r), True, color)
        window.blit(nbr, (0, r * SQ_SIZE + 5))

    # necessaire pour la mis a jour de l affichage chaque fois qqchose change
    # p.display.update()


def drawPieces(window, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":  # piece != d une case vide
                window.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def drawState(window, gs):
    drawBoard(window)
    high_light_King(window, gs)
    drawPieces(window, gs.board)


def draw_available_moves(window, moveList):
    # s = p.Surface((SQ_SIZE, SQ_SIZE),p.SRCALPHA)
    # s.set_alpha(5)
    # s.fill((255, 255, 204))
    for move in moveList:
        if len(move) > 0:
            r = move[0]
            c = move[1]
            # p.draw.rect(window, BLUE, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
            p.draw.circle(window, (133, 193, 233), (c * SQ_SIZE + SQ_SIZE // 2, r * SQ_SIZE + SQ_SIZE // 2),
                          SQ_SIZE // 7)
            # window.blit(s, (c * SQ_SIZE, r * SQ_SIZE))
            p.display.update()


def high_light_piece(window, r, c, board):
    p.draw.rect(window, (133, 193, 233), p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
    window.blit(IMAGES[board[r][c]], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
    p.display.update()


def high_light_King(window, gs):
    red = "#ED0800"
    if gs.inCheck:
        if gs.whiteToMove:
            r = gs.whiteKinglocation[0]
            c = gs.whiteKinglocation[1]
        else:
            r = gs.blackKinglocation[0]
            c = gs.blackKinglocation[1]
        p.draw.rect(window, red, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def end_game_text(window, text):
    s = p.Surface((WIDTH, WIDTH))
    s.set_alpha(100)
    s.fill((200, 200, 200))
    window.blit(s, (0, 0))
    FONT = p.font.Font(None, 70)
    TEXT = FONT.render(text, True, p.Color("Black"))
    textLocation = p.Rect(0, 0, WIDTH, WIDTH).move(WIDTH // 2 - TEXT.get_width() // 2, WIDTH // 3)
    window.blit(TEXT, textLocation)

    FONT = p.font.Font(None, 40)
    TEXT = FONT.render("R to Reset", True, p.Color("Black"))
    textLocation = p.Rect(0, 0, WIDTH, WIDTH).move(WIDTH // 2 - TEXT.get_width() // 2, WIDTH // 2)
    window.blit(TEXT, textLocation)


def get_draw_move(valid_moves, startSq, draw_moves):
    for moves in valid_moves:
        if moves.startSq == startSq:
            draw_moves.append(moves.endSq)
    draw_move = list(OrderedDict.fromkeys(draw_moves))
    return draw_move


def reset(gs):
    while gs.moveLog:
        gs.undoMove()
    gs.checkMate = False
    gs.staleMate = False


"""Fonction definissant une partie d'échec"""


def main(mode=True):
    global draw_moves
    draw_moves = []
    load_images(IMAGES)
    # La fenetre elle-meme
    WIN = p.display.set_mode((WIDTH, WIDTH))
    p.display.set_caption("Chess Game")

    # variable utiliser pour la FPS
    clock = p.time.Clock()

    # objet de class gameState
    gs = ChessEngine.gameState()
    # gs.whiteToMove = False
    valid_moves = gs.getValidMoves()
    # inCheck, Checks, pins = gs.checkForPinsAndChecks()
    moveMade = False  # flag pour génerer des nouveaux mvts juste au cas le joueur a effectué un movt valide

    # chargement des images des pieces

    # constante de la boucle principale
    run = True

    # historique des cliques
    sqSelected = ()  # va prendre la ligne et la colonne de la case choisie
    playerClicks = []  # va contenir la position initial et terminal de la piece

    # les joueurs
    if mode:
        playerOne = True  # True si le joueurs est humains / False s'il n'est pas
        playerTwo = True
    else:
        playerOne = True# True si le joueurs est humains / False s'il n'est pas
        playerTwo = False

    # variable indiquant la fin d'une partie
    game_over = False

    # boucle principale
    while run:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        clock.tick(FPS)
        # responsable de l ouverture et fermeture de la fenetre
        for event in p.event.get():
            if event.type == p.QUIT:
                run = False
            # gestion des cliques souris
            elif event.type == p.MOUSEBUTTONDOWN:
                # la position de la souris (colonne,ligne) sur l'échiquier
                if p.mouse.get_pressed()[0]:
                    if not game_over and humanTurn:
                        location = p.mouse.get_pos()
                        col = location[0] // SQ_SIZE  # colonne de l'échiquier
                        row = location[1] // SQ_SIZE  # ligne de l'échiquier
                        if gs.board[row][col] != "--":
                            high_light_piece(WIN, row, col, gs.board)
                        get_draw_move(valid_moves, (row, col), draw_moves)
                        if sqSelected == (row, col):
                            sqSelected = ()
                            playerClicks = []
                            draw_moves = []
                        else:
                            sqSelected = (row, col)
                            playerClicks.append(sqSelected)
                            # cas de sélection d'une case vide comme case de depart
                            if gs.board[playerClicks[0][0]][playerClicks[0][1]] == "--":
                                sqSelected = ()
                                playerClicks = []
                        if len(playerClicks) == 2:  # responsable du déplacement des pieces
                            # réception des cases choisies par le joueur
                            move = Move(playerClicks[0], playerClicks[1], gs.board)
                            # réalisation du mouvement
                            # if gs.whiteToMove:
                            for i in range(len(valid_moves)):
                                if move == valid_moves[i]:
                                    if move.isPawnPromotion:
                                        gs.piece_promo = promotion(move.endRow, move.endCol)
                                    gs.makeMove(valid_moves[i])
                                    print(move.getChessNotation())
                                    moveMade = True
                            sqSelected = ()
                            playerClicks = []
                            draw_moves = []
            elif event.type == p.KEYDOWN:
                if event.key == p.K_z:
                    gs.undoMove()
                    gs.checkMate = False
                    gs.staleMate = False
                    game_over = False
                    moveMade = True

                elif event.key == p.K_r and game_over:
                    reset(gs)
                    draw_moves = []
                    sqSelected = ()
                    playerClicks = []
                    game_over = False
                    moveMade = True
        if not game_over and not humanTurn:
            AImove =getRandomMove(valid_moves)
            gs.makeMove(AImove)
            print(AImove.getChessNotation())
            moveMade = True

        if moveMade:
            valid_moves = gs.getValidMoves()
            moveMade = False

        if draw_moves:
            draw_available_moves(WIN, draw_moves)
        else:
            drawState(WIN, gs)
            if gs.checkMate:
                if gs.whiteToMove:
                    end_game_text(WIN, "Black wins")
                    game_over = True
                else:
                    end_game_text(WIN, "White Wins")
                    game_over = True
            elif gs.staleMate:
                end_game_text(WIN, "Stalemate")
                game_over = True
            p.display.flip()


if __name__ == "__main__":
    main()
