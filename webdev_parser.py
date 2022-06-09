# -*- coding: utf-8 -*-

from math import ceil
import pickle
from bs4 import BeautifulSoup

CRITERIA = {}
SITES    = {}

class Criterion:
    """Irányelv - általános, nem tartalmaz értékeléseket."""

    __slots__ = {
        'index': 'int - Az irányelv sorszáma (#).',
        'category': 'str - A kategória, amelybe az irányelv tartozik (pl. ''Kurzus követelmény'').',
        'text': 'str - Az irányelv szövege.',
        'success_score': 'int - Az irányelv sikeres teljesítéséért járó pontok.',
        'failure_score': 'int - Az irányelv sikertelen teljesítéséért járó pontok (kiemelt irányelvek esetén negatív, különben 0).',
        'ratings': '[Rating] - Rating objektumokra való hivatkozások listája, amelyek erre az irányelvre vonatkoznak.'
    }

    def __init__(self, index : int, category : str, text : str, success_score : int = None, failure_score : int = None):
        self.index = int(index)
        self.category = category
        self.text = text
        self.success_score = success_score
        self.failure_score = failure_score
        self.ratings = []

    def __int__(self):
        """Az irányelve sorszáma."""
        return self.index

    def important(self) -> bool:
        """Fontos-e az irányelv. Ismeretlen esetén `None`."""
        if self.failure_score == 0:
            return False
        if self.failure_score is not None: # and failure_score < 0 -- redundant
            return True

    def get_score(self, success : bool) -> bool: # may return None
        """Értékelés sikerességétől függően az irányelvre kapott pontszám."""
        if success:
            return self.success_score
        return self.failure_score

    def simple(self):
        """Az irányelv első bekezdése/mondata."""
        return self.text.split('\n', maxsplit=1)[0].split('.', maxsplit=1)[0] + '.'

    def passed(self) -> list:
        """Azon oldalak listája, amik sikeresen teljesítették az irányelvet."""
        return [r.site for r in self.ratings if r.score() > 0]

    def failed(self) -> list:
        """Azon oldalak listája, amik nem teljesítették az irányelvet."""
        return [r.site for r in self.ratings if r.score() <= 0]

class Site:
    pass

class Rating:
    """Egy oldalon egy értékelésre adott pontok."""

    __slots__ = {
        'criterion': 'Criterion - az irányelv, amire az értékelés vonatkozik.',
        'site': 'Site - az oldal, amire az értékelés vonatkozik.',
        'critics_approved': '(bool) - az irányelv teljesítésének a sikeressége egyes értékelők szerint; értékelők .site.critics sorrendben vannak.',
        'comments': '(str) - az irányelvre vonatkozó megjegyzések egyes értékelők szerint; értékelők .site.critics sorrendben vannak.'
    }

    def __init__(self, criterion : Criterion, site : Site, critics_approved : (bool), comments : (str)):
        self.criterion = criterion
        self.site = site
        self.critics_approved = critics_approved
        self.comments = comments
        criterion.ratings.append(self)

    def consensus(self) -> bool:
        """Igaz, ha az összes társértékelő véleménye megegyezik; hamis, ha nem, vagy kevesebb, mint 2 társértékelő van."""
        if self.site.peer_critics() < 2:
            return None
        for i in range(-1, -self.site.peer_critics(), -1):
            if self.critics_approved[i] != self.critics_approved[i-1]:
                return False
        return True

    def critic_score(self, i : int) -> int:
        """`i` indexű értékelő által adott pontszám - erre a methodra valószínűleg nem lesz szükséged."""
        if self.criterion.index == 56 and i == 1 and self.site.tutor_reviewed() and not self.critics_approved[1]:
            return -5 # mert így működik
        return self.criterion.get_score(self.critics_approved[i])

    def author_score(self) -> int:
        """Önértékelési pontszám."""
        return self.critic_score(0)

    def tutor_score(self) -> int:
        """Gyakvez által adott pontszám. None, ha a gyakvez még nem értékelte az oldalt."""
        if self.site.tutor_reviewed():
            return self.critic_score(1)

    def peer_review_score(self) -> int:
        """Társértékelők közös véleménye által adott pontszám; 0, ha kevesebb, mint 2 társértékelő van (vagy nem egyezik meg a véleményük)."""
        if self.site.peer_critics() < 2:
            return 0 # 0 in original table as well, None is too much hassle (although more informative)
        if not self.consensus():
            return 0
        return self.critic_score(-1)

    def passed(self) -> bool:
        """Aktuális legpontosabb értékelés szerint sikeres-e az irányelv teljesítése.

        Ha a gyakvez értékelte már, a gyakvez véleménye;
        Különben, ha több társértékelő is értékelte már, a közös véleményük;
        Különben, ha csak egy társértékelő értékelte, az ő véleménye;
        Különben az önértékelés
        """
        if self.site.tutor_reviewed():
            return self.critics_approved[1]
        elif self.site.peer_critics() >= 1:
            return all(self.critics_approved[1:])
        return self.author_score()

    def score(self) -> int:
        """Aktuális legpontosabb értékelés* szerint az irányelvre járó pontszám *(lásd: ``help(Rating.passed)``)."""
        return self.criterion.get_score(self.passed())

