import re
import datetime


class Formatter:
    def __init__(self):
        self.convertors = {
            # TR1
            'datedoteu': self.c_datedoteu,
            'datedotus':self.c_datedotus,
            'datelonguk':self.c_datelonguk,
            'datelongus':self.c_datelongus,
            'dateshortuk':self.c_dateshortuk,
            'dateshortus':self.c_dateshortus,
            'dateslasheu':self.c_dateslasheu,
            'dateslashus':self.c_dateslashus,
            'datelongdaymonthuk':self.c_datelongdaymonthuk,
            'datelongmonthdayus':self.c_datelongmonthdayus,
            'dateshortdaymonthuk':self.c_dateshortdaymonthuk,
            'dateshortmonthdayus':self.c_dateshortmonthdayus,
            'dateslashdaymontheu':self.c_dateslashdaymontheu,
            'dateslashmonthdayus':self.c_dateslashmonthdayus,
            'datelongyearmonth':self.c_datelongyearmonth,
            'dateshortyearmonth':self.c_dateshortyearmonth,
            'datelongmonthyear':self.c_datelongmonthyear,
            'dateshortmonthyear':self.c_dateshortmonthyear,
            'numcomma':self.c_numcomma,
            'numcommadot':self.c_numcommadot,
            'numdash':self.c_numdash,
            'numdotcomma':self.c_numdotcomma,
            'numspacecomma':self.c_numspacecomma,
            'numspacedot':self.c_numspacedot,
            # TR2

            'datemonthdayyearen': self.c_datemonthdayyearen,
            'numdotdecimal': self.c_numdotdecimal,
            'zerodash': self.c_zerodash,
            # SEC
            'duryear': self.c_sec_duryear,
            'durmonth': self.c_sec_durmonth,
            'durweek': self.c_sec_durweek,
            'durday': self.c_sec_durday,
            'durhour': self.c_sec_durhour,
            'durwordsen': self.c_sec_durwordsen,
            'numwordsen': self.c_sec_numwordsen,
            'datequarterend': self.c_sec_datequarterend,
            'boolballotbox': self.c_sec_boolballotbox,
            'exchnameen': self.c_sec_exchnameen,
            'stateprovnameen': self.c_sec_stateprovnameen,
            'countrynameen': self.c_sec_countrynameen,
            'edgarprovcountryen': self.c_sec_edgarprovcountryen,
            'entityfilercategoryen': self.c_sec_entityfilercategoryen
        }
        self.sec_states = {
            'alabama': 'AL', 'alaska': 'AK', 'arizona': 'AZ', 'arkansas': 'AR', 'california': 'CA',
            'colorado': 'CO', 'connecticut': 'CT', 'delaware': 'DE', 'florida': 'FL', 'georgia': 'GA',
            'hawaii': 'HI', 'idaho': 'ID', 'illinois': 'IL', 'indiana': 'IN', 'iowa': 'IA',
            'kansas': 'KS', 'kentucky': 'KY', 'louisiana': 'LA', 'maine': 'ME', 'maryland': 'MD',
            'massachusetts': 'MA', 'michigan': '', 'MI': '', 'minnesota': 'MN', 'mississippi': 'MS',
            'missouri': 'MO', 'montana': 'MT', 'nebraska': 'NE', 'nevada': 'NV', 'new hampshire': 'NH',
            'new jersey': 'NJ', 'new mexico': 'NM', 'new york': 'NY', 'north carolina': 'NC', 'north dakota': 'ND',
            'ohio': 'OH', 'oklahoma': 'OK', 'oregon': 'OR', 'pennsylvania': 'PA', 'rhode island': 'RI',
            'south carolina': 'SC', 'south dakota': 'SD', 'tennessee': 'TN', 'texas': 'TX', 'utah': 'UT',
            'vermont': 'VT', 'virginia': 'VA', 'washington': 'WA', 'west virginia': 'WV', 'wisconsin': 'WI',
            'wyoming': 'WY'
        }
        self.en_months_short = {
            'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
            'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12}
        self.en_months_long = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6,
            'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12}
        self.zerodash_chars = ['-', '-', '-', '֊', '־', '‐', '‑', '‒', '–', '—', '―', '﹘', '﹣', '－']

    def apply_format(self, v, f):
        method = self.convertors.get(f)
        if not method and ':' in f:
            method = self.convertors.get(f.split(':')[1])
        if method:
            t = method(v)
            return t[0] if t and t[0] else v  # First member of the tuple
        else:
            return v  # TODO: Give a message if there is an error

    def c_datemonthdayyearen(self, v):
        p = '(January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr' \
            '|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC|JANUARY|FEBRUARY|MARCH' \
            '|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER)[^0-9]+[0-9]{1,2}[^0-9]+([0-9]{1,' \
            '2}|[0-9]{4}) '
        if not re.fullmatch(p, v):
            return None, f'Value {v} doesn not match pattern {p}'
        sp = '(January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr' \
             '|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC|JANUARY|FEBRUARY|MARCH' \
             '|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER) '
        split = re.split(v, sp)
        if not split:
            return None, f'Invalid date {v}'
        month_str = [p for p in split if p][0].upper()
        part2 = [p for p in split if p][-1]
        sp2 = '[^0-9]+'
        split2 = re.split(part2, sp2)
        day_str = [p for p in split2 if p][0]
        year_str = [p for p in split2 if p][-1]
        day = int(day_str)
        if not day:
            return None, f'Invalid day {day_str}'
        month = self.en_months_long.get(month_str)
        if not month:
            month = self.en_months_short.get(month_str)
        if not month:
            return None, f'Invalid month {month_str}'
        if len(year_str) == 3:
            return None, f'Invalid year {year_str}'
        elif len(year_str) == 2:
            year_str = f'20{year_str}'
        elif len(year_str) == 1:
            year_str = f'200{year_str}'
        year = int(year_str)
        dt = datetime.datetime(year, month, day)
        if not dt:
            return None, f'Invalid date'
        return dt.strftime('%Y-%m-%d')

    def c_numdotdecimal(self, v):
        p = '[0-9]{1,3}((,| | )?[0-9]{3})*(\.[0-9]+)?'
        if not re.fullmatch(p, v):
            return None, f'Value {v} does not match pattern {p}'
        pos_comma = v.find(',')
        pos_dot = v.find('.')
        commas = re.findall(v, '\,')
        if pos_comma != -1 and pos_dot != -1 and pos_comma > pos_dot:
            return None, f'Invalid format for {v}'
        integerPart = v.replace(' ', ',').replace(' ', ',').replace('-', '').split('.')[0]
        split = integerPart.split(',')
        if len([p for p in split if p and len(p) % 3 != 0 and p != split[0]]):
            return None, f'Invalid format for {v} - incorret position of thousands separator.'
        if len(commas) > 1:
            return None, f'Invalid format for {v} - too many commas.'
        if v.startswith('.'):
            return None, f'Invalid format for {v}. Should not start with a separator.'
        v = v.replace(',', '').replace(' ', '').replace(" ", '')
        d = float(v)
        if not d or d < 0:
            return None, 'Incorrect decimal format'
        return f'{d}', None

    def c_zerodash(self, v):
        if v not in self.zerodash_chars:
            return None, f'Invalid zerodash value {v}'
        return '0', None

    # https://cdn2.hubspot.net/hubfs/486687/EDGAR-filer-manual/Vol_II_ch5.pdf
    def c_sec_stateprovnameen(self, v):
        abbr = self.sec_states.get(v.tolower())
        return abbr, None if None else None, f'Invalid state {v}'

    def c_sec_boolballotbox(self, v):
        return 'true', None if v in ['&#9745;', '&#9746;', '☑', '☒'] \
            else 'false', None if v in ['&#9744;', ''] \
                   else None, f'Invalid Ballot Box Value {v}'

    def c_sec_exchnameen(self, v):
        return None, v  # TODO: Support transfroamtion

    def c_sec_datequarterend(self, v):
        return None, v  # TODO: Support transfroamtion

    def c_sec_durwordsen(self, v):
        return '0', None if v.tolower() in ['no', 'none'] else None, v  # TODO: Support transformation

    def c_sec_numwordsen(self, v):
        return None, v  # TODO: Support transformation

    def c_sec_duryear(self, v):
        return None, v  # TODO: Support transformation

    def c_sec_durmonth(self, v):
        return None, v  # TODO:  Support transformation

    def c_sec_durweek(self, v):
        return None, v  # TODO:  Support transformation

    def c_sec_durday(self, v):
        return None, v  # TODO:  Support transformation

    def c_sec_durhour(self, v):
        return None, v  # TODO: Support transformation

    def c_sec_countrynameen(self, v):
        return None, v

    def c_sec_edgarprovcountryen(self, v):
        return None, v

    def c_sec_entityfilercategoryen(self, v):
        return None, v

    def c_datedoteu(self, v):
        return None, v

    def c_datedotus(self, v):
        return None, v

    def c_datelonguk(self, v):
        return None, v

    def c_datelongus(self, v):
        return None, v

    def c_dateshortuk(self, v):
        return None, v

    def c_dateshortus(self, v):
        return None, v

    def c_dateslasheu(self, v):
        return None, v

    def c_dateslashus(self, v):
        return None, v

    def c_datelongdaymonthuk(self, v):
        return None, v

    def c_datelongmonthdayus(self, v):
        return None, v

    def c_dateshortdaymonthuk(self, v):
        return None, v

    def c_dateshortmonthdayus(self, v):
        return None, v

    def c_dateslashdaymontheu(self, v):
        return None, v

    def c_dateslashmonthdayus(self, v):
        return None, v

    def c_datelongyearmonth(self, v):
        return None, v

    def c_dateshortyearmonth(self, v):
        return None, v

    def c_datelongmonthyear(self, v):
        return None, v

    def c_dateshortmonthyear(self, v):
        return None, v

    def c_numcomma(self, v):
        return None, v

    def c_numcommadot(self, v):
        return None, v

    def c_numdash(self, v):
        return None, v

    def c_numdotcomma(self, v):
        return None, v

    def c_numspacecomma(self, v):
        return None, v

    def c_numspacedot(self, v):
        return None, v



