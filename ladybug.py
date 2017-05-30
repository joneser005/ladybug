#!/usr/bin/python3
import argparse
import math
import pprint
import multiprocessing, queue
import random
import sys
import time

names = ['Ella Yellow', 'Olivia Orange', 'Rickey Red', 'Tommy Teal']


def run(threadID, threadName, shuffler, num_games, num_players, resultq):
    print ("{} START for {} games".format(threadName, num_games))
    results = {names[x]:0 for x in range(num_players)}
    for n in range(num_games):
        winner = play_game(shuffler, num_players)
        results[winner] = results[winner] + 1
        # print("{} winner:{}:{}".format(threadName, n, winner['name']))
        # threading.
    #   print('+')
    resultq.put(results)
    print ("Exiting " + threadName)


def shuffle_deck(shuffle):
    deck = ['a1', 'a2', 'a3', 'a3', 'a4', 'm-1', 'm-2', 'm-3', 'm-4r', 'm-4r',
            'm1', 'm1', 'm1', 'm1', 'm2', 'm2', 'm2', 'm2', 'm2r', 'm2r', 'm2r',
            'm2r', 'm3', 'm3', 'm3', 'm3', 'm3r', 'm3r', 'm3r', 'm4', 'm4', 'm4',
            'm4r', 'm4r', 'm5', 'm5', 'm6', 'm6']
    shuffle(deck)
    return deck

def setup_game(num_players, print_board=False):
    ''' Returns a game dict with an array of players, cards, and a board
    card legend:
            a{num} - gain {num} aphids
            m{num}[r] - move {num} squares.  If trailing 'r', go again.
    '''
    deck = ['a1', 'a2', 'a3', 'a3', 'a4', 'm-1', 'm-2', 'm-3', 'm-4r', 'm-4r',
            'm1', 'm1', 'm1', 'm1', 'm2', 'm2', 'm2', 'm2', 'm2r', 'm2r', 'm2r',
            'm2r', 'm3', 'm3', 'm3', 'm3', 'm3r', 'm3r', 'm3r', 'm4', 'm4', 'm4',
            'm4r', 'm4r', 'm5', 'm5', 'm6', 'm6']
    board = 'start 0 0 a3 mantiscard 0 slide13 0 mantiscard mantis-stop 0 0 0 a2 0 a5 0 a-2 0 0 m-2 0 0 a-1 0 0 ants-stop 0 lose-turn 0 0 0 lose-turn 0 finish 0 a1 0 a3 0 m-2 0 slide22'.split()
    if print_board:
        pprint.pprint([(x,y) for x,y in enumerate(board)])

    players = [{'player_num': p,
                'name': names[p],
                'aphids': 0, 'position': 0, 'mantis_cards': 0} for p in range(num_players)]
    return {'players': players, 'deck': deck, 'board': board}


def player_won(board, player):
    return player['position'] == 34


def append_move(moves, player, message):
    moves.append('{}: {}'.format(player['name'], message))
    return moves


def do_moves(board, player, m):
    moves = []
    step = 1 if m > 0 else -1

    # special ant check
    if player['position'] == 26 and 'aphids-paid' not in player.keys():  # if you got here going backwards, you won't have paid your aphids yet
        player['position'] = 35
        player.pop('aphids-paid', None)
        append_move(moves, player, 'Taking long way loop back to ants.....')
    else:
        for i in range(int(math.fabs(m))):
            if player['position'] < 0:
                player['position'] = 0  # start
            elif player['position'] < len(board)-1:  # if at end, stay there - it should slide/jump to elsewhere
                player['position'] += step

            current = board[player['position']]

            if current == 'start':
                append_move(moves, player, 'At start - move complete')
                break;
            elif current == 'finish':
                append_move(moves, player, 'At finish, game over!')
                break
            elif current == 'mantis-stop' and step > 0:
                append_move(moves, player, 'At Hydrandea Hideout - face the Mantis!')
                if player['mantis_cards'] > 0:
                    player['mantis_cards'] -= 1
                    append_move(moves, player, '... had mantis card!  Remaining: {}'.format(player['mantis_cards']))
                else:
                    player['position'] = 0
                    append_move(moves, player, '... no mantis card - go back to start!')
                    break
            elif current == 'ants-stop' and step > 0:
                append_move(moves, player, 'Face the Ants!  Pay 10 aphids!')
                if (player['aphids'] >= 10):
                    player['aphids'] -= 10
                    player['aphids-paid'] = True
                    append_move(moves, player, '... paid 10 aphids.  Remaining: {}'.format(player['aphids']))
                else:
                    if 'aphids-paid' in player.keys():
                        player.pop('aphids-paid', None)
                    moves.append('    Player does not have 10 aphids.')

                break;
            # else keep going
    return moves