class Site:
    """Egy beadandó oldal információi."""
    
    __slots__ = {
        'author': 'str - Az oldal készítőjének a társértékelő kódja.',
        'tutor_name': 'str - Az oldalt értékelő gyakvez neve.',
        'critics': '(str) - Az oldalt értékelők neve, ahogy a táblázat headerjében megjelenik (pl. (''Hallgatói önértékelés'', ''Tutori értékelés'', ''1. társértékelő\nvéleménye'', ...).',
        'ratings': '[Rating] - Az oldalra adott értékelések listája (minden értékelés egy irányelvre vonatkozik, ld. ``help(Rating)``).',
        'extra_score': 'int - A gyakvez által adott további pontok.',
        'tutor_comment': 'str - A gyakvez megjegyzése az oldalra; None, ha nem tett megjegyzést'
    }

    def __init__(self, author, tutor_name, critics, extra_score = 0, tutor_comment = None):
        self.author = author
        self.tutor_name = tutor_name
        self.critics = critics
        self.ratings = []
        self.extra_score = extra_score
        self.tutor_comment = tutor_comment

    def __repr__(self):
        return self.author

    def tutor_reviewed(self) -> bool:
        """Igaz, ha a gyakvez értékelte már az oldalt."""
        return self.critics[1] == 'Tutori értékelés'

    def peer_critics(self) -> int:
        """Az oldal társértékelőinek a száma (ha egy társértékelő nem értékelte az oldalt, akkor itt sem számít)."""
        return len(self.critics) - self.tutor_reviewed() - 1

    def critic_score(self, i : int) -> int:
        """Az `i` indexű értékelő által adott pontok összege."""
        return sum([r.critic_score(i) for r in self.ratings])

    def author_score(self) -> int:
        """Az önértékelésre adott pontok összege."""
        return self.critic_score(0)

    def tutor_score(self) -> int:
        """A gyakvez által adott pontok összege, beleértve a ""további pontokat""."""
        if self.tutor_reviewed():
            return self.critic_score(1) + self.extra_score

    def peer_review_score(self) -> int:
        """A társértékelők közös véleménye alapján járó pontok összege."""
        return sum([r.peer_review_score() for r in self.ratings])

    def score(self) -> int:
        """Aktuális legpontosabb értékelés szerint járó pontszám, ld. ``help(Rating.score)``."""
        # Nem jó önmagában a szokásos sum formula, a gyakvez által adott további pontokat is bele kell számolni
        if self.tutor_reviewed(): 
            return self.tutor_score()
        elif self.peer_critics() >= 2:
            return self.peer_review_score()
        elif self.peer_critics() == 1:
            return self.critic_score(-1)
        return self.author_score()

    def critic_criteria_completed(self, i : int) -> int:
        """`i` indexű értkékelő szerint sikeresen teljesített irányelvek száma - erre a methodra valószínűleg nem lesz szükséged."""
        return sum([r.critic_score(i) > 0 for r in self.ratings])

    def author_criteria_completed(self) -> int:
        """Önértékelés szerint sikeresen teljesített irányelvek száma."""
        return self.critic_criteria_completed(0)

    def tutor_criteria_completed(self):
        """A gyakvez szerint sikeresen teljesített irányelvek száma."""
        if self.tutor_reviewed():
            return self.critic_criteria_completed(1)

    def peer_review_criteria_completed(self) -> int:
        """Társértékelők közös véleménye szerint sikeresen teljesített irányelvek száma; None, ha az oldalnak 0 vagy 1 társértékelője van."""
        if self.peer_critics() >= 2:
            return sum([r.peer_review_score() > 0 for r in self.ratings])

    def author_rating_correctness_score(self) -> int:
        """Önértékelés helyességére járó pontszám. Ha a gyakvez értékelte az oldalt, az ő értékelése van az önértékeléssel összevetve, különben a társértékelőké."""
        wrong : int
        if self.tutor_reviewed():
            wrong = sum([r.author_score() != r.tutor_score() for r in self.ratings])
        else:
            wrong = sum([r.author_score() != r.peer_review_score() for r in self.ratings])
        return max(0, ceil((30-wrong)*8/15)) # Forrás: önértékelő excel fájl

    def passed(self) -> bool:
        """Megvan-e a kettes."""
        return self.author_rating_correctness_score() >= 8 and self.score() >= 50

    def grade_if_passed(self):
        """Jegy - kizárólag a pontok (`Site.score`) által kiszámítva, más feltétel nincs figyelembe véve."""
        score = self.score() # Forrás: önértékelő excel fájlban rejtett munkalap
        if score >= 89:
            return 5
        if score >= 76:
            return 4
        if score >= 63:
            return 3
        if score >= 50:
            return 2
        return 1

    def grade(self):
        """Jegy."""
        return self.grade_if_passed() if self.passed() else 1

