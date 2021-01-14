import random, pygame, sys

class Card(object):
    SUITS = ['Clubs', 'Diamonds', 'Hearts', 'Spades']
    RANKS = ['N/A', 'Ace', '2', '3', '4', '5', '6', '7',
             '8', '9', '10', 'Jack', 'Queen', 'King']

    def __init__(self, suit=0, rank=0):
        self.suit = suit
        self.rank = rank

    def __str__(self):
        return "{} of {}".format(Card.RANKS[self.rank], Card.SUITS[self.suit])

    #how the card images load into the game
    def load(self):
        card = pygame.image.load("cards2/" + Card.SUITS[self.suit].lower() + "_" + Card.RANKS[self.rank].lower() + ".png")#loads our images from a folder called cards
        small_card = pygame.transform.scale(card, (85,140))#scales the image down
        return small_card

class Deck(object):

    def __init__(self):
        self.cards = []
        for suit in range(4):
            for rank in range(1, 14):
                self.cards.append(Card(suit, rank))

    def __repr__(self):
        return "Hand(" + ", ".join([str(card) for card in self.cards]) + ")"

    def shuffle(self):
        random.shuffle(self.cards)

    def add_card(self, card):
        self.cards.append(card)

    def remove_card(self):
        return self.cards.pop(0)

    def deal(self, hand_1, hand_2):
        for two_cards in range(2):
            hand_1.add_card(self.remove_card())
            hand_2.add_card(self.remove_card())

class Hand(Deck):
    
    def __init__(self, name='', money=100):
        self.cards = []
        self.name = name
        self.money = money

    @property
    def total(self):
        hand_total = 0
        ace_count = 0
        for card in self.cards:
            if card.rank > 10:
                hand_total += 10
            elif card.rank == 1:
                hand_total += 11
                ace_count += 1
            else:    
                hand_total += card.rank

        while hand_total > 21 and ace_count > 0:
            hand_total -= 10
            ace_count -= 1 

        return hand_total

    #returns cards from hands back to deck
    def return_cards(self, deck):
        while len(self.cards) > 0:
            deck.add_card(self.remove_card())

