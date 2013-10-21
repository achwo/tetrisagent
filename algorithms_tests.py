import algorithms
import unittest


class BotTest(unittest.TestCase):

    def setUp(self):
        self.bot = algorithms.Bot()
        self.bot.training = self.training
        self.bot.trainings_done = 0

    def test_runs_training_function(self):
        self.bot.has_run = False

        self.bot.training_episodes = 1

        self.bot.run()
        self.assertEqual(1, self.bot.trainings_done)

    def test_runs_training_function_n_times(self):
        n = 1000

        self.bot.training_episodes = n
        self.bot.run()
        self.assertEqual(n, self.bot.trainings_done)

    def training(self):
        self.bot.trainings_done += 1


if __name__ == '__main__':
    unittest.main()