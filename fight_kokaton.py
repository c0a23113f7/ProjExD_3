import os
import random
import sys
import time
import pygame as pg


WIDTH = 1100  # ゲームウィンドウの幅
HEIGHT = 650  # ゲームウィンドウの高さ
NUM_OF_BOMBS = 5  #爆弾の個数
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    """
    オブジェクトが画面内or画面外を判定し，真理値タプルを返す関数
    引数：こうかとんや爆弾，ビームなどのRect
    戻り値：横方向，縦方向のはみ出し判定結果（画面内：True／画面外：False）
    """
    yoko, tate = True, True
    if obj_rct.left < 0 or WIDTH < obj_rct.right:
        yoko = False
    if obj_rct.top < 0 or HEIGHT < obj_rct.bottom:
        tate = False
    return yoko, tate


class Bird:
    """
    ゲームキャラクター（こうかとん）に関するクラス
    """
    delta = {  # 押下キーと移動量の辞書
        pg.K_UP: (0, -5),
        pg.K_DOWN: (0, +5),
        pg.K_LEFT: (-5, 0),
        pg.K_RIGHT: (+5, 0),
    }
    img0 = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    img = pg.transform.flip(img0, True, False)  # デフォルトのこうかとん（右向き）
    imgs = {  # 0度から反時計回りに定義
        (+5, 0): img,  # 右
        (+5, -5): pg.transform.rotozoom(img, 45, 0.9),  # 右上
        (0, -5): pg.transform.rotozoom(img, 90, 0.9),  # 上
        (-5, -5): pg.transform.rotozoom(img0, -45, 0.9),  # 左上
        (-5, 0): img0,  # 左
        (-5, +5): pg.transform.rotozoom(img0, 45, 0.9),  # 左下
        (0, +5): pg.transform.rotozoom(img, -90, 0.9),  # 下
        (+5, +5): pg.transform.rotozoom(img, -45, 0.9),  # 右下
    }

    def __init__(self, xy: tuple[int, int]):
        """
        こうかとん画像Surfaceを生成する
        引数 xy：こうかとん画像の初期位置座標タプル
        """
        self.img = __class__.imgs[(+5, 0)]
        self.rct: pg.Rect = self.img.get_rect()
        self.rct.center = xy

    def change_img(self, num: int, screen: pg.Surface):
        """
        こうかとん画像を切り替え，画面に転送する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 screen：画面Surface
        """
        self.img = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 0.9)
        screen.blit(self.img, self.rct)

    def update(self, key_lst: list[bool], screen: pg.Surface):
        """
        押下キーに応じてこうかとんを移動させる
        引数1 key_lst：押下キーの真理値リスト
        引数2 screen：画面Surface
        """
        sum_mv = [0, 0]
        for k, mv in __class__.delta.items():
            if key_lst[k]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        self.rct.move_ip(sum_mv)
        if check_bound(self.rct) != (True, True):
            self.rct.move_ip(-sum_mv[0], -sum_mv[1])
        if not (sum_mv[0] == 0 and sum_mv[1] == 0):
            self.img = __class__.imgs[tuple(sum_mv)]
        screen.blit(self.img, self.rct)


class Beam:
    """
    こうかとんが放つビームに関するクラス
    """
    def __init__(self, bird:"Bird"):
        """
        ビーム画像Surfaceを生成する
        引数 bird：ビームを放つこうかとん（Birdインスタンス）
        """
        self.img = pg.image.load(f"fig/beam.png")
        self.rct = self.img.get_rect()
        self.rct.centery = bird.rct.centery  # こうかとんの中心縦座標
        self.rct.left = bird.rct.right  # こうかとんの右座標
        self.vx, self.vy = +5, 0

    def update(self, screen: pg.Surface):
        """
        ビームを速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        if check_bound(self.rct) == (True, True):
            self.rct.move_ip(self.vx, self.vy)
            screen.blit(self.img, self.rct)    


class Bomb:
    """
    爆弾に関するクラス
    """
    def __init__(self, color: tuple[int, int, int], rad: int):
        """
        引数に基づき爆弾円Surfaceを生成する
        引数1 color：爆弾円の色タプル
        引数2 rad：爆弾円の半径
        """
        self.img = pg.Surface((2*rad, 2*rad))
        pg.draw.circle(self.img, color, (rad, rad), rad)
        self.img.set_colorkey((0, 0, 0))
        self.rct = self.img.get_rect()
        self.rct.center = random.randint(0, WIDTH), random.randint(0, HEIGHT)
        self.vx, self.vy = +5, +5

    def update(self, screen: pg.Surface):
        """
        爆弾を速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        yoko, tate = check_bound(self.rct)
        if not yoko:
            self.vx *= -1
        if not tate:
            self.vy *= -1
        self.rct.move_ip(self.vx, self.vy)
        screen.blit(self.img, self.rct)
