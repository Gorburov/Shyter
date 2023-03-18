from random import randint
from time import time as timer
from pygame import *
font.init()
mixer.init()

w = 1200
h = 800

clock = time.Clock()
FPS = 60


window = display.set_mode((w,h),RESIZABLE)
display.set_caption('шутер')

mixer.music.load('son/space.ogg')
mixer.music.set_volume(0.1)
mixer.music.play()

shoot = mixer.Sound('son/fire.ogg')
shoot.set_volume(0.1)
back = transform.scale(image.load('image/galaxy.jpg'), (w, h))

font1 = font.Font(None, 30)
font_finish = font.Font(None, 150)

texst_lose = font_finish.render('You lose', True,(245,55,55))
texst_win = font_finish.render('You win', True,(55,255,55))
lost = 0
score = 0

text_lost = font1.render('Пропущенно:' + str(lost), True, (255, 255, 255))
text_score = font1.render('Рахунок:' + str(score), True, (255, 255, 255))

freeze_chance = 10

current_size = window.get_size()
virtual_surfase = Surface((w,h))


kd = 0

class GameSprite(sprite.Sprite):
    def __init__(self, sprite_image,x,y,w,h,speed):
        super().__init__()
        self.image = transform.scale(image.load(sprite_image), (w, h))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = speed

    def reset(self):
        virtual_surfase.blit(self.image,(self.rect.x, self.rect.y))

class Player(GameSprite):
    def __init__(self, x, y):
        super().__init__('image/air.png', x, y, 100, 120, 10)
        self.clip = 20
        self.guns = 1
        self.kd = 0
        self.hp = 3
        self.reload = False
        self.start_reload = 0

    def update_pos(self):
        global clip
        keys_pressed = key.get_pressed()

        if keys_pressed[K_a] and self.rect.x > 5:
            self.rect.x -= self.speed
        if keys_pressed[K_d] and self.rect.x < w - 105:
            self.rect.x += self.speed
        if (keys_pressed[K_SPACE] and self.kd < 0) and (self.clip >= 0 and not self.reload) :
            self.fire()
            shoot.play()
            self.kd = 7
            self.clip -= 1
            clip = clip[:-1]
        else:
            self.kd -= 1

        if self.clip == 0:
            self.reload = True
            self.clip = 20
            self.start_reload = timer()

        if self.reload:
            current_time = timer()
            if current_time - self.start_reload >= 2:
                self.reload = False
                bullet_x = 30
                for i in range(player.clip):
                    bullet = GameSprite('image/bullet.png',bullet_x, h - 60,20,40,0)
                    clip.append(bullet)
                    bullet_x +=20


    def fire(self):
        bullet = Bullet(self.rect.centerx -5,self.rect.top)
        bullets.add(bullet)
        if self.guns>2:
            bullet = Bullet(self.rect.x, self.rect.bottom-30)
            bullets.add(bullet)
        if self.guns>3:
            bullet = Bullet(self.rect.x+90, self.rect.bottom-30)
            bullets.add(bullet)

class Enemy(GameSprite):
    def __init__(self,x ,y):
        super().__init__('image/ufo.png',x,y,120,70,2)

    def update(self):
        global text_lost
        global lost
        self.rect.y += self.speed
        if self.rect.y >h:
            lost +=1
            self.rect.x = randint(0, w-120)
            self.rect.y = -70
            text_lost = font1.render('Пропущенно:' + str(lost), True, (255, 255, 255))


class Boss_ufo(GameSprite):
    hp_koef = 1

    def __init__(self,x,y,):
        Boss_ufo.hp_koef += 1
        super().__init__('image/ufo.png',x,y,240,140,1)
        self.hp = 7*Boss_ufo.hp_koef

    def update(self):
        global text_lost
        global lost
        self.rect.y += self.speed
        if self.rect.y > h:
            lost += 3
            self.kill()
            text_lost = font1.render('Пропущенно:' + str(lost), True, (255, 255, 255))


class Bullet(GameSprite):
    def __init__(self,x,y):
        super().__init__('image/bullet.png',x,y,10,30,10)

    def update(self):
        self.rect.y -= self.speed
        if self.rect.y <= -30:
            self.kill()


class Bonus(GameSprite):
    def __init__(self, sprite_image,x,y):
        super().__init__(sprite_image,x,y,40,40,1)

    def update(self):
        self.rect.y += self.speed
        if self.rect.y >= h:
            self.kill()

class Asteroidd(GameSprite):
    def __init__(self):
        super().__init__('image/asteroid.png',randint(0,w-40), randint(-h,-40), 80,80,3)

    def update(self):
        self.rect.y += self.speed
        if self.rect.y >= h :
            self.rect.x = randint(0,w - 40)
            self.rect.y = randint(-h, -40)