class GameState(object):

    #screen settings
    size = width, height = 720, 540
    screen = pygame.display.set_mode(size)

    #different colors we use
    green = (71, 113, 72)
    light_green = (0, 255, 0)
    brass = (205, 149, 117)
    black = (0, 0, 0)

    clock = pygame.time.Clock() #setting up the frame rate

    #a game count tracker, might use this in the future
    game_count = 0

    #every game we load up will start as playing and have no outcome yet
    playing = True
    outcome = None

    def __init__(self):
        #raise the game count everytime we load up a game
        GameState.game_count += 1 
    
    def bet_screen(self, deck, player, dealer):
        bet = ''

        #size of fonts and what type of font
        bigfont = pygame.font.SysFont('Corbel', 100, True)
        mediumfont = pygame.font.SysFont('Corbel', 50, True)

        #different fonts used
        player_money_text = mediumfont.render('Your Balance: ' + str(player.money), True, self.brass)
        blackjack_text = bigfont.render('BLACKJACK', True, self.brass)
        place_bet_text = mediumfont.render('Place Bet:', True, self.brass)
        play_text = bigfont.render('PLAY', True, self.brass)
        bet_text = mediumfont.render(bet, True, self.brass)

        #x,y cords for fonts
        blackjack_text_x, blackjack_text_y = self.width/2 - blackjack_text.get_width()/2, self.height/6
        place_bet_text_x, place_bet_text_y = self.width/2 - place_bet_text.get_width()/2, self.height*(2/5) + 50
        player_money_text_x, player_money_text_y = self.width/2 - player_money_text.get_width()/2, self.height*(2/5) 

        while True:
            self.screen.fill(self.green)

            #bet font cords need to be updated when we type in more numbers
            bet_text_x, bet_text_y = self.width/2 - bet_text.get_width()/2, self.height*(2/5) + 100

            #play button dimensions
            #needs to come after bet text dimensions because it uses those values
            play_btn_width, play_btn_height = 300, 150
            play_btn_x, play_btn_y = self.width/2 - play_btn_width/2, bet_text_y + bet_text.get_height() + 10

            #play button
            play_btn = pygame.draw.rect(self.screen, self.light_green, [play_btn_x, play_btn_y, play_btn_width, play_btn_height]) #x,y,width, height(rect object)

            #x,y cords for play font
            play_text_x, play_text_y = play_btn.centerx - play_text.get_width()/2, play_btn.centery - play_btn_height/4

            #mouse positions
            mouse = pygame.mouse.get_pos()

            for event in pygame.event.get():
                #Quits the screen
                if event.type == pygame.QUIT: 
                    sys.exit()

                elif event.type == pygame.KEYDOWN:

                    #erases the last number
                    if event.key == pygame.K_BACKSPACE:
                        bet = bet[:-1] #returns all numbers but the last

                    #one way to start the game
                    elif event.key == pygame.K_RETURN:
                        if 0 < int(bet) <= player.money:
                            player.money -= int(bet) #take off the bet they placed
                            play_again, earnings = self.run_game(deck, player, dealer, int(bet)) #start game, and if they choose to play again/earnings
                            return play_again, earnings

                    else:
                        #checks if we type in a number, if not we ignore it
                        try:
                            if isinstance(int(event.unicode), int): #checks if we type in a number
                                bet += event.unicode

                        except:
                            pass

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    
                    #another way to start the game
                    if play_btn.left <= mouse[0] <= play_btn.right and play_btn.top <= mouse[1] <= play_btn.bottom:
                        try:
                            if 0 < int(bet) <= player.money:
                                player.money -= int(bet) #take off the bet they placed
                                play_again, earnings = self.run_game(deck, player, dealer, int(bet)) #start game, and if they choose to play again/earnings
                                return play_again, earnings
                        
                        #if we hit play without inputting a bet we get an error so we need a try and except
                        except ValueError:
                            pass

            #updated bet_text when user types in a number
            bet_text = mediumfont.render(bet, True, self.brass)

            #text that we are showing to the screen
            self.screen.blit(blackjack_text, (blackjack_text_x, blackjack_text_y))
            self.screen.blit(bet_text, (bet_text_x, bet_text_y))
            self.screen.blit(place_bet_text, (place_bet_text_x, place_bet_text_y))
            self.screen.blit(player_money_text, (player_money_text_x, player_money_text_y))
            self.screen.blit(play_text, (play_text_x, play_text_y))

            #update the frames of the game
            pygame.display.update()
            self.clock.tick(30) #frame rate
            

    
    #the parts that run the game
    def run_game(self, deck, player, dealer, bet):
        win, lose, draw = 'You Win!', 'You Lose!', 'Draw!'
        blackjack = False

        #Natural cases (Gets 21 off the first two cards)
        if player.total == 21:

            #is a draw state and bets are returned to player
            if dealer.total == 21:
                self.outcome = draw

            #otherwise the player wins and gets a blackjack and 1.5 their bet
            else:
                self.outcome = win
                blackjack = True

            self.playing = False

        elif dealer.total == 21:
            #player just loses here since we already checked if they have 21
            self.outcome = lose
            self.playing = False

        #font qualities for buttons
        smallfont = pygame.font.SysFont('Corbel', 20, True)
        mediumfont = pygame.font.SysFont('Corbel', 40, True)

        #creating words
        hit_text = smallfont.render('Hit', True, self.brass)
        stand_text = smallfont.render('Stand', True, self.brass)
        play_again_text = smallfont.render('Play Again', True, self.brass)
        
        #rectangle objects/buttons
        hit_btn = pygame.Rect(10, 110, 80, 30)
        stand_btn = pygame.Rect(10, 150, 80, 30)
        play_again_btn = pygame.Rect(10, 10, 100, 30)

        while True:

            #fills the screen a poker green
            self.screen.fill(self.green)

            player_x = 100 #used to track the position of the last card
            dealer_x = 100 
            dealer_first_card = True #Boolean used to check if this is the first card so its hidden

            #Display the hands of the dealer and the player
            for card in player.cards:
                self.screen.blit(card.load(), (player_x,100))
                player_x += 100
                
            for card in dealer.cards:
                #dealer card is hidden when player is playing
                if dealer_first_card == True and self.playing == True: #we need to have the dealer's first card hidden
                    back = pygame.image.load("cards2/back.png")
                    small_back = pygame.transform.scale(back, (85,140))
                    self.screen.blit(small_back, (dealer_x,300))
                    dealer_first_card = False

                #when game is over we flip the first card
                else:
                    self.screen.blit(card.load(), (dealer_x,300))
                dealer_x += 100

            mouse = pygame.mouse.get_pos()

            #drawing a rect object to be the space representing the buttons
            if self.playing == True:
                pygame.draw.rect(self.screen, self.light_green, hit_btn)
                pygame.draw.rect(self.screen, self.light_green, stand_btn)

            #show on screen if game is over
            #play again button and font being updated to screen
            if self.playing == False:
                pygame.draw.rect(self.screen, self.light_green, play_again_btn)
                self.screen.blit(play_again_text, (play_again_btn.centerx - play_again_text.get_width()/2, play_again_btn.centery - play_again_btn.height/4))
            
            #different event types that happen in the game
            for event in pygame.event.get():
                #quit the game
                if event.type == pygame.QUIT: 
                    sys.exit()

                #events that concern mouse clicks
                if event.type == pygame.MOUSEBUTTONDOWN:
                    
                    #mouse clicks that concern when the game is still being played
                    if self.playing == True:
                        #what happens when we click the hit button
                        if hit_btn.left <= mouse[0] <= hit_btn.right and hit_btn.top <= mouse[1] <= hit_btn.bottom:
                            player.add_card(deck.remove_card())

                            #checks if the player busts after we hit a card
                            if player.total > 21:
                                self.outcome = lose
                                self.playing = False
                                #Note: Technically we could hit stand here before things get updated but it should update fast enough it doesn't matter

                        #what happens when we click the stand button
                        if stand_btn.left <= mouse[0] <= stand_btn.right and stand_btn.top <= mouse[1] <= stand_btn.bottom:
                            #game ends when player hits stand, dealer must take its turn
                            self.playing = False 

                            #we have to code the dealer's moves here
                            #dealer must hit if he has less then 17
                            #dealer must also count the ace as 11 if the total is 17 or more but less then 21
                            while dealer.total < 17:
                                dealer.add_card(deck.remove_card())

                            #a bunch of cases that can happen after dealer and player play

                            #dealer busts
                            if dealer.total > 21:
                                self.outcome = win
                            
                            #player has a total greater then dealer and neither has busted
                            elif player.total > dealer.total and self.outcome == None:
                                self.outcome = win
                            
                            #dealer has a total greater then player and neither has busted
                            elif dealer.total > player.total and self.outcome == None:
                                self.outcome = lose

                            #player and dealer has the same total
                            elif dealer.total == player.total and self.outcome == None:
                                self.outcome = draw
                    
                    #mouse events that happen after the game has ended
                    if self.playing == False:
                        #what happens when we click the play again button 
                        if play_again_btn.left <= mouse[0] <= play_again_btn.right and play_again_btn.top <= mouse[1] <= play_again_btn.bottom:

                            #what they earn if they win
                            if self.outcome == win:
                                if blackjack:
                                    bet *= 2.5
                                else:
                                    bet *= 2

                            #if its a draw we return what they bet so nothing changes
                            elif self.outcome == draw:
                                pass

                            #if its a loss they earn no money back
                            elif self.outcome == lose:
                                bet = 0

                            return True, bet

            #placing the text on the buttons
            #show on screen if game is still playing
            if self.playing == True:
                self.screen.blit(hit_text, (hit_btn.centerx - hit_text.get_width()/2, hit_btn.centery - hit_btn.height/4))
                self.screen.blit(stand_text, (stand_btn.centerx - stand_text.get_width()/2, stand_btn.centery - stand_btn.height/4))

            if self.playing == False:
                outcome_text_x, outcome_text_y = play_again_btn.right + 20, play_again_btn.top
                outcome_text = mediumfont.render(self.outcome, True, self.brass)
                self.screen.blit(outcome_text, (outcome_text_x, outcome_text_y))
                pass 


            #update the frames of the game
            pygame.display.update()


#how the game runs with all the classes           

pygame.init()

test_deck = Deck()

player = Hand("Player")
dealer = Hand("Dealer")

play_again = True
while play_again:
    game = GameState()
    test_deck.shuffle()
    test_deck.deal(player, dealer)
    play_again, earnings = game.bet_screen(test_deck, player, dealer)
    player.money += earnings #add what they won (if they did) to their balance
    player.return_cards(test_deck)
    dealer.return_cards(test_deck)
    print(len(test_deck.cards))