class Score:
    """
    ゲームのスコアを管理するクラス
    """
    def __init__(self):
        """
        スコアの初期化
        """
        self.fonto = pg.font.SysFont("hgp創英角ﾎﾟｯﾌﾟ体", 30)
        self.color = (0, 0, 255)  # スコア表示の文字色（青）
        self.score = 0  # スコア初期値
        self.img = self.fonto.render(f"Score: {self.score}", 0, self.color)
        self.rct = self.img.get_rect()
        self.rct.center = (100, HEIGHT - 50)  # 画面左下

    def add(self, amount:int):
        """
        スコアを加算する
        引数：加算するスコア
        """
        self.score += amount
        self.img = self.fonto.render(f"Score: {self.score}", 0, self.color)

    def update(self, screen:pg.Surface):
        """
        スコアを画面に表示
        """
        screen.blit(self.img, self.rct)


class Explosion:
    """
    爆発アニメーションを管理するクラス
    """
    def __init__(self, center: tuple[int, int], life: int = 20):
        """
        爆発アニメーションの初期化
        引数1 center: 爆発の中心座標 (爆弾の位置)
        引数2 life: 爆発の持続時間
        """
        # 爆発アニメーション用のSurfaceをロードし、リストに格納
        img = pg.image.load("fig/explosion.gif")
        self.images = [
            img,  # オリジナル
            pg.transform.flip(img, True, False),  # 左右反転
            pg.transform.flip(img, False, True),  # 上下反転
        ]
        self.rct = self.images[0].get_rect()
        self.rct.center = center
        self.life = life  # 爆発の持続時間
        self.image_index = 0  # 現在表示中の画像インデックス

    def update(self, screen: pg.Surface):
        """
        爆発アニメーションを描画し、時間を減算する
        引数 screen: 画面Surface
        """
        if self.life > 0:
            screen.blit(self.images[self.image_index], self.rct)
            self.life -= 1
            # チラつきを防ぐため、一定周期で画像を切り替え
            if self.life % 5 == 0:
                self.image_index = (self.image_index + 1) % len(self.images)

def main():
    pg.display.set_caption("たたかえ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))    
    bg_img = pg.image.load("fig/pg_bg.jpg")
    bird = Bird((300, 200))
    bombs = [Bomb((255, 0, 0), 10) for _ in range(NUM_OF_BOMBS)]  
    beams = []  # 複数ビームを管理するリスト
    explosions = []  # 爆発アニメーションを管理するリスト
    score = Score()  # スコアインスタンスの生成
    clock = pg.time.Clock()
    tmr = 0

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                # スペースキー押下でBeamクラスのインスタンス生成
                beams.append(Beam(bird))
                
        screen.blit(bg_img, [0, 0])
        
        # こうかとんと爆弾の衝突判定
        for bomb in bombs:
            if bird.rct.colliderect(bomb.rct):
                # ゲームオーバー時に，こうかとん画像を切り替え，1秒間表示させる
                bird.change_img(8, screen)
                fonto = pg.font.Font(None, 80)
                txt = fonto.render("Game Over", True, (255, 0, 0))
                screen.blit(txt, [WIDTH//2-150, HEIGHT//2])
                pg.display.update()
                time.sleep(1)
                return

        # ビームと爆弾の衝突判定
        remove_beams = []  # 削除対象のビームを記録
        remove_bombs = []  # 削除対象の爆弾を記録

        for beam in beams:
            for bomb in bombs:
                if beam.rct.colliderect(bomb.rct):  # ビームが爆弾を撃ち落とした場合
                    remove_beams.append(beam)  # 削除対象として記録
                    remove_bombs.append(bomb)  # 削除対象として記録
                    explosions.append(Explosion(bomb.rct.center))  # 爆発生成
                    score.add(1)  # スコア加算
                    bird.change_img(6, screen)
                    break  # 衝突があればそのビームの処理を終了

        # 記録されたビームと爆弾をリストから削除
        beams = [beam for beam in beams if beam not in remove_beams]
        bombs = [bomb for bomb in bombs if bomb not in remove_bombs]

        # ビームリストの更新（画面外のビームを除外）
        beams = [beam for beam in beams if check_bound(beam.rct) == (True, True)]

        # 各オブジェクトの描画と更新
        key_lst = pg.key.get_pressed()
        bird.update(key_lst, screen)

        for bomb in bombs:
            bomb.update(screen)
        for beam in beams:
            beam.update(screen)

        # 爆発の描画とリスト更新
        explosions = [exp for exp in explosions if exp.life > 0]
        for exp in explosions:
            exp.update(screen)

        score.update(screen)  # スコアのアップデート
        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()      