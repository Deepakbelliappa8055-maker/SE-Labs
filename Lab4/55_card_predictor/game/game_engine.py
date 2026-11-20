import pygame
from game.deck import Deck

BASE_POINTS = 10
MAX_MULTIPLIER = 5
REVEAL_MS = 1200


class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.deck = Deck()

        self.current_card = self.deck.draw()
        self.next_card = None
        self.score = 0
        self.streak = 0
        self.best_streak = 0
        self.status_msg = "Will the next card be HIGHER or LOWER?"
        self.status_color = (220, 220, 220)

        # Reveal state: while revealing, both cards are shown side by side
        # and clicks are ignored until the timer runs out.
        self.revealing = False
        self.reveal_until = 0

        btn_w, btn_h = 140, 48
        self.btn_higher = pygame.Rect(width // 2 - btn_w - 20, height - 72, btn_w, btn_h)
        self.btn_lower = pygame.Rect(width // 2 + 20, height - 72, btn_w, btn_h)

        self.font_title = pygame.font.SysFont(None, 40)
        self.font_medium = pygame.font.SysFont(None, 30)
        self.font_small = pygame.font.SysFont(None, 24)

    @property
    def multiplier(self):
        """Multiplier the next correct guess will earn (x1 .. x5)."""
        return min(self.streak + 1, MAX_MULTIPLIER)

    def evaluate_guess(self, guess):
        """Draws next card and evaluates prediction."""
        self.next_card = self.deck.draw()
        new_rank = self.next_card.numeric_rank
        old_rank = self.current_card.numeric_rank
        shown = f"{self.next_card.rank_str} vs {self.current_card.rank_str}"

        if new_rank == old_rank:
            # Tie: neither higher nor lower, so keep score and streak.
            self.status_msg = f"PUSH! {shown} - score and streak kept"
            self.status_color = (240, 200, 90)
        else:
            if guess == "HIGHER":
                correct = new_rank > old_rank
            else:
                correct = new_rank < old_rank

            if correct:
                mult = self.multiplier
                gained = BASE_POINTS * mult
                self.score += gained
                self.streak += 1
                self.best_streak = max(self.best_streak, self.streak)
                self.status_msg = f"CORRECT! {shown}  +{gained} (x{mult})"
                self.status_color = (80, 220, 80)
            else:
                self.score = max(0, self.score - BASE_POINTS)
                self.streak = 0
                self.status_msg = f"WRONG! {shown}  -{BASE_POINTS}, streak reset"
                self.status_color = (235, 75, 75)

        self.revealing = True
        self.reveal_until = pygame.time.get_ticks() + REVEAL_MS

    def handle_event(self, event):
        if self.revealing:
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.btn_higher.collidepoint(event.pos):
                self.evaluate_guess("HIGHER")
            elif self.btn_lower.collidepoint(event.pos):
                self.evaluate_guess("LOWER")

    def update(self):
        if self.revealing and pygame.time.get_ticks() >= self.reveal_until:
            self.current_card = self.next_card
            self.next_card = None
            self.revealing = False

    def _draw_button(self, screen, rect, label, color):
        if self.revealing:
            color = tuple(c // 2 for c in color)
        pygame.draw.rect(screen, color, rect, border_radius=8)
        pygame.draw.rect(screen, (220, 220, 220), rect, width=2, border_radius=8)
        surf = self.font_medium.render(label, True, (255, 255, 255))
        screen.blit(surf, (rect.centerx - surf.get_width() // 2, rect.centery - surf.get_height() // 2))

    def render(self, screen):
        screen.fill((25, 80, 45))

        title_surf = self.font_title.render("High-Low Card Predictor", True, (245, 245, 245))
        screen.blit(title_surf, (self.width // 2 - title_surf.get_width() // 2, 20))

        score_surf = self.font_medium.render(f"Score: {self.score}", True, (255, 220, 80))
        screen.blit(score_surf, (30, 60))
        streak_surf = self.font_small.render(
            f"Streak: {self.streak}  (next x{self.multiplier})   Best: {self.best_streak}",
            True, (230, 230, 230))
        screen.blit(streak_surf, (30, 88))

        rem_surf = self.font_small.render(f"Deck: {self.deck.remaining} left", True, (210, 210, 210))
        screen.blit(rem_surf, (self.width - rem_surf.get_width() - 30, 64))

        card_w, card_h = 130, 180
        top = 118
        if self.revealing and self.next_card is not None:
            gap = 40
            left_x = self.width // 2 - card_w - gap // 2
            right_x = self.width // 2 + gap // 2
            self.current_card.render(screen, left_x, top, card_w, card_h)
            self.next_card.render(screen, right_x, top, card_w, card_h)
            for x, label in ((left_x, "Previous"), (right_x, "New card")):
                lab = self.font_small.render(label, True, (230, 230, 230))
                screen.blit(lab, (x + card_w // 2 - lab.get_width() // 2, top + card_h + 6))
        else:
            self.current_card.render(screen, self.width // 2 - card_w // 2, top, card_w, card_h)

        status_surf = self.font_small.render(self.status_msg, True, self.status_color)
        screen.blit(status_surf, (self.width // 2 - status_surf.get_width() // 2, top + card_h + 32))

        self._draw_button(screen, self.btn_higher, "HIGHER", (40, 140, 60))
        self._draw_button(screen, self.btn_lower, "LOWER", (170, 50, 50))
