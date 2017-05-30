#!/usr/bin/python3
import unittest
import ladybug

class TestLadybug(unittest.TestCase):

    game = None


    #def setUp(self):


    def test_player_won(self):
        game = ladybug.setup_game(2)
        p1 = game['players'][0]
        self.assertFalse(ladybug.player_won(game['board'], p1))
        p1['position'] = 34
        self.assertTrue(ladybug.player_won(game['board'], p1))


    def test_move_player_with_mantis_card(self):
        game = ladybug.setup_game(2)
        p1 = game['players'][0]
        self.assertTrue(p1['position'] == 0)
        ladybug.move_player(game['board'], p1, 1)
        self.assertTrue(p1['position'] == 1)
        ladybug.move_player(game['board'], p1, -1)
        self.assertTrue(p1['position'] == 0)
        ladybug.move_player(game['board'], p1, 1)
        self.assertTrue(p1['position'] == 1)
        ladybug.move_player(game['board'], p1, 3)
        self.assertTrue(p1['position'] == 4)  # get mantis card
        ladybug.move_player(game['board'], p1, 1)
        self.assertTrue(p1['position'] == 5)
        ladybug.move_player(game['board'], p1, 1)
        self.assertTrue(p1['position'] == 13)
        ladybug.move_player(game['board'], p1, -3)
        self.assertTrue(p1['position'] == 10)
        ladybug.move_player(game['board'], p1, -3)
        self.assertTrue(p1['position'] == 7, p1['position'])  # passed the mantis going backwards
        ladybug.move_player(game['board'], p1, -2)
        self.assertTrue(p1['position'] == 5)
        ladybug.move_player(game['board'], p1, 4)
        self.assertTrue(p1['position'] == 9)  ## mantis, no card

    def test_move_player_without_mantis_card(self):
        game = ladybug.setup_game(2)
        p1 = game['players'][0]
        self.assertTrue(p1['position'] == 0)
        ladybug.move_player(game['board'], p1, 1)
        self.assertTrue(p1['position'] == 1)
        ladybug.move_player(game['board'], p1, 2)
        self.assertTrue(p1['position'] == 3)
        ladybug.move_player(game['board'], p1, 7)
        self.assertTrue(p1['position'] == 0)  # no mantis card, get sent back to start


    def test_move_player_gain_aphids(self):
        game = ladybug.setup_game(2)
        p1 = game['players'][0]
        p1['position'] = 16
        self.assertTrue(p1['position'] == 16)
        p1['aphids'] = 3
        self.assertTrue(p1['aphids'] == 3)
        ladybug.move_player(game['board'], p1, 1)
        self.assertTrue(p1['aphids'] == 1, p1['aphids'])

        p1['position'] = 16
        self.assertTrue(p1['position'] == 16)
        self.assertTrue(p1['aphids'] == 1)
        ladybug.move_player(game['board'], p1, 1)
        self.assertTrue(p1['aphids'] == 0, p1['aphids'])


    def test_move_player_lose_aphids(self):
        game = ladybug.setup_game(2)
        p1 = game['players'][0]
        p1['position'] = 2
        self.assertTrue(p1['position'] == 2)
        self.assertTrue(p1['aphids'] == 0)
        ladybug.move_player(game['board'], p1, 1)
        self.assertTrue(p1['aphids'] == 3)


    def test_move_past_ants_with_10_aphids(self):
        game = ladybug.setup_game(2)
        p1 = game['players'][0]
        p1['position'] = 25
        self.assertTrue(p1['position'] == 25)
        p1['aphids'] = 10
        self.assertTrue(p1['aphids'] == 10)

        # pass ants 1 square at a time
        ladybug.move_player(game['board'], p1, 1)
        self.assertTrue(p1['aphids'] == 0)
        self.assertTrue(p1['position'] == 26, p1['position'])  # must stop at ants for turn
        ladybug.move_player(game['board'], p1, 1)
        self.assertTrue(p1['position'] == 27)

        # pass ants multiple squares at a time, still must stop on ants
        p1['position'] = 25
        self.assertTrue(p1['position'] == 25)
        p1['aphids'] = 10
        self.assertTrue(p1['aphids'] == 10)
        print(ladybug.move_player(game['board'], p1, 2))
        self.assertTrue(p1['aphids'] == 0)
        self.assertTrue(p1['position'] == 26, p1['position'])  # must stop at ants for turn


    def test_move_past_ants_without_10_aphids(self):
        game = ladybug.setup_game(2)
        p1 = game['players'][0]
        # try to pass ants without enough aphids - land on ants
        p1['position'] = 25
        self.assertTrue(p1['position'] == 25)
        p1['aphids'] = 9
        self.assertTrue(p1['aphids'] == 9)
        print(ladybug.move_player(game['board'], p1, 1))
        self.assertTrue(p1['aphids'] == 9)
        self.assertTrue(p1['position'] == 26, p1['position'])  # must stop at ants for turn
        ladybug.move_player(game['board'], p1, 1)
        self.assertTrue(p1['position'] == 35, p1['position'])

        # try to pass ants without enough aphids - land on ants
        p1['position'] = 25
        self.assertTrue(p1['position'] == 25)
        p1['aphids'] = 0
        self.assertTrue(p1['aphids'] == 0)
        print(ladybug.move_player(game['board'], p1, 2))
        self.assertTrue(p1['aphids'] == 0)
        self.assertTrue(p1['position'] == 26, p1['position'])  # must stop at ants for turn
        self.assertTrue(p1['aphids'] == 0)
        ladybug.move_player(game['board'], p1, 1)
        self.assertTrue(p1['position'] == 35)


    def test_games_per_thread(self):
        x = ladybug.get_games_per_thread(1, 1)
        self.assertTrue(len(x) == 1)
        self.assertTrue(x[0] == 1, x[0])

        x = ladybug.get_games_per_thread(1, 2)
        self.assertTrue(len(x) == 2)
        self.assertTrue(x[0] == 1)
        self.assertTrue(x[1] == 0, x[1])

        x = ladybug.get_games_per_thread(2, 7)
        self.assertTrue(len(x) == 7)
        self.assertTrue(x[0] == 1)
        self.assertTrue(x[1] == 1, x[1])
        self.assertTrue(x[2] == 0, x[2])
        self.assertTrue(x[6] == 0, x[6])

        x = ladybug.get_games_per_thread(7, 3)
        self.assertTrue(len(x) == 3)
        self.assertTrue(x[0] == 3)
        self.assertTrue(x[1] == 2, x[1])
        self.assertTrue(x[2] == 2, x[2])


if __name__ == '__main__':
    unittest.main()