player = Player((w - 100)//2, h - 150)

monsters = sprite.Group()
for i in range(10):
    monster = Enemy(randint(0, w - 120), randint(-h, -70))
    monsters.add(monster)

health = []
health_x = 20
for i in range(player.hp):
    heart = GameSprite('image/health.png',health_x,80,50,50,0)
    health.append(heart)
    health_x += 60

clip = []
bullet_x = 30
for i in range(player.clip):
    bullet = GameSprite('image/bullet.png',bullet_x,h-60,20,40,0)
    clip.append(bullet)
    bullet_x += 20

bullets = sprite.Group()
bonuses = sprite.Group()
asteroids = sprite.Group()
for i in range(3):
    asteroid = Asteroidd()
    asteroids.add(asteroid)

bonus_freeze=0
bonus_gun = 0
bonus_backup = 0
giga_monster = 0

def freezing():
    global unfreeze
    global freeze
    for enemy in monsters:
        enemy.speed = 0
    freeze = True
    unfreeze = 60

game = True
unfreeze = 0
freeze = False
finish = False


while game:


    for e in event.get():
        if e.type == QUIT:
            game = False
        if e.type == VIDEORESIZE:
            current_size = e.size
        if e.type == KEYDOWN:
            if e.key == K_ESCAPE:
                game = False

    if freeze:
        if unfreeze >= 0:
            unfreeze -=1
        else:
            for enemy in monsters:
                enemy.speed = 2
            freeze= False
    if not finish:
        virtual_surfase.blit(back,(0,0))

        player.update_pos()
        player.reset()

        monsters.update()
        monsters.draw(virtual_surfase)

        asteroids.update()
        asteroids.draw(virtual_surfase)

        bonuses.update()
        bonuses.draw(virtual_surfase)

        if giga_monster:
            giga_monster.update()
            giga_monster.reset()
            boos_hit = sprite.spritecollide(giga_monster,bullets,True)
            if sprite.collide_rect(player,giga_monster):
                player.hp -= 2
                health = health[:-1]
                health = health[:-1]
                giga_monster = 0

            if len(boos_hit ) != 0:
                giga_monster.hp -= 1
                if giga_monster.hp <=0:
                    score +=3
                    player.hp +=1
                    health_x = 20 + 60 *(player.hp - 1)
                    heart = GameSprite('image/health.png', health_x, 80, 50, 50, 0)
                    health.append(heart)
                    chance = randint(0,100)
                    if chance <= 60:
                        if not bonus_gun:
                            bonus_gun = Bonus('image/gun_bonus.png',
                                              giga_monster.rect.centerx - 20, giga_monster.rect.bottom)
                            bonuses.add(bonus_gun)
                        giga_monster = 0
                    else:
                        if not bonus_backup:
                            bonus_backup = Bonus("image/backup.png",
                                                 giga_monster.rect.centerx - 20, giga_monster.rect.bottom)
                            bonuses.add(bonus_backup)
                        giga_monster = 0

        else:
            if score % 20 and score != 0:
                giga_monster = Boss_ufo(randint(0, w -240), randint(-h, -140))
        bullets.update()
        bullets.draw(virtual_surfase)
        crush_list = sprite.spritecollide(player, monsters, False)
        crush_list_asteroids = sprite.spritecollide(player, asteroids, False)
        dead_monsters = sprite.groupcollide(monsters, bullets, False, True)
        hit_asteroids = sprite.groupcollide(asteroids, bullets, False, True)
        for monster in dead_monsters:
            score += 1
            text_score = font1.render("Раxунoк: " + str(score), True, (255, 255, 255))
            chance = randint(0, 100)
            if chance <= freeze_chance:
                if not bonus_freeze:
                    bonus_freeze = Bonus("image/freez.png", monster.rect.centerx - 20, monster.rect.bottom)
                    bonuses.add(bonus_freeze)
            monster.rect.x = randint(0, w- 120)
            monster.rect.y = randint(-h, -70)
        if len(crush_list) != 0:
            for monster in crush_list:
                 monster.rect.x = randint(0, w - 120)
                 monster.rect.y = randint(-h, -70)
                 player.hp -= 1
                 health = health[:-1]
        if len(crush_list_asteroids) != 0:
            for asteroid in crush_list_asteroids:
                asteroid.rect.x = randint(0, w - 40)
                asteroid.rect.y = randint(-h, -40)
                player.hp -= 1
                health = health[:-1]
        if lost >= 100 or player.hp <= 0:
            finish = True
            virtual_surfase.blit(texst_lose, (350, 300))
        if score >= 100:
            finish = True
            virtual_surfase.blit(texst_win, (350, 300))
        if bonus_freeze:
            if sprite.collide_rect(player, bonus_freeze):
                freezing()
                bonus_freeze.rect.x = 100
                bonus_freeze = 0
        if bonus_backup:
            if sprite.collide_rect(player, bonus_backup):
                lost = 1
                bonus_backup.rect.x = - 100
                bonus_backup = 0
                text_lost = font1.render('Пропушено:' + str(lost), True, (255, 255, 255))
        if bonus_gun:

            if sprite.collide_rect(player, bonus_gun):
                player.guns += 2
                bonus_gun.rect.x = -200
                bonus_gun = 0

        virtual_surfase.blit(text_lost, (20, 20))
        virtual_surfase.blit(text_score, (20, 50))
        for heart in health:
            heart.reset()
        for bullet in clip:
            bullet.reset()
        scaled_surface = transform.scale(virtual_surfase, current_size)
        window.blit(scaled_surface, (0, 0))
    display.update()
    clock.tick(FPS)

