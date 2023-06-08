# -*- coding: utf-8 -*-

import pickle
import matplotlib.pyplot as plt
from matplotlib import lines
from matplotlib.ticker import MultipleLocator
from webdev_parser import parse_folder, Criterion, Rating, Site

f = None
try:
    f = open('crit_sites.pickle', 'rb')
except FileNotFoundError:
    parse_folder('ertekelesek')
    f = open('crit_sites.pickle', 'rb')
CRITERIA, SITES = pickle.load(f)
f.close()

DPI = 150

finals = list(filter(lambda s: s.tutor_reviewed(), SITES.values()))
complete = [s for s in finals if s.peer_critics() >= 2]

def print_stats():

    def print_fails():
        fails = [site for site in finals if not site.passed()]
        print(len(fails), 'oldal bukott biztosan -', format(len(fails)/len(finals), '.2%'))
        print()

    def print_perfect():
        perfect = [site for site in finals if site.tutor_criteria_completed() == 56] # bónusz pontok nélkül 100 pont
        print(len(perfect), ' oldal tökéletes a gyakvezek értékelése szerint: ',
              ', '.join(map(str, perfect[:5])), '...', sep='')
        print()

    def print_most_missed_single():
        near_perfect = [site for site in finals if site.tutor_criteria_completed() == 55]
        missed_one = {}
        for site in near_perfect:
            for r in site.ratings:
                if r.tutor_score() <= 0:
                    if r.criterion not in missed_one:
                        missed_one[r.criterion] = 1
                    else:
                        missed_one[r.criterion] += 1
                    break
        most_missed_one = list(missed_one.values()).index(max(missed_one.values()))
        most_missed_one = list(missed_one.keys())[most_missed_one]
        print('Akik csak egy követelményt nem teljesítettek a gyakvez szerint, azok a(z) ',
              most_missed_one.index, '. követelményt hibázták el a leggyakrabban (',
              missed_one[most_missed_one], '/', len(near_perfect),
              '): ', most_missed_one.simple(), sep='')
        print()

    def print_most_missed():
        missed = {c: 0 for c in CRITERIA.values()}
        for site in finals:
            for r in site.ratings:
                if r.tutor_score() <= 0:
                    missed[r.criterion] += 1
        most_missed = list(missed.values()).index(max(missed.values()))
        most_missed = list(missed.keys())[most_missed]
        print('Gyakvezek értékelése szerint a(z) ',
              most_missed.index, '. követelményt hibázták el a leggyakrabban (',
              format(missed[most_missed]/len(finals), '.0%'), '): ',
              most_missed.simple(), sep='')
        print()

    def print_peer_discrepancies():
        discrepancies = {c: 0 for c in CRITERIA.values()}
        for site in complete:
            for r in site.ratings:
                if r.tutor_score() != r.peer_review_score():
                    discrepancies[r.criterion] += 1
        maxd = list(discrepancies.values()).index(max(discrepancies.values()))
        maxd = list(discrepancies.keys())[maxd]
        print('A gyakvezek és a társértékelők pontozása a leggyakrabban (',
              discrepancies[maxd], '/', len(complete), ') a(z) ', maxd.index,
              '. követelménynél tért el: ', maxd.simple(), sep='')
        print()

    print_fails()
    print_perfect()
    print_most_missed_single()
    print_most_missed()
    print_peer_discrepancies()

