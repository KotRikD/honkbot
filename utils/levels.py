levels = '''Рекрут
Знаток
Любитель букв
Хикка
Геймер чата
Мифическое существо'''.splitlines()

class xputils():
    #ripple-osu level calculation xD
    @staticmethod
    async def getRequiredScoreForLevel(level):
        """
        Return score required to reach a level
        :param level: level to reach
        :return: required score
        """
        if level >= 2:
            return int(48 / 3 * (4 * (level ** 3) - 3 * (level ** 2) - level))
        elif level <= 0 or level == 1:
            return 1  # Should be 0, but we get division by 0 below so set to 1

    @staticmethod
    async def getLevel(totalScore):
        """
        Return level from totalScore
        :param totalScore: total score
        :return: level
        """
        level = 1
        while True:
            # if the level is > 8000, it's probably an endless loop. terminate it.
            if level > 8000:
                return level

            # Calculate required score
            reqScore = await xputils.getRequiredScoreForLevel(level)

            # Check if this is our level
            if totalScore <= reqScore:
                # Our level, return it and break
                return level - 1
            else:
                # Not our level, calculate score for next level
                level += 1