def check_position(board, player, moves, m):
    # Now eval final landing square, skipping the cases handled in-flight (start, finish, mantis/ant stops)
    position = int(player['position'])
    square = board[position]
    # print('Debug2: position, square:', position, square)
    if (square in ['start', 'mantis-stop', 'ants-stop', 'lose-turn', 'finish']):
        append_move(moves, player, 'Landing position is a stop-square: {}'.format(square))
        pass
    elif 'mantiscard' == square:
        player['mantis_cards'] += 1
        append_move(moves, player, 'Acquired Mantis card')
    elif 'slide' in square:
        s = int(square[5:])
        # print('Debug: slide int is ', s)
        player['position'] = s
        append_move(moves, player, 'Moved to {}'.format(s))
    elif 'lose-turn' in square:
        # print('!!!!! TODO - lose-turn')
        append_move(moves, player, '!!!!! TODO - lose-turn')
    elif square[0] == 'a':
        player['aphids'] += int(square[1:])
        if player['aphids'] < 0:
            player['aphids'] = 0
        append_move(moves, player, 'Gained {} aphids'.format(int(square[1:])))
    elif square[0] == 'm':
        append_move(moves, player, 'Go back {} squares.'.format(int(square[2:])))  # Index 2 skips 'm-'
        append_move(moves, player, move_player(board, player, int(square[1:])))
    else:
        append_move(moves, player, 'Move {} squares, current position = {}:{}'.format(m, player['position'], board[player['position']]))
        pass

    return moves


def move_player(board, player, m):
    # print('ENTER move_player(board, player({},position={}), {})'.format(player['name'], player['position'], m))
    moves = do_moves(board, player, m)

    # print('EXIT move_player(board, player({},position={}), {})'.format(player['name'], player['position'], m))
    return check_position(board, player, moves, m)


def play_card(board, player, card):
    moves = []
    if card[0] == 'a':  # aphid card
        player['aphids'] = player['aphids'] + int(card[1:])
        append_move(moves, player, 'Gained {} aphids for a total of {}'.format(
                int(card[1:]), player['aphids']))
    elif card[0] == 'm':  # move card - ignore the trailing go-again indicator ('r') here
        m = int(card[1:len(card)-1] if card[-1] == 'r' else card[1:])
        moves.append(move_player(board, player, m))
    else:
        append_move(moves, player, '===== FAULT: card:' + card)

    return moves


def draw_card_and_play(board, moves, draw_pile, shuffler, player):
    if len(draw_pile) == 0:
        moves.append('Reshuffled deck')
        draw_pile = shuffle_deck(shuffler)

    card = draw_pile.pop()
    moves.append('@@@@@ CARD {}'.format(card))
    move = play_card(board, player, card)
    moves.append(move)
    # print(move)
    if player_won(board, player):
        return draw_pile, player

    winner = None
    if card[:-1] == 'r':
        append_move(moves, player, 'Go again!')
        draw_pile, winner = draw_card_and_play(draw_pile, player)

    return draw_pile, winner

def play_game(shuffler, num_players):
    game = setup_game(num_players)
    board = game['board']
    draw_pile = shuffle_deck(shuffler)
    players = game['players']
    moves = []
    winner = None
    while not winner:
        for player in players:
            draw_pile, winner = draw_card_and_play(board, moves, draw_pile, shuffler, player)
            if winner:
                break;

    # moves was for development and any future data capture
    # we aren't currently using, and no longer passing back to the caller
    # to keep memory requirements down when running large numbers of games
    moves.append('Winner: ' + winner['name'])
    return winner['name']


def play_games_singleproc(args):
    ''' single-threaded version '''
    print('(Single-threaded)')
    winners = {}
    for i in range(args.num_games):
        winner = play_game(random.shuffle, args.num_players)
        x = winners.get(winner, 0)
        winners[winner] = x+1
    return winners


def print_player(player):
    print('===== PLAYER: ', player['name'], ': ', end='');
    for key in sorted(player.keys()):
        print(key, '=', player[key], '; ', end='')
    print()


def get_games_per_thread(num_games, num_threads):
    games_per_thread = []
    n = int(num_games / num_threads)
    n_remainder = num_games % num_threads
    # print('Input: ', num_games, num_threads)
    # print('n:', n, '   n_remainder: ', n_remainder)
    for x in range(num_threads):
        # print('x=',x,': ',n+1 if x < n_remainder else n)
        games_per_thread.append(n+1 if x < n_remainder else n)

    return games_per_thread


def parse_cli_args():
    parser = argparse.ArgumentParser(description='Ladybug game inputs')
    parser.add_argument('-p', '--num_players', type=int, default=2,
                        help='number of players, 2+')
    parser.add_argument('-n', '--num_games', type=int, default=1,
                        help='Number of games to play, default=1')
    parser.add_argument('-t', '--num_threads', type=int, default=0,   # def zero so we can still run one thread in multithreaded version
                        help='Number of threads to use, default=1')

    args = parser.parse_args()
    print("Number of players:", args.num_players)
    print("Number of games:", args.num_games)
    print("Number of threads:", args.num_threads)
    return args


def main():
    args = parse_cli_args()
    if args.num_threads == 0:
        winners = play_games_singleproc(args)
        print('===== Results: ', winners)
    else:
        winners = {}
        # resultq = queue.Queue()
        resultq = multiprocessing.Queue()
        games_per_thread = get_games_per_thread(args.num_games, args.num_threads)
        threads = []
        for n, num_games in enumerate(games_per_thread):
            if num_games == 0: continue
            # Create new threads
            p = multiprocessing.Process(target=run, args=(n, "Thread-"+str(n), random.shuffle, num_games, args.num_players, resultq,))
            threads.append(p)

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        print('Threads done.  Collecting results.....')
        while not resultq.empty():
            try:
                winner = resultq.get_nowait()
                # print(winner)
                for p, n in winner.items():
                    winners[p] = winners.get(p, 0) + n
            except queue.Empty:
                pass
            # print('-', end='')

        print('===== Results: ', winners)
        # pprint.pprint(winners)

if __name__ == "__main__":
    main()