def draw_figures(saveformat = None):

    def draw_avg(ax, avg, dim, pos = None, fmt='0.1f', linesytle='dashed', color='r', fontsize='x-small'):
        ymin, ymax = plt.ylim()
        xmin, xmax = plt.xlim()

        if dim in ('v', 'vert', 'vertical'):
            line_x = (avg, avg)
            text_x = avg + 0.25
            text_ha = 'center'
            if pos in (None, 'e', 'end', 't', 'top'):
                line_y = (ymin, 0.1*ymin + 0.9*ymax)
                text_y = line_y[1] + 1
                text_va = 'bottom'
            elif pos in ('s', 'start', 'b', 'bottom'):
                line_y = (0.9*ymin + 0.1*ymax, ymax)
                text_y = line_y[0]
                text_va = 'top'
            else:
                raise ValueError(str(pos) + ' invalid value for position')

        elif dim in ('h', 'horiz', 'horizontal'):
            line_x = plt.xlim()
            line_y = (avg, avg)
            text_va = 'bottom'
            if pos in (None, 's', 'start', 'l', 'left'):
                text_x = xmin + 0.5
                text_ha = 'left'
            elif pos in ('e', 'end', 't', 'top'):
                text_x = xmax - 0.5
                text_ha = 'right'
            else:
                raise ValueError(str(pos) + ' invalid value for position')
            text_y = avg + 1

        else:
            raise ValueError(str(dim) + ' invalid value for dimension')

        ax.add_line(lines.Line2D(
            xdata = line_x,
            ydata = line_y,
            linestyle = linesytle,
            alpha = 0.5,
            color = color,
            lw = 0.8,
            zorder = 2.5
        ))
        plt.text(
            x = text_x,
            y = text_y,
            s = 'Átlag: ' + format(avg, fmt),
            size = fontsize,
            color = color,
            ha = text_ha,
            va = text_va
        )

    def draw_scores():
        scores = [site.score() for site in SITES.values()]
        avg = sum([scores.count(i) * i for i in range(-110, 110)])/len(scores)

        plt.figure(dpi=DPI)
        ax = plt.axes()
        ax.xaxis.set_minor_locator(MultipleLocator(5))
        plt.ylim(0, 100) # needs to be set in order to use it in avg drawing

        plt.xlabel('Elért pontszám')
        plt.ylabel('Fő')
        plt.title('Webfejlesztés beadandó eredmények')
        draw_avg(ax, avg, 'vertical')
        plt.text(
            x = 50,
            y = 31,
            s = 'Pontosan 50 pont:\n' + str(scores.count(50)) + ' fő',
            ha  = 'center',
            size = 'small'
        )

        plt.hist(
            scores,
            bins = range(-50, 101, 5),
            histtype = 'barstacked',
            stacked = True,
            width = 4,
            zorder = 2
        )
        plt.grid(True, which='major', axis='y')
        if saveformat:
            fname = 'scores.' + str(saveformat)
            plt.savefig(fname, dpi=DPI)
            print('saved', fname)
        else:
            plt.show()
        plt.close()

    def draw_completed_criteria():
        tutor_criteria_completed = [site.tutor_criteria_completed() for site in finals]
        tutor_criteria_count = [tutor_criteria_completed.count(i) for i in range(20, 57)]
        avg = sum([tutor_criteria_count[i] * (20+i) for i in range(0, 37)])/len(finals)

        plt.figure(dpi=DPI)
        ax = plt.axes()
        ax.xaxis.set_minor_locator(MultipleLocator(1))

        plt.suptitle('Webfejlesztés beadandó eredmények')
        plt.title('Gyakvezek értékelése alapján', size='small', alpha=0.8)
        plt.xlabel('Teljesített követelmények')
        plt.ylabel('Fő')
        plt.xlim(20, 56.75)
        plt.ylim(0, 50)
        draw_avg(ax, avg, 'vertical')

        plt.bar(
            x = range(20, 57),
            height = tutor_criteria_count,
            zorder = 2
        )
        plt.grid(True, which='major', axis='y')
        if saveformat:
            fname = 'completed_criteria.' + str(saveformat)
            plt.savefig(fname, dpi=DPI)
            print('saved', fname)
        else:
            plt.show()
        plt.close()

    def draw_grades():
        grades = {i: 0 for i in list(range(1, 6))}
        for s in finals:
            grades[s.grade()] += 1
        avg = sum([grades[i] * i for i in range(1, 6)])/len(finals)

        plt.figure(dpi=DPI)
        ax = plt.axes()

        plt.suptitle('Webfejlesztés beadandó jegyek')
        plt.title('Gyakvezek értékelése alapján', size='small', alpha=0.8)
        plt.xlabel('Jegy')
        plt.ylabel('Fő')
        plt.xlim(0.5, 5.5)
        plt.ylim(0, 1.1 * max(grades.values())) # needs to be set in order to use it in avg drawing
        draw_avg(ax, avg, 'vertical')
        for g in grades:
            plt.text(
                x = g,
                y = grades[g] + 1,
                s = grades[g],
                ha = 'center',
                size = 'small'
            )

        plt.bar(
            x = grades.keys(),
            height = grades.values(),
            zorder = 2
        )
        plt.grid(True, which='major', axis='y')
        if saveformat:
            fname = 'grades.' + str(saveformat)
            plt.savefig(fname, dpi=DPI)
            print('saved', fname)
        else:
            plt.show()
        plt.close()

    def draw_discrepancy():
        discrepancy_amount = {i: 0 for i in range(1, 57)} # eleve rendezve kéne lennie, de így tuti rendezve lesz
        for c in CRITERIA.values():
            for r in c.ratings:
                if r.site.tutor_reviewed() and (r.critics_approved[0] != r.critics_approved[1]): # score-nál az összes sikertelen 56. irányelvre igazat adna, ld. Rating.critic_score() forráskódja
                    discrepancy_amount[c.index] += 1
        avg = sum(discrepancy_amount.values())/len(discrepancy_amount)

        plt.figure(dpi=DPI)
        ax = plt.axes()
        ax.xaxis.set_minor_locator(MultipleLocator(1))
        ax.xaxis.set_major_locator(MultipleLocator(5))

        plt.title('Gyakvezek és önértékelések eltérése')
        plt.xlabel('Irányelv sorszáma')
        plt.ylabel('Eltérés előfordulása ' + str(len(finals)) + ' értékelésben')
        plt.xlim(0.1, 56.9)
        draw_avg(ax, avg, 'horizontal')
        m = max(discrepancy_amount.values())
        for c, d in discrepancy_amount.items():
            if d == m:
                plt.text(
                    x = c,
                    y = d+1,
                    s = str(d) + ' - ' + format(d/len(finals), '.1%'),
                    ha = 'center',
                    size = 'xx-small'
                )
            else:
                plt.text(
                    x = c,
                    y = d+1,
                    s = d,
                    ha = 'center',
                    size = 'xx-small'
                )

        plt.bar(
            x = discrepancy_amount.keys(),
            height = discrepancy_amount.values(),
            zorder = 2
        )
        plt.grid(True, which='major', axis='y')
        if saveformat:
            fname = 'discrepancies.' + str(saveformat)
            plt.savefig(fname, dpi=DPI)
            print('saved', fname)
        else:
            plt.show()
        plt.close()

    def draw_sorted_discrepancy(): # ez mi a halál egyáltalán
        discrepancy_amount = {i: 0 for i in range(1, 57)}
        for c in CRITERIA.values():
            for r in c.ratings:
                if r.site.tutor_reviewed() and (r.critics_approved[0] != r.critics_approved[1]): # score-nál az összes sikertelen 56. irányelvre igazat adna, ld. Rating.critic_score() forráskódja
                    discrepancy_amount[c.index] += 1
        avg = sum(discrepancy_amount.values())/len(discrepancy_amount)
        discrepancy_amount = sorted(discrepancy_amount.items(), key = lambda i: i[1])
        discrepancy_amount = {k: v for k, v in discrepancy_amount}

        plt.figure(dpi=DPI, figsize=plt.figaspect(1.25))
        ax = plt.axes()
        ax.xaxis.set_minor_locator(MultipleLocator(5))
        ax.yaxis.set_major_formatter('')
        ax.yaxis.set_ticks(ticks=[])
        # yoink https://stackoverflow.com/a/7966544
        xleft, xright = ax.get_xlim()
        ybottom, ytop = ax.get_ylim()
        ax.set_aspect(abs((xright-xleft)/(ybottom-ytop))*3)


        plt.suptitle('Gyakvezek és önértékelések eltérése')
        least = list(discrepancy_amount.keys())[0]
        most = list(discrepancy_amount.keys())[-1]
        plt.title(
            str(most) + '. irányelv: ' + CRITERIA[most].simple() + '\n' +
            str(least) + '. irányelv: ' + CRITERIA[least].simple(),
            size='x-small', alpha=0.75, va='bottom'
        )
        plt.ylabel('Irányelv sorszáma')
        plt.xlabel('Eltérés előfordulása ' + str(len(finals)) + ' értékelésben')
        plt.ylim(-0.25, 57.25)
        draw_avg(ax, avg, 'vertical', pos='start')
        for n, (k, c) in enumerate(discrepancy_amount.items(), 1):
            if True or n % 2 or n <= 4:
                plt.text(
                    x = c + 0.5,
                    y = n,
                    s = k,
                    va = 'center',
                    size = 4.5
                )

        plt.barh(
            y = range(1, 57),
            width = discrepancy_amount.values(),
            zorder = 2
        )
        plt.grid(True, which='major', axis='x')
        if saveformat:
            fname = 'discrepancies_sorted.' + str(saveformat)
            plt.savefig(fname, dpi=DPI)
            print('saved', fname)
        else:
            plt.show()
        plt.close()

    draw_scores()
    draw_completed_criteria()
    draw_grades()
    draw_discrepancy()
    draw_sorted_discrepancy()

if __name__ == '__main__':
    print_stats()
    try:
        exit # fails if running from ipython console, doesn't do anything otherwise (it just works, trust me bro)
        DPI=300
        print('Detected non-interactive environment, saving figures instead of displaying them')
        draw_figures('png')
    except NameError:
        draw_figures()