def parse_row(row, site):
    row = [e.text for e in row]

    try:
        index = int(row[0]) # ?? for some reason a few files have invalid chars
    except ValueError:
        index = max([r.criterion.index for r in site.ratings]) + 1
    category = row[1]
    text = row[2]
    score = int(row[-1])

    criterion = None
    if index in CRITERIA:
        criterion = CRITERIA[index]
    else:
        criterion = Criterion(index, category, text)
        CRITERIA[index] = criterion

    critics_approved = []
    comments = []
    for i in range(3, len(row)-2, 2):
        critics_approved.append(row[i] == 'Igen')
        comments.append(row[i+1].strip())
    critics_approved = tuple(critics_approved)
    comments = tuple(comments)

    rating = Rating(criterion, site, critics_approved, comments)
    site.ratings.append(rating)

    if score > 0:
        criterion.success_score = score
    elif score < 0 or (row[-2] == 'Teljes' and not critics_approved[-1]):
        criterion.failure_score = score

def parse_site(f):
    soup = BeautifulSoup(f, 'html.parser')
    tb = soup.find('table', 'excel')

    m_start = soup.text.find('A gyakorlatvezetőd neve (NEPTUN szerint): ')
    m_end = soup.text.find(' Ha kérdésed van, vele konzultálj!')
    tutor = soup.text[(m_start+42) : m_end] # 42: len of m_start string
    author = soup.find('h2').text[:4]
    critics = tb.find('tr').find_all('th')[1:-2]
    critics = tuple(e.text for e in critics)
    bonus = 0
    tutor_comment = None
    mtable = soup.find('table', {'id': 'tutori'})
    if mtable:
        tutor_comment = mtable.find_all('tr')[5].find_all('td')[1].text.strip()
        try:
            bonus = mtable.find_all('tr')[2].find_all('td')[1]
            bonus = int(bonus.text.strip())
        except:
            pass
    if not bonus or type(bonus) is not int:
        bonus = 0
    if not tutor_comment:
        tutor_comment = None

    site = Site(author, tutor, critics, bonus, tutor_comment)

    rowlength = 2*len(critics) + 5
    footercells = 3*len(critics) + 6

    criteria = tb.find_all('tr')[2].find_all('td')[:-footercells] # shit's fucked yo
    criteria.reverse() # for some reason

    while criteria:
        row = [criteria.pop() for _ in range(rowlength)]
        parse_row(row, site)

    SITES[author] = site

def parse_folder(folder = 'ertekelesek'):
    SITES.clear()
    CRITERIA.clear()

    f = open('codes.txt')
    codes = [code.strip() for code in f.readlines()]
    f.close()

    for code in codes:
        # BOM ('\uFEFF') van a fájlok elején, utf-8-sig módban megnyitva át lesz ugorva
        # https://docs.python.org/3/howto/unicode.html#reading-and-writing-unicode-data
        f = open(folder + '/' + code + '.html', encoding='utf-8-sig')
        parse_site(f)
        f.close()

    for c in CRITERIA.values(): # assumme 0 points if no data (shouldn't matter, do anyway just in case)
        if c.success_score is None:
            c.success_score = 0 # []
        if c.failure_score is None:
            c.failure_score = 0 # [9, 14, 19, 40, 46]

    print('LOADED FOLDER', folder)
    f = open('crit_sites.pickle', 'wb')
    pickle.dump((CRITERIA, SITES), f)
    f.close()
    print('SAVED TO crit_sites.pickle')

if __name__ == '__main__':
    parse_folder('ertekelesek')
