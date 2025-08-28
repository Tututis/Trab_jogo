import pygame
import sys
import random

pygame.init()

# Tela
LARGURA, ALTURA = 800, 600
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Mapa Vertical de Plataformas")

# Cores
AMARELO  = (112, 123, 47)
VERDE  = (50, 200, 50)
VERMELHO = (200, 50, 50)

# Fonte
fonte_titulo = pygame.font.SysFont("arial", 40, bold=True)
fonte_sub    = pygame.font.SysFont("arial", 28)
fonte_pontos = pygame.font.SysFont("arial", 24)

# Jogador
player_w, player_h = 50, 50
gravidade = 0.8
forca_pulo = -20
speed = 5

# Carrega os sprites
background = pygame.image.load("assets/Backmenu.png").convert()
background = pygame.transform.scale(background, (LARGURA, ALTURA))
sprite_idle = pygame.image.load("assets/Idle.png").convert_alpha()
sprite_jump = pygame.image.load("assets/Jump.png").convert_alpha()
sprites_run = [
    pygame.image.load(f"assets/Walk{i}.png").convert_alpha()
    for i in range(1, 5)
]

# Variáveis
player_x = player_y = 0
vel_x = vel_y = 0
no_chao = False
plataformas = []
camera_offset_y = 0
anim_index = 0
anim_timer = 0
anim_velocidade = 8

# Pontuação
pontuacao = 0
recorde = 0

clock = pygame.time.Clock()

def reset_game():
    global player_x, player_y, vel_x, vel_y, no_chao, plataformas, camera_offset_y, pontuacao

    player_x = LARGURA // 2
    player_y = ALTURA - 100
    vel_x, vel_y = 0, 0
    no_chao = False
    camera_offset_y = 0
    pontuacao = 0

    # Cálculo do alcance vertical e horizontal
    tempo_subida = abs(forca_pulo) / gravidade
    tempo_total = tempo_subida * 2
    alcance_h = speed * tempo_total * 1.3  # dificuldade aumentada
    alcance_v = abs(forca_pulo) * 1.5 * 8   # dificuldade aumentada

    plataformas = []
    y_atual = ALTURA - 50
    x_atual = LARGURA // 2
    plataformas.append(pygame.Rect(x_atual - 100, y_atual, 200, 20))

    for _ in range(100):
        if random.random() < 0.3:
            largura_plat = random.randint(80, 100)
        else:
            largura_plat = random.randint(100, 160)

        dist_y = random.randint(70, int(alcance_v))
        nova_y = y_atual - dist_y

        min_x = max(50, x_atual - int(alcance_h))
        max_x = min(LARGURA - largura_plat - 50, x_atual + int(alcance_h))
        nova_x = random.randint(min_x, max_x)

        plataformas.append(pygame.Rect(nova_x, nova_y, largura_plat, 20))
        y_atual = nova_y
        x_atual = nova_x

    return plataformas

estado = "menu"  # menu, jogo, gameover

while True:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

            if estado == "menu":
                if evento.key == pygame.K_RETURN:
                    plataformas = reset_game()
                    estado = "jogo"

            elif estado == "jogo":
                if evento.key == pygame.K_SPACE and -2 <= vel_y <= 2:
                    vel_y = forca_pulo

            elif estado == "gameover":
                if evento.key == pygame.K_RETURN:
                    plataformas = reset_game()
                    estado = "jogo"

    if estado == "menu":
        tela.blit(background, (0, 0))
        txt1 = fonte_titulo.render("Enter para iniciar", True, AMARELO)
        txt2 = fonte_sub.render("Esc para sair", True, AMARELO)
        tela.blit(txt1, txt1.get_rect(center=(LARGURA//2, ALTURA//2 - 10)))
        tela.blit(txt2, txt2.get_rect(center=(LARGURA//2, ALTURA//2 + 35)))

    elif estado == "jogo":
        teclas = pygame.key.get_pressed()
        vel_x = 0
        if teclas[pygame.K_LEFT]:
            vel_x = -speed
        if teclas[pygame.K_RIGHT]:
            vel_x = speed

        vel_y += gravidade
        player_x += vel_x
        player_y += vel_y

        no_chao = False
        player_rect = pygame.Rect(player_x, player_y, player_w, player_h)
        for plat in plataformas:
            if player_rect.colliderect(plat) and player_rect.bottom <= plat.bottom:
                player_y = plat.top - player_h
                vel_y = 0
                no_chao = True

        altura_atual = ALTURA - player_y
        pontuacao = max(pontuacao, int(altura_atual // 10))

        if player_y - camera_offset_y > ALTURA:
            recorde = max(recorde, pontuacao)
            estado = "gameover"

        if player_y - camera_offset_y < ALTURA // 3:
            camera_offset_y = player_y - ALTURA // 3

        tela.blit(background, (0, 0))
        for plat in plataformas:
            pygame.draw.rect(tela, VERDE, (plat.x, plat.y - camera_offset_y, plat.width, plat.height))
        if not no_chao:
            sprite_atual = sprite_jump
        elif vel_x != 0:
            anim_timer += 1
            if anim_timer >= anim_velocidade:
                anim_timer = 0
                anim_index = (anim_index + 1) % len(sprites_run)
            sprite_atual = sprites_run[anim_index]
        else:
            sprite_atual = sprite_idle
        if vel_x < 0:
            sprite_atual = pygame.transform.flip(sprite_atual, True, False)
        tela.blit(sprite_atual, (player_x, player_y - camera_offset_y))

        txt_pontos = fonte_pontos.render(f"Pontos: {pontuacao}", True, AMARELO)
        tela.blit(txt_pontos, (20, 20))

    elif estado == "gameover":
        tela.blit(background, (0, 0))
        txt1 = fonte_titulo.render("GAME OVER", True, VERMELHO)
        txt2 = fonte_sub.render(f"Pontos: {pontuacao}", True, AMARELO)
        txt3 = fonte_sub.render(f"Recorde: {recorde}", True, AMARELO)
        txt4 = fonte_sub.render("Enter para reiniciar", True, AMARELO)
        txt5 = fonte_sub.render("Esc para sair", True, AMARELO)

        tela.blit(txt1, txt1.get_rect(center=(LARGURA//2, ALTURA//2 - 60)))
        tela.blit(txt2, txt2.get_rect(center=(LARGURA//2, ALTURA//2 - 20)))
        tela.blit(txt3, txt3.get_rect(center=(LARGURA//2, ALTURA//2 + 10)))
        tela.blit(txt4, txt4.get_rect(center=(LARGURA//2, ALTURA//2 + 50)))
        tela.blit(txt5, txt5.get_rect(center=(LARGURA//2, ALTURA//2 + 85)))

    pygame.display.flip()
    clock.tick(60)
