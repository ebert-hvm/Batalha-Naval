from client import Client
from grid import Grid
import pygame
import sys
import time

# Constantes
SCREEN_WIDTH, SCREEN_HEIGHT = 1305, 660

# Cores
WHITE = (255, 255, 255)
DARK_BLUE = (4, 58, 122)
LIGHT_BLUE = (132, 189, 255)
BLUE = (27, 91, 166)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)

# Estados do Jogo
MENU, LOADING, GAME_SETUP, GAME_WAITING_FOR_OPPONENT, GAME_PLAY, GAME_END = range(6)

# Inicialização do Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Batalha Naval')

# Variáveis do Jogo
game_state = MENU
button_continue = False

# Dimensões e posições
GRID_TOP_LEFT = (50, 100)
GRID_CELL_SIZE = 50
GRID_ROWS = 10
GRID_COLS = 10
SHIP_AREA = (GRID_TOP_LEFT[0] + GRID_CELL_SIZE*GRID_COLS + 50, GRID_TOP_LEFT[1])
SHIP_WIDTH = 40
SHIP_HEIGHT = GRID_CELL_SIZE
rotate_button_position = (SHIP_AREA[0], SHIP_AREA[1] + GRID_CELL_SIZE * (GRID_ROWS + 1))
rotate_button_dimensions = (200, 50)
PLAYER_BOARD_TOP_LEFT = GRID_TOP_LEFT
ENEMY_BOARD_TOP_LEFT = ((SCREEN_WIDTH / 2) + 20, GRID_TOP_LEFT[1])



