from enum import IntEnum


def plural(word, count=2):
    """ Return the plural version the word if there is more than one count, otherwise return as is."""
    if count > 1:
        if word.endswith('sh'):
            return word + 'es'
        else:
            return word + 's'

    else:
        return word


class TimeUnit(IntEnum):
    SECOND = 1
    MINUTE = 60 * SECOND
    HOUR = 60 * MINUTE
    DAY = 24 * HOUR
    WEEK = 7 * DAY
    MONTH = 30 * DAY
    YEAR = 365 * DAY

    @property
    def seconds(self):
        return self.value

    @classmethod
    def duration(cls, seconds, first=True):
        """
        Constructs a human readable string to indicate the time duration for the given seconds

        :param int seconds:
        :param bool first: Just return the first unit instead of all
        :rtype: str
        """
        num_units = []

        for unit in reversed(TimeUnit):
            if seconds >= unit.seconds:
                name = unit.name.lower()
                count = int(seconds / unit.seconds)
                num_units.append(f'{count} {plural(name, count=count)}')
                seconds -= count * unit.seconds

                if first or not seconds:
                    break

        return ' '.join(num_units)
