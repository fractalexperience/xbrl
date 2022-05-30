import re
import datetime
from xbrl.base import util as util


class Formatter:
    def __init__(self):
        self.convertors = {
            # TR1
            'datedoteu': self.c_datedoteu,
            'datedotus': self.c_datedotus,
            'datelonguk': self.c_datelonguk,
            'datelongus': self.c_datelongus,
            'dateshortuk': self.c_dateshortuk,
            'dateshortus': self.c_dateshortus,
            'dateslasheu': self.c_dateslasheu,
            'dateslashus': self.c_dateslashus,
            'datelongdaymonthuk': self.c_datelongdaymonthuk,
            'datelongmonthdayus': self.c_datelongmonthdayus,
            'dateshortdaymonthuk': self.c_dateshortdaymonthuk,
            'dateshortmonthdayus': self.c_dateshortmonthdayus,
            'dateslashdaymontheu': self.c_dateslashdaymontheu,
            'dateslashmonthdayus': self.c_dateslashmonthdayus,
            'datelongyearmonth': self.c_datelongyearmonth,
            'dateshortyearmonth': self.c_dateshortyearmonth,
            'datelongmonthyear': self.c_datelongmonthyear,
            'dateshortmonthyear': self.c_dateshortmonthyear,
            'numcomma': self.c_numcomma,
            'numcommadot': self.c_numcommadot,
            'numdash': self.c_numdash,
            'numdotcomma': self.c_numdotcomma,
            'numspacecomma': self.c_numspacecomma,
            'numspacedot': self.c_numspacedot,
            # TR2

            'datemonthdayyearen': self.c_datemonthdayyearen,
            'numdotdecimal': self.c_numdotdecimal,
            'nocontent': self.c_nocontent,
            'zerodash': self.c_zerodash,

            # TR3
            'booleanfalse': self.c_booleanfalse,
            'booleantrue': self.c_booleantrue,
            # 'calindaymonthyear': self.c_calindaymonthyear,
            # 'datedaymonth': self.c_datedaymonth,
            # 'datedaymonthdk': self.c_datedaymonthdk,
            # 'datedaymonthen': self.c_datedaymonthen,
            # 'datedaymonthyear': self.c_datedaymonthyear,
            # 'datedaymonthyeardk': self.c_datedaymonthyeardk,
            # 'datedaymonthyearen': self.c_datedaymonthyearen,
            # 'datedaymonthyearin': self.c_datedaymonthyearin,
            # 'dateerayearmonthdayjp': self.c_dateerayearmonthdayjp,
            # 'dateerayearmonthjp': self.c_dateerayearmonthjp,
            # 'datemonthday': self.c_datemonthday,
            # 'datemonthdayen': self.c_datemonthdayen,
            # 'datemonthdayyear': self.c_datemonthdayyearen,
            # 'datemonthyear': self.c_datemonthyear,
            # 'datemonthyeardk': self.c_datemonthyeardk,
            # 'datemonthyearen': self.c_datemonthyearen,
            # 'datemonthyearin': self.c_datemonthyearin,
            # 'dateyearmonthday': self.c_dateyearmonthday,
            # 'dateyearmonthdaycjk': self.c_dateyearmonthdaycjk,
            # 'dateyearmonthcjk': self.c_dateyearmonthcjk,
            # 'dateyearmonthen': self.c_dateyearmonthen,
            'numdotdecimalin': self.c_numdotdecimal,
            'numunitdecimal': self.c_numunitdecimal,
            'numunitdecimalin': self.c_numunitdecimal,

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
            'entityfilercategoryen': self.c_sec_entityfilercategoryen,

            # TR5
            'date-day-month': self.tr5_repeat,
            'date-day-month-year': self.tr5_repeat,
            'date-day-monthname-bg': self.tr5_repeat,
            'date-day-monthname-cs': self.tr5_repeat,
            'date-day-monthname-cy': self.tr5_repeat,
            'date-day-monthname-da': self.tr5_repeat,
            'date-day-monthname-de': self.tr5_repeat,
            'date-day-monthname-el': self.tr5_repeat,
            'date-day-monthname-en': self.tr5_repeat,
            'date-day-monthname-es': self.tr5_repeat,
            'date-day-monthname-et': self.tr5_repeat,
            'date-day-monthname-fi': self.tr5_repeat,
            'date-day-monthname-fr': self.tr5_repeat,
            'date-day-monthname-hr': self.tr5_repeat,
            'date-day-monthname-it': self.tr5_repeat,
            'date-day-monthname-lv': self.tr5_repeat,
            'date-day-monthname-nl': self.tr5_repeat,
            'date-day-monthname-no': self.tr5_repeat,
            'date-day-monthname-pl': self.tr5_repeat,
            'date-day-monthname-pt': self.tr5_repeat,
            'date-day-monthname-ro': self.tr5_repeat,
            'date-day-monthname-sk': self.tr5_repeat,
            'date-day-monthname-sl': self.tr5_repeat,
            'date-day-monthname-sv': self.tr5_repeat,
            'date-day-monthname-year-bg': self.tr5_repeat,
            'date-day-monthname-year-cs': self.tr5_repeat,
            'date-day-monthname-year-cy': self.tr5_repeat,
            'date-day-monthname-year-da': self.tr5_repeat,
            'date-day-monthname-year-de': self.tr5_repeat,
            'date-day-monthname-year-el': self.tr5_repeat,
            'date-day-monthname-year-en': self.tr5_repeat,
            'date-day-monthname-year-es': self.tr5_repeat,
            'date-day-monthname-year-et': self.tr5_repeat,
            'date-day-monthname-year-fi': self.tr5_repeat,
            'date-day-monthname-year-fr': self.tr5_repeat,
            'date-day-monthname-year-hi': self.tr5_repeat,
            'date-day-monthname-year-hr': self.tr5_repeat,
            'date-day-monthname-year-it': self.tr5_repeat,
            'date-day-monthname-year-nl': self.tr5_repeat,
            'date-day-monthname-year-no': self.tr5_repeat,
            'date-day-monthname-year-pl': self.tr5_repeat,
            'date-day-monthname-year-pt': self.tr5_repeat,
            'date-day-monthname-year-ro': self.tr5_repeat,
            'date-day-monthname-year-sk': self.tr5_repeat,
            'date-day-monthname-year-sl': self.tr5_repeat,
            'date-day-monthname-year-sv': self.tr5_repeat,
            'date-day-monthroman': self.tr5_repeat,
            'date-day-monthroman-year': self.tr5_repeat,
            'date-ind-day-monthname-year-hi': self.tr5_repeat,
            'date-jpn-era-year-month': self.tr5_repeat,
            'date-jpn-era-year-month-day': self.tr5_repeat,
            'date-month-day': self.tr5_repeat,
            'date-month-day-year': self.tr5_repeat,
            'date-month-year': self.tr5_repeat,
            'date-monthname-day-en': self.tr5_repeat,
            'date-monthname-day-hu': self.tr5_repeat,
            'date-monthname-day-lt': self.tr5_repeat,
            'date-monthname-day-year-en': self.tr5_repeat,
            'date-monthname-year-bg': self.tr5_repeat,
            'date-monthname-year-cs': self.tr5_repeat,
            'date-monthname-year-cy': self.tr5_repeat,
            'date-monthname-year-da': self.tr5_repeat,
            'date-monthname-year-de': self.tr5_repeat,
            'date-monthname-year-el': self.tr5_repeat,
            'date-monthname-year-en': self.tr5_repeat,
            'date-monthname-year-es': self.tr5_repeat,
            'date-monthname-year-et': self.tr5_repeat,
            'date-monthname-year-fi': self.tr5_repeat,
            'date-monthname-year-fr': self.tr5_repeat,
            'date-monthname-year-hi': self.tr5_repeat,
            'date-monthname-year-hr': self.tr5_repeat,
            'date-monthname-year-it': self.tr5_repeat,
            'date-monthname-year-nl': self.tr5_repeat,
            'date-monthname-year-no': self.tr5_repeat,
            'date-monthname-year-pl': self.tr5_repeat,
            'date-monthname-year-pt': self.tr5_repeat,
            'date-monthname-year-ro': self.tr5_repeat,
            'date-monthname-year-sk': self.tr5_repeat,
            'date-monthname-year-sl': self.tr5_repeat,
            'date-monthname-year-sv': self.tr5_repeat,
            'date-monthroman-year': self.tr5_repeat,
            'date-year-day-monthname-lv': self.tr5_repeat,
            'date-year-month': self.tr5_repeat,
            'date-year-month-day': self.tr5_repeat,
            'date-year-monthname-day-hu': self.tr5_repeat,
            'date-year-monthname-day-lt': self.tr5_repeat,
            'date-year-monthname-en': self.tr5_repeat,
            'date-year-monthname-hu': self.tr5_repeat,
            'date-year-monthname-lt': self.tr5_repeat,
            'date-year-monthname-lv': self.tr5_repeat,
            'fixed-empty': self.tr5_fixedempty,
            'fixed-false': self.tr5_fixedfalse,
            'fixed-true': self.tr5_fixedtrue,
            'fixed-zero': self.tr5_fixedzero,
            'numcommadecimal': self.tr5_numcommadecimal,
            'num-comma-decimal': self.tr5_numcommadecimal,
            'num-dot-decimal': self.tr5_numdotdecimal,
            'num-unit-decimal': self.tr5_repeat,
            'num-comma-decimal-apos': self.tr5_numdotdecimal,
            'num-dot-decimal-apos': self.tr5_numcommadecimal,
            'num-unit-decimal-apos': self.tr5_repeat

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
        self.dct_numbers = {
            'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6, 'seven': 7,
            'eight': 8, 'nine': 9, 'ten': 10, 'eleven': 11, 'twelve': 12, 'thirteen': 13, 'fourteen': 14,
            'fifteen': 15, 'sixteen': 16, 'seventeen': 17, 'eighteen': 18, 'nineteen': 19, 'twenty': 20,
            'thirty': 30, 'forty': 40, 'fifty': 50, 'sixty': 60, 'seventy': 70, 'eighty': 80, 'ninety': 90}
        self.dct_quantifiers = {
            'hundred': 100, 'thousand': 1000, 'million': 10 ** 6, 'billion': 10 ** 9, 'trillion': 10 ** 12,
            'quadrillion': 10 ** 15, 'quintillion': 10 ** 18}

        self.exch_names = util.create_key_index({
            'The New York Stock Exchange': 'NYSE',
            'York Stock Exchange LLC': 'NYSE',
            'NASDAQ Global Select Market': 'NASDAQ',
            'The Nasdaq Stock Market LLC': 'NASDAQ',
            'BOX Exchange LLC': 'BOX',
            'Nasdaq BX, Inc.': 'BX',
            'Cboe C2 Exchange, Inc.': 'C2',
            'Cboe Exchange, Inc.': 'CBOE',
            'Chicago Stock Exchange, Inc.': 'CHX',
            'Cboe BYX Exchange, Inc.': 'CboeBYX',
            'Cboe BZX Exchange, Inc.': 'CboeBZX',
            'Cboe EDGA Exchange, Inc.': 'CboeEDGA',
            'Cboe EDGX Exchange, Inc.': 'CboeEDGX',
            'Nasdaq GEMX, LLC': 'GEMX',
            'Investors Exchange LLC': 'IEX',
            'Nasdaq ISE, LLC': 'ISE',
            'Miami International Securities Exchange': 'MIAX',
            'Nasdaq MRX, LLC': 'MRX',
            'NYSE American LLC': 'NYSEAMER',
            'NYSE Arca, Inc.': 'NYSEArca',
            'NYSE National, Inc.': 'NYSENAT',
            'MIAX PEARL, LLC': 'PEARL',
            'Nasdaq PHLX LLC': 'Phlx'
        })

    def apply_format(self, v, f):
        method = self.convertors.get(f)
        if not method and ':' in f:
            method = self.convertors.get(f.split(':')[1])
        if method:
            t = method(v)
            return t[0] if t else v  # First member of the tuple
        else:
            print('Unknown format:', f, 'for value', v)
            return v

    # Numeric
    def tr5_repeat(self, v):
        print('Known, but unsupported format for value', v)
        return v, None

    def tr5_fixedempty(self, v):
        return '', None

    def tr5_fixedfalse(self, v):
        return 'false', None

    def tr5_fixedtrue(self, v):
        return 'true', None

    def tr5_fixedzero(self, v):
        return '0', None

    def tr5_numdotdecimal(self, v):
        return self.c_numdotdecimal(''.join([c for c in v if c.isdigit() or c == '.' or c == 'e']))

    def tr5_numcommadecimal(self, v):
        return self.c_numcomma(''.join([c for c in v if c.isdigit() or c == ',' or c == 'e']))

    def c_nocontent(self, v):
        return None, None  # No matter of the value, we return none

    def c_numunitdecimal(self, v):
        v = util.normalize(util.strip_chars(v, ['.', ' '])).replace(' ', '.')
        return self.c_numdotdecimal(v)

    def c_numdotdecimal(self, v):
        if not v:
            return v
        v = v.strip()
        p = '[0-9]{1,3}((,| | )?[0-9]{3})*(\\.[0-9]+)?'
        if not re.fullmatch(p, v):
            return None, f'Value {v} does not match pattern {p}'
        pos_comma = v.find(',')
        pos_dot = v.find('.')
        commas = re.findall(v, '\\,')
        if pos_comma != -1 and pos_dot != -1 and pos_comma > pos_dot:
            return None, f'Invalid format for {v}'
        integerPart = v.replace(' ', ',').replace(' ', ',').replace('-', '').split('.')[0]
        split = integerPart.split(',')
        if len([p for p in split if p and len(p) % 3 != 0 and p != split[0]]):
            return None, f'Invalid format for {v} - incorrect position of thousands separator.'
        if len(commas) > 1:
            return None, f'Invalid format for {v} - too many commas.'
        if v.startswith('.'):
            return None, f'Invalid format for {v}. Should not start with a separator.'
        v = v.replace(',', '').replace(' ', '').replace(" ", '')
        d = float(v)
        if d < 0:
            return None, 'Incorrect decimal format'
        return d, None

    def c_zerodash(self, v):
        v = v.strip()
        if v not in self.zerodash_chars:
            return None, f'Invalid zerodash value {v}'
        return '0', None

    def c_booleanfalse(self, v):
        return False, None

    def c_booleantrue(self, v):
        return True, None

    def c_numdash(self, v):
        """ Single dash character used to denote a zero value. """
        if v not in self.zerodash_chars:
            return None, f'Invalid zerodash value {v}'
        return '0', None

    def is_nonnegative_decimal(self, v):
        f = None
        try:
            f = float(v)
            is_float = True
        except ValueError:
            is_float = False
        return is_float and f >= 0

    def c_numcomma(self, v):
        p = '\\d+(,\\d+)?'
        if not re.fullmatch(p, v):
            return None, f'Invalid value against pattern {p}'
        # Convert a thousands separator to a canonical value.
        d = str(v).strip().replace(',', '.')
        if not self.is_nonnegative_decimal(d):
            return None, f'Invalid nonNegativeDecimal {v}'
        return d, None

    def c_numcommadot(self, v):
        """ Positive decimal values with a comma for the thousands separator and a dot for the fraction separator.
            No spaces (unless leading or trailing), signs, or exponentials accepted.
            Must have at least one digit before the decimal point, if any. If there is a decimal,
            then it must be followed by at least one digit. """
        p = '\\d{1,3}(,\\d{3,3})*(\\.\\d+)?'
        if not re.fullmatch(p, v):
            return None, f'Invalid value against pattern {p}'

        # Convert a thousands separator to a canonical value.
        d = str(v).strip().replace(',', '')
        if not self.is_nonnegative_decimal(d):
            return None, f'Invalid nonNegativeDecimal {v}'
        return d, None

    def c_numdotcomma(self, v):
        """ Positive decimal values with a dot for the thousands separator and a comma for the fraction separator.
            No spaces (unless leading or trailing), signs, or exponentials accepted.
            Must have at least one digit before the decimal point, if any.
            If there is a decimal, then it must be followed by at least one digit. """
        p = '\\d{1,3}(.\\d{3,3})*(,\\d+)?'
        d = str(v).strip().replace('.', '').replace(',', '.')
        if not self.is_nonnegative_decimal(d):
            return None, f'Invalid nonNegativeDecimal {v}'
        return d, None

    def c_numspacecomma(self, v):
        """ Positive decimal values with a single space for the thousands separator and a comma for the fraction separator.
            No spaces (unless leading or trailing), signs, or exponentials accepted.
            Must have at least one digit before the decimal point, if any. If there is a decimal,
            then it must be followed by at least one digit. """
        p = '\\d{1,3}( \\d{3,3})*(,\\d+)?'
        d = str(v).strip().replace(' ', '').replace(',', '.')
        if not self.is_nonnegative_decimal(d):
            return None, f'Invalid nonNegativeDecimal {v}'
        return d, None

    def c_numspacedot(self, v):
        """ Positive decimal values with a single space for the thousands separator and a dot for the fraction separator.
            No spaces (unless leading or trailing), signs, or exponentials accepted.
            Must have at least one digit before the decimal point, if any.
            If there is a decimal, then it must be followed by at least one digit. """
        p = '\\d{1,3}( \\d{3,3})*(\\.\\d+)?'
        d = str(v).strip().replace(' ', '')
        if not self.is_nonnegative_decimal(d):
            return None, f'Invalid nonNegativeDecimal {v}'
        return d, None

    # https://cdn2.hubspot.net/hubfs/486687/EDGAR-filer-manual/Vol_II_ch5.pdf
    def c_sec_stateprovnameen(self, v):
        abbr = self.sec_states.get(v.tolower())
        return abbr, None if None else None, f'Invalid state {v}'

    def c_sec_boolballotbox(self, v):
        return 'true', None if v in ['&#9745;', '&#9746;', '☑', '☒'] \
            else 'false', None if v in ['&#9744;', ''] \
                   else None, f'Invalid Ballot Box Value {v}'

    def c_sec_exchnameen(self, v):
        resolved = self.exch_names.get(util.get_key_lower(v), None)
        if resolved:
            return resolved, None
        return v, 'Unknown stock exchange name'

    def c_sec_datequarterend(self, v):
        return v, None  # TODO: Support transfroamtion

    def c_sec_durwordsen(self, v):
        return '0', None if v.lower() in ['no', 'none'] else v, 'Unrecognized [durwordsen] value'

    def c_sec_numwordsen(self, v):
        v = util.normalize(v.lower().replace('-', ' ').replace(',', ''))
        if v in ['no', 'none', 'nil', 'zero']:
            return '0', None
        v = util.normalize(v.replace('\n', ' ').replace('\t', ' '))
        parts = v.split(' ')
        total_sum = 0
        partial_sum = None
        quantifier = 1
        state = 'i'
        old_state = state
        to_ignore = ['and', ',']
        for p in [p for p in parts if p not in to_ignore]:
            pnum = self.dct_numbers.get(p, None)
            pqtf = self.dct_quantifiers.get(p, None)
            if pnum is None and pqtf is None:
                return v, f'Unrecognized token in [numwordsen] {p}'
            if pnum is not None:
                state = 'p'
            if pqtf is not None:
                state = 'q'
            transition = old_state+state
            match transition:
                case 'ip':
                    partial_sum = pnum
                case 'iq':
                    return v, f'Invalid [numwordsen] value {v} - should not start with a quantifier.'
                case 'pq':
                    quantifier = quantifier * pqtf
                    total_sum += partial_sum * quantifier
                case 'qp':
                    partial_sum = pnum
                    quantifier = 1
                case 'pp':
                    partial_sum += pnum
                case 'qq':
                    total_sum -= partial_sum * quantifier
                    quantifier = quantifier * pqtf
                    total_sum += partial_sum * quantifier
            # print(p, ' --> ', transition, ': (p)', partial_sum, '(q)',quantifier, '(t)', total_sum)
            old_state = state

        state = 'e'
        transition = old_state + state
        match transition:
            case 'ip':
                total_sum = partial_sum
            case 'pq':
                total_sum += partial_sum * quantifier
            case 'qp':
                total_sum += partial_sum * quantifier
            case 'pe':
                total_sum += partial_sum
            case 'qe':
                pass
        # print('|->', transition, ': (p)', partial_sum, '(q)', quantifier, '(t)', total_sum)
        return total_sum, None

    def c_sec_duryear(self, v):
        return v, None  # TODO: Support transformation

    def c_sec_durmonth(self, v):
        return v, None  # TODO:  Support transformation

    def c_sec_durweek(self, v):
        return v, None  # TODO:  Support transformation

    def c_sec_durday(self, v):
        return v, None  # TODO:  Support transformation

    def c_sec_durhour(self, v):
        return v, None  # TODO: Support transformation

    def c_sec_countrynameen(self, v):
        return v, None

    def c_sec_edgarprovcountryen(self, v):
        return v, None

    def c_sec_entityfilercategoryen(self, v):
        return v, None

    # Dates
    @staticmethod
    def format_day(v):
        s = str(v).strip().zfill(2)
        if not s:
            return s, 'Empty day'
        if not s.isdigit():
            return v, f'Invalid day {s}'
        return s, None

    @staticmethod
    def format_year(v):
        y = v.strip()
        if not y:
            return y, 'Empty year'
        if len(y) == 3 or not y.isdigit():
            return y, f'Invalid year {y}'
        if len(y) == 1:
            y = f'200{y}'
        elif len(y) == 2:
            y = f'20{y}'
        return y, None

    @staticmethod
    def format_month(v, dct_months):
        m = v.strip()
        if not m:
            return m, 'Empty month'
        if dct_months:
            month = dct_months.get(m.lower())
            if not month:
                return None, 'Unknown month'
            m = str(month)
        else:
            if not m.isdigit() or int(m) < 1 or int(m) > 12:
                return m, f'Invalid month {m}'
        return m.zfill(2), None

    def format_date(self, value, pattern, to_ignore, delimiter, positions, dct_months):
        """
        pattern is a RegEx to roughly check the validity.
        positions is a tuple where:
        1: day position,
        2: month position
        3: year position """
        if pattern and not re.fullmatch(pattern, value):
            return None, f'Value {value} does not match pattern {pattern}'
        if to_ignore:
            value = util.normalize(value.replace(to_ignore, ' '))
        split = value.split(delimiter)
        if len(split) < 3:
            return None, 'Invalid date.'
        d, msg_d = self.format_day(split[positions[0]])
        m, msg_m = self.format_month(split[positions[1]], dct_months)
        y, msg_y = self.format_year(split[positions[2]])
        messages = [p for p in {msg_d, msg_m, msg_y} if p]
        if messages:
            return None, ','.join(messages)
        try:
            datetime.datetime(int(y), int(m), int(d))
            is_correct = True
        except ValueError:
            is_correct = False
        if not is_correct:
            return None, f'Incorrect date {value}'
        return f'{y}-{m}-{d}', None

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

    def c_datedoteu(self, v):
        """ Date in format DD.MM.YY(YY). Will also accept single digits for D, M, Y.
            Does not check for valid day or month. e.g. accepts 30.02.2008 40.40.2008 """
        return self.format_date(v, None, None, '.', (0, 1, 2), None)

    def c_datedotus(self, v):
        """ Date in format MM.DD.YY(YY). Will also accept single digits for D, M, Y.
            Does not check for valid day or month. e.g. accepts 02.30.2008 40.40.2008 """
        p = '\\d{1,2}\\.\\d{1,2}\\.(\\d|\\d{2,2}|\\d{4,4})'
        return self.format_date(v, p, None, '.', (1, 0, 2), None)

    def c_datelonguk(self, v):
        """ Date in format DD Month YY(YY). Will also accept single digits for D.
            Does not check for valid day or month. e.g. accepts "30 February 2008" and "40 March 2008" """
        p = '(\\d|\\d{2,2}) (January|February|March|April|May|June|July|August|September|October|November|December) (\\d{2,2}|\\d{4,4})'
        return self.format_date(v, p, None, ' ', (0, 1, 2), self.en_months_long)

    def c_datelongus(self, v):
        """ Date in format Month DD, YY(YY). Will also accept single digits for D.
            Does not check for valid day or month. e.g. accepts 'February 30, 2008' and 'March 40, 2008'. """
        p = '(January|February|March|April|May|June|July|August|September|October|November|December) (\\d|\\d{2,2}), (\\d{2,2}|\\d{4,4})'
        return self.format_date(v, p, ',', ' ', (1, 0, 2), self.en_months_long)

    def c_dateshortuk(self, v):
        """ Date in format DD Mon YY(YY). Will also accept single digits for D.
            Does not check for valid day or month. e.g. accepts "30 Feb 2008" and "40 Mar 2008" """
        p = '(\\d|\\d{2,2}) (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) (\\d{2,2}|\\d{4,4})'
        return self.format_date(v, p, None, ' ', (0, 1, 2), self.en_months_short)

    def c_dateshortus(self, v):
        """ Date in format Mon DD, YY(YY). Will also accept single digits for D.
            Does not check for valid day or month. e.g. accepts "Feb 30, 2008" and "Mar 40, 2008". """
        p = '(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) (\\d|\\d{2,2}), (\\d{4,4}|\\d{2,2})'
        return self.format_date(v, p, ',', ' ', (1, 0, 2), self.en_months_short)

    def c_dateslasheu(self, v):
        """ Date in format DD/MM/YY(YY). Will also accept single digits for D, M, Y.
            Does not check for valid day or month. e.g. accepts 30/02/2008 40/40/2008 """
        p = '\\d{1,2}/\\d{1,2}/(\\d|\\d{2,2}|\\d{4,4})'
        return self.format_date(v, p, None, '/', (0, 1, 2), None)

    def c_dateslashus(self, v):
        """ Date in format MM/DD/YY(YY). Will also accept single digits for D, M, Y.
            Does not check for valid day or month. e.g. accepts 02/30/2008 40/40/2008 """
        p = '\\d{1,2}/\\d{1,2}/(\\d|\\d{2,2}|\\d{4,4})'
        return self.format_date(v, p, None, '/', (1, 0, 2), None)

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