class Button:
    def __init__(self, text, width, height, pos, font_size, bg_color, fg_color):
        self.text = text
        self.width = width
        self.height = height
        self.position = pos
        self.font_size = font_size
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.rect = pygame.Rect(pos[0], pos[1], width, height)

    def draw(self, win):
        pygame.draw.rect(win, self.bg_color, self.rect)
        font = pygame.font.Font(None, self.font_size)
        text = font.render(self.text, True, self.fg_color)
        text_rect = text.get_rect(center=self.rect.center)
        win.blit(text, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


class Ship:
    def __init__(self, size, position, horizontal=True):
        self.size = size
        self.selected = False
        self.position = position
        self.positioned = False
        self.original_position = position
        self.horizontal = horizontal
        self.rects = self.create_rects()
    def getShape(self):
        pos = [((x - PLAYER_BOARD_TOP_LEFT[i]) // GRID_CELL_SIZE) for i, x in enumerate(self.position)]
        if self.horizontal:
            return pos + [self.size, 1]
        else:
            return pos + [1, self.size]
    def create_rects(self):
        rects = []
        for i in range(self.size):
            x = self.position[0] + (i * GRID_CELL_SIZE if self.horizontal else 0)
            y = self.position[1] + (i * GRID_CELL_SIZE if not self.horizontal else 0)
            rects.append(pygame.Rect(x, y, GRID_CELL_SIZE, GRID_CELL_SIZE))
        return rects

    def draw(self, win):
        for rect in self.rects:
            pygame.draw.rect(win, DARK_BLUE, rect)

    def rotate(self):
        self.horizontal = not self.horizontal
        self.rects = self.create_rects()

    def set_position(self, pos):
        self.position = pos
        self.original_position = pos
        self.rects = self.create_rects()

def draw_menu():
    global game_state

    font = pygame.font.Font(None, 54)
    title_text = font.render('Batalha Naval', True, (0, 0, 0))
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH / 2, 100))

    start_button = Button("Iniciar", 150, 50, (SCREEN_WIDTH / 2 - 75, 250), 36, (0, 128, 0), (255, 255, 255))

    screen.fill(LIGHT_BLUE)
    screen.blit(title_text, title_rect)
    start_button.draw(screen)


    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            if start_button.is_clicked(event.pos):
                game_state = LOADING


def draw_loading(client):
    global game_state
    font = pygame.font.Font(None, 36)
    text = font.render('Procurando adversário...', True, (0, 0, 0))
    text_rect = text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 30))

    loading_dots = ''
    max_dots = 3
    start_time = time.time()
    while game_state == LOADING:
        client.execute()
        if(client.getState() != Client.CONNECTION):
            game_state = GAME_SETUP

        screen.fill(LIGHT_BLUE)
        screen.blit(text, text_rect)
        # Animação de pontos de carregamento
        current_time = time.time()
        if current_time - start_time >= 0.5:  # Atualiza os pontos a cada 0.5 segundos
            loading_dots = loading_dots + '.' if len(loading_dots) < max_dots else ''
            start_time = current_time

        loading_dots_text = font.render(loading_dots, True, (0, 0, 0))
        loading_dots_rect = loading_dots_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
        screen.blit(loading_dots_text, loading_dots_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                client.closeSocket()
                pygame.quit()
                sys.exit()
        pygame.display.flip()
        pygame.time.delay(100)  # Pequeno atraso para reduzir o uso da CPU



def draw_grid(board_top_left):
    font = pygame.font.Font(None, 36)
    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            rect = pygame.Rect(board_top_left[0] + col * GRID_CELL_SIZE,
                               board_top_left[1] + row * GRID_CELL_SIZE,
                               GRID_CELL_SIZE, GRID_CELL_SIZE)
            pygame.draw.rect(screen, BLACK, rect, 1)
            if row == 0:
                num_text = font.render(str(col + 1), True, BLACK)
                screen.blit(num_text, (rect.x + 15, rect.y - 30))
            if col == 0:
                letter_text = font.render(chr(65 + row), True, BLACK)
                screen.blit(letter_text, (rect.x - 30, rect.y + 10))


def initialize_ships(config={
        "gridSize": 10,
        "shipsNumber": 5,
        "shipsShape": [[5,1],[4,1],[4,1],[3,1],[3,1],[3,1],[2,1],[2,1],[2,1],[2,1]]
    }):
    global GRID_ROWS
    global GRID_COLS
    GRID_ROWS = GRID_COLS = config['gridSize']
    # Define o espaçamento entre navios do mesmo tipo e entre tipos diferentes
    horizontal_spacing = 10
    vertical_spacing = 60

    # Posição inicial para o primeiro navio
    start_x = SHIP_AREA[0]
    start_y = SHIP_AREA[1]

    # Cria uma lista para armazenar os navios
    ships = []

    # Posições iniciais de cada tipo de navio
    positions = {
        5: (start_x, start_y),
        4: (start_x, start_y + vertical_spacing),
        3: (start_x, start_y + 2 * vertical_spacing),
        2: (start_x, start_y + 3 * vertical_spacing),
        1: (start_x, start_y + 4 * vertical_spacing)
    }

    # Tamanhos dos navios e quantas vezes cada um aparece
    ship_sizes = {}
    for pair in config['shipsShape']:
        size = pair[0]
        if size in ship_sizes:
            ship_sizes[size] += 1
        else:
            ship_sizes[size] = 1


    for size, count in ship_sizes.items():
        for i in range(count):
            position = positions[size][0] + i * (size * GRID_CELL_SIZE + horizontal_spacing), positions[size][1]
            ship = Ship(size, position, horizontal=True)
            ships.append(ship)

    for ship in ships:
        ship.original_position = ship.position  # Armazena a posição inicial
    return ships

def draw_ships(ships, board_top_left):
    for ship in ships:
        if ship.positioned:  # Certifique-se de desenhar apenas navios posicionados
            for rect in ship.rects:
                # Desenha o retângulo do navio ajustado para a posição do tabuleiro
                ship_rect = pygame.Rect(board_top_left[0] + (rect.x - board_top_left[0]),
                                        board_top_left[1] + (rect.y - board_top_left[1]),
                                        rect.width, rect.height)
                pygame.draw.rect(screen, DARK_BLUE, ship_rect)


def draw_continue_button(enabled=True):
    font = pygame.font.Font(None, 36)
    button_color = BLUE if enabled else GRAY
    margin = 20  # Margem em relação ao lado direito da tela
    button_width = SCREEN_WIDTH - SHIP_AREA[0] - margin * 2  # Largura do botão com base na largura da tela e margens
    button_height = 50  # Altura do botão

    # Calcula a posição x mantendo a margem à direita
    button_x = SHIP_AREA[0] + margin
    # Mantém uma margem na parte inferior da tela para a posição y do botão
    button_y = GRID_TOP_LEFT[1] + GRID_CELL_SIZE * GRID_ROWS - button_height

    button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
    pygame.draw.rect(screen, button_color, button_rect)

    # Renderiza o texto "CONTINUAR" centrado no botão
    text = font.render('CONTINUAR', True, WHITE if enabled else BLACK)
    text_rect = text.get_rect(center=button_rect.center)
    screen.blit(text, text_rect)

    return button_rect


def draw_game_setup(board_top_left):
    screen.fill(LIGHT_BLUE)
    draw_grid(board_top_left)
    draw_ships(ships, board_top_left)
    draw_continue_button(True)

def is_valid_position(ship, ships):
    # Esta função assume que o 'ship' já está posicionado onde o jogador quer colocá-lo.
    for rect in ship.rects:
        # Verifica se o navio está dentro dos limites do tabuleiro
        if not (GRID_TOP_LEFT[0] <= rect.x < GRID_TOP_LEFT[0] + GRID_CELL_SIZE * GRID_COLS and
                GRID_TOP_LEFT[1] <= rect.y < GRID_TOP_LEFT[1] + GRID_CELL_SIZE * GRID_ROWS):
            return False

        # Verifica a proximidade de outros navios
        for other_ship in ships:
            if other_ship == ship:
                continue  # Ignora a verificação do próprio navio e dos navios não posicionados
            for other_rect in other_ship.rects:
                # Verifica se algum rect do 'ship' está em um dos rects inflados de 'other_ship'
                if rect.colliderect(other_rect.inflate(GRID_CELL_SIZE, GRID_CELL_SIZE)):
                    return False
    return True


def snap_to_grid(pos):
    grid_x = ((pos[0] - GRID_TOP_LEFT[0]) // GRID_CELL_SIZE) * GRID_CELL_SIZE + GRID_TOP_LEFT[0]
    grid_y = ((pos[1] - GRID_TOP_LEFT[1]) // GRID_CELL_SIZE) * GRID_CELL_SIZE + GRID_TOP_LEFT[1]
    return grid_x, grid_y

def all_ships_positioned(ships):
    return all(ship.positioned for ship in ships)


def handle_ship_placement(event, ships, selected_ship, original_positions):
    if event.type == pygame.MOUSEBUTTONDOWN:
        for ship in ships:
            # Verifica se o clique foi em cima de algum dos rects do navio
            if any(rect.collidepoint(event.pos) for rect in ship.rects):
                selected_ship = ship
                selected_ship.selected = True
                # Salva a posição original do navio
                original_positions[ship] = ship.position
                break

    elif event.type == pygame.MOUSEBUTTONUP and selected_ship:
        selected_ship.selected = False
        # Encaixa o navio na grade mais próxima do tabuleiro
        ship_center = selected_ship.rects[0].center  # Pega o centro do primeiro rect como referência
        new_position = snap_to_grid(ship_center)
        selected_ship.set_position(new_position)
        if not is_valid_position(selected_ship, ships):
            # Posição inválida, retorna o navio para sua posição original fora do tabuleiro
            selected_ship.set_position(original_positions[selected_ship])
            selected_ship.positioned = False  # O navio não está corretamente posicionado
        else:
            selected_ship.positioned = True  # O navio está corretamente posicionado
        selected_ship = None

    elif event.type == pygame.MOUSEMOTION and selected_ship and selected_ship.selected:
        # Segue o movimento do mouse
        mouse_x, mouse_y = event.pos
        offset_x = mouse_x - selected_ship.rects[0].width // 2
        offset_y = mouse_y - selected_ship.rects[0].height // 2
        selected_ship.set_position((offset_x, offset_y))

    return selected_ship


selected_ship = None


def draw_rotate_button(screen, enabled=True):
    font = pygame.font.Font(None, 36)
    button_color = BLUE
    margin = 20  # Margem em relação ao lado direito da tela
    button_width = 250  # Largura menor para o botão de rotação
    button_height = 50  # Altura do botão

    # Posição x e y mantendo as margens
    button_x = SHIP_AREA[0] + margin
    button_y = GRID_TOP_LEFT[1] + GRID_CELL_SIZE * GRID_ROWS - button_height - margin - button_height  # Acima do botão CONTINUAR

    button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
    pygame.draw.rect(screen, button_color, button_rect)

    # Renderiza o texto "ROTACIONAR" centrado no botão
    text = font.render('ROTACIONAR', True, WHITE)
    text_rect = text.get_rect(center=button_rect.center)
    screen.blit(text, text_rect)

    return button_rect  # Retorna o retângulo do botão para detecção de clique


rotate_button_rect = None


def draw_waiting_for_opponent_screen(ships):
    screen.fill(LIGHT_BLUE)  # Define a cor de fundo da tela de espera
    draw_grid(PLAYER_BOARD_TOP_LEFT)  # Desenha o tabuleiro
    draw_ships(ships, PLAYER_BOARD_TOP_LEFT)  # Desenha os navios na posição final do GAME_SETUP

    # Adicione o texto de espera à direita do tabuleiro
    font = pygame.font.Font(None, 36)
    waiting_text = font.render('Esperando adversário...', True, BLACK)
    text_rect = waiting_text.get_rect(center=(SCREEN_WIDTH/2 + SCREEN_WIDTH/4, SCREEN_HEIGHT/2))
    screen.blit(waiting_text, text_rect)

def draw_hatched_rect(surface, color, rect):
    surface.fill(color, rect)
    num_lines = 8  # Number of hatch lines
    for i in range(num_lines):
        pygame.draw.line(surface, LIGHT_BLUE, rect.topleft, rect.bottomright, 2)
        rect.topleft = rect.topleft[0], rect.topleft[1] + GRID_CELL_SIZE // num_lines

def draw_game_play_screen(client):
    # Limpa a tela
    screen.fill(LIGHT_BLUE)
    font = pygame.font.Font(None, 30)
    if client.myTurn():
        txt = 'Sua vez:'
    else:
        txt = 'Vez do oponente:'
    title_text = font.render(txt, True, (0, 0, 0))
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH / 2, 50))
    screen.blit(title_text, title_rect)
    draw_grid(PLAYER_BOARD_TOP_LEFT)
    draw_grid(ENEMY_BOARD_TOP_LEFT)
    playerGrid, enemyGrid = client.getGrids()
    for y, row in enumerate(playerGrid):
        for x, el in enumerate(row):
            square_rect = pygame.Rect(PLAYER_BOARD_TOP_LEFT[0] + x * GRID_CELL_SIZE,
                            PLAYER_BOARD_TOP_LEFT[1] + y * GRID_CELL_SIZE,
                            GRID_CELL_SIZE, GRID_CELL_SIZE)
            if el == Grid.EMPTY:
                continue
            elif el == Grid.SHIP:
                pygame.draw.rect(screen, DARK_BLUE, square_rect)
            elif el == Grid.REVEALED_SHIP:
                draw_hatched_rect(screen, DARK_BLUE, square_rect)
            elif el == Grid.HIT:
                pygame.draw.rect(screen, DARK_BLUE, square_rect)
                pygame.draw.line(screen, (255, 0, 0), square_rect.topleft, square_rect.bottomright, 3)
                pygame.draw.line(screen, (255, 0, 0), square_rect.bottomleft, square_rect.topright, 3)
            elif el == Grid.MISS:
                pygame.draw.rect(screen, (0,0,255), square_rect)

    for y, row in enumerate(enemyGrid):
        for x, el in enumerate(row):
            square_rect = pygame.Rect(ENEMY_BOARD_TOP_LEFT[0] + x * GRID_CELL_SIZE,
                            ENEMY_BOARD_TOP_LEFT[1] + y * GRID_CELL_SIZE,
                            GRID_CELL_SIZE, GRID_CELL_SIZE)
            if el == Grid.EMPTY:
                continue
            elif el == Grid.REVEALED_SHIP:
                draw_hatched_rect(screen, DARK_BLUE, square_rect)
            elif el == Grid.HIT:
                pygame.draw.line(screen, (255, 0, 0), square_rect.topleft, square_rect.bottomright, 3)
                pygame.draw.line(screen, (255, 0, 0), square_rect.bottomleft, square_rect.topright, 3)
            elif el == Grid.MISS:
                pygame.draw.rect(screen, (0,0,255), square_rect)
                
    # draw_ships(ships, PLAYER_BOARD_TOP_LEFT)
    # draw_hits_and_misses(enemy_attacks, PLAYER_BOARD_TOP_LEFT)

    # # Desenha o tabuleiro do inimigo sem os navios, mas com os ataques do jogador
    # draw_grid(ENEMY_BOARD_TOP_LEFT)
    # draw_hits_and_misses(player_attacks, ENEMY_BOARD_TOP_LEFT)


def handle_board_click(pos, board_top_left, attacks):
    grid_x = (pos[0] - board_top_left[0]) // GRID_CELL_SIZE
    grid_y = (pos[1] - board_top_left[1]) // GRID_CELL_SIZE

    # Verifica se o clique foi dentro do tabuleiro
    if 0 <= grid_x < GRID_COLS and 0 <= grid_y < GRID_ROWS:
        if (grid_x, grid_y) not in attacks:  # Não pode atacar a mesma célula duas vezes
            # Determina se é um hit ou miss
            is_hit = enemy_board[grid_y][grid_x] == 'ship'  # Suponha que você tenha uma representação do tabuleiro inimigo
            attacks[(grid_x, grid_y)] = 'hit' if is_hit else 'miss'
            return is_hit
    return None


player_attacks = {}  # Registra os ataques do jogador ao tabuleiro inimigo
enemy_attacks = {}  # Registra os ataques do inimigo ao tabuleiro do jogador
enemy_board = [[0] * GRID_COLS for _ in range(GRID_ROWS)]
hits = set()  # Acertos no tabuleiro do adversário
misses = set()  # Erros no tabuleiro do adversário


def draw_hits_and_misses(attacks, board_top_left):
    attacks = {(0,0): 'hit',(9,9):'miss'}
    for (x, y), result in attacks.items():
        rect = pygame.Rect(board_top_left[0] + x * GRID_CELL_SIZE,
                           board_top_left[1] + y * GRID_CELL_SIZE,
                           GRID_CELL_SIZE, GRID_CELL_SIZE)
        if result == 'hit':
            pygame.draw.line(screen, (255, 0, 0), rect.topleft, rect.bottomright, 3)
            pygame.draw.line(screen, (255, 0, 0), rect.bottomleft, rect.topright, 3)
        elif result == 'miss':
            pygame.draw.rect(screen, (0, 0, 255), rect)


def register_attack(pos, board_top_left, client):
    # Converte a posição do clique para coordenadas do grid
    grid_x = int(pos[0] - board_top_left[0]) // GRID_CELL_SIZE
    grid_y = int(pos[1] - board_top_left[1]) // GRID_CELL_SIZE

    # Verifica se o clique foi dentro do tabuleiro do inimigo
    if 0 <= grid_x < GRID_COLS and 0 <= grid_y < GRID_ROWS:
        client.makeMove(grid_x, grid_y)

game_result = 'defeat'


def draw_game_end_screen(result):
    screen.fill(LIGHT_BLUE)  # Define a cor de fundo para a tela de final de jogo

    # Define a fonte e o tamanho do texto
    font = pygame.font.Font(None, 90)
    if result:
        end_text = font.render('VITÓRIA!', True, (2,93,0))
    else:
        end_text = font.render('DERROTA...', True, (255, 8, 8))

    # Centraliza o texto na tela
    text_rect = end_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
    screen.blit(end_text, text_rect)

    # Calcula a posição dos botões
    button_width = 200
    button_height = 50
    button_spacing = 30  # Espaçamento entre os botões
    total_button_width = (button_width * 2) + button_spacing
    first_button_x = (SCREEN_WIDTH - total_button_width) // 2
    button_y = SCREEN_HEIGHT // 2 + 100

    # Define os botões
    menu_button = Button("Menu Principal", button_width, button_height, (first_button_x, button_y), 36, BLUE, WHITE)
    revanche_button = Button("Revanche", button_width, button_height,
                             (first_button_x + button_width + button_spacing, button_y), 36, BLUE, WHITE)

    # Desenha os botões na tela
    menu_button.draw(screen)
    revanche_button.draw(screen)

    return menu_button, revanche_button  # Retorna os botões para verificar os cliques fora desta função

def reset_ship_positions(ships):
    for ship in ships:
        ship.set_position(ship.original_position)
        ship.positioned = False


client = Client()
# Loop Principal
ships = []
original_positions = {}
# game_state = GAME_PLAY
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            client.closeSocket()
            pygame.quit()
            sys.exit()

        if game_state == GAME_SETUP:
            temp_ship = handle_ship_placement(event, ships, selected_ship, original_positions)
            if temp_ship is not None:
                selected_ship = temp_ship  # Atualiza o último navio selecionado

            if rotate_button_rect and event.type == pygame.MOUSEBUTTONDOWN:
                if rotate_button_rect.collidepoint(event.pos) and selected_ship:
                    # Rotaciona o último navio selecionado
                    selected_ship.rotate()
                    # Verifica se a nova posição é válida após a rotação
                    if not is_valid_position(selected_ship, ships):
                        # Se não for válida, desfaz a rotação
                        selected_ship.rotate()

            if event.type == pygame.MOUSEBUTTONDOWN and button_continue_rect.collidepoint(event.pos) and all_ships_positioned(ships):
                # O jogador pressionou o botão "Continuar", muda para a tela de espera do adversário
                shapes = [ship.getShape() for ship in ships]
                print(shapes)
                client.finishSetup(shapes)
                game_state = GAME_WAITING_FOR_OPPONENT

        if game_state == GAME_PLAY:
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                # Verifica se o clique foi no tabuleiro do inimigo
                if ENEMY_BOARD_TOP_LEFT[0] <= pos[0] <= ENEMY_BOARD_TOP_LEFT[0] + GRID_CELL_SIZE * GRID_COLS and \
                        ENEMY_BOARD_TOP_LEFT[1] <= pos[1] <= ENEMY_BOARD_TOP_LEFT[1] + GRID_CELL_SIZE * GRID_ROWS:
                    register_attack(pos, ENEMY_BOARD_TOP_LEFT, client)

        if game_state == GAME_END:
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if menu_button.is_clicked(pos):
                    reset_ship_positions(ships)  # Reseta a posição dos navios
                    game_state = MENU  # Volta para o menu principal
                elif revanche_button.is_clicked(pos):
                    reset_ship_positions(ships)  # Reseta a posição dos navios
                    game_state = GAME_SETUP  # Inicia uma nova partida

    screen.fill(LIGHT_BLUE)

    if game_state == MENU:
        draw_menu()
    elif game_state == LOADING:
        draw_loading(client)
        ships = initialize_ships(client.getConfig())
        original_positions = {ship: ship.position for ship in ships}
    elif game_state == GAME_SETUP:
        draw_game_setup(PLAYER_BOARD_TOP_LEFT)

        if selected_ship and selected_ship.selected:
            # Obtenha a posição atual do mouse
            mouse_x, mouse_y = pygame.mouse.get_pos()
            # Centraliza o navio no cursor do mouse
            offset_x = mouse_x - selected_ship.rects[0].width // 2
            offset_y = mouse_y - selected_ship.rects[0].height // 2
            # Atualiza a posição do navio para seguir o mouse
            selected_ship.set_position((offset_x, offset_y))

        button_continue = all_ships_positioned(ships)

        draw_grid(PLAYER_BOARD_TOP_LEFT)  # Desenha o tabuleiro
        button_continue_rect = draw_continue_button(button_continue)  # Desenha o botão "CONTINUAR"
        rotate_button_rect = draw_rotate_button(screen, selected_ship is not None and selected_ship.selected)

        # Redesenha todos os navios após movê-los
        for ship in ships:
            ship.draw(screen)

    elif game_state == GAME_WAITING_FOR_OPPONENT:
        draw_waiting_for_opponent_screen(ships)
        client.execute()
        # print(client.getState() + " " + Client.GAME)
        if client.getState() == Client.GAME:
            game_state = GAME_PLAY

    elif game_state == GAME_PLAY:
        client.execute()
        draw_game_play_screen(client)
        if client.getState() == Client.END:
            game_state = GAME_END

    elif game_state == GAME_END:
        menu_button, revanche_button = draw_game_end_screen(client.haveIWon())

    pygame.display.flip()
