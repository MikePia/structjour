'''
Created on Oct 16, 2018

@author: Mike Petersen
'''
from random import randint
import pandas as pd
# pylint: disable = C0301
# pylint: disable = C0103


class Inspire(object):
    '''TODO use an optional db to keep track of these and allow the user to add and delete quotes. The quotes in the __init__ will be the
    initial quotes in an Inspire object'''

    def __init__(self):
        quotes = []

        quotes.append([
            "Bezos", "On Change", "Jeff Bezos, Amazon.com founder and CEO",
            "What's dangerous is not to evolve."])
        quotes.append([
            "Ellington", "On Drive", "Duke Ellington, Influential 20th c composer",
            "My attitude is never to be satisfied, never enough, never."
        ])
        quotes.append([
            "Ash", "On Goals", "Mary Kay Ash, cosmetics entrepreneur",
            '''Don't limit yourself. Many people limit themselves to what they think they can
do. You can go as far as your mind lets you. What you believe, remember, you can achieve.'''
        ])
        quotes.append(["Ghandi", "On Honesty", "Mahatma Ghandi, statesman,",
                       '''A "No" uttered from the deepest conviction is better than a "Yes" merely uttered to
please, or worse, to avoid trouble.'''
                       ])
        quotes.append([
            "IBD", "10 Secrets to Success", "10 Traits of Successful People, Number one",
            '''How you think is Everything: Always be positive. Think success, not failure.
Beware of a negative enviornment.'''
        ])
        quotes.append([
            "IBD", "10 Secrets to Success", "10 Traits of Successful People, Number two",
            '''DECIDE UPON YOUR TRUE DREAMS AND GOALS: Write down your specific goals and
develop a plan to reach them'''
        ])
        quotes.append([
            "IBD", "10 Secrets to Success", "10 Traits of Successful People, Number three",
            '''TAKE ACTION: Goals are nothing without action. Don't be afraid to get started.
Just do it.'''
        ])
        quotes.append([
            "IBD", "10 Secrets to Success", "10 Traits of Successful People, Number four",
            '''NEVER STOP LEARNING: Go back to school or read books. Get training and acquire
skills.'''
        ])
        quotes.append([
            "IBD", "10 Secrets to Success", "10 Traits of Successful People, Number five",
            '''BE PERSISTENT AND WORK HARD: Success is a marathon, not a sprint. Never give up.'''
        ])
        quotes.append([
            "IBD", "10 Secrets to Success", "10 Traits of Successful People, Number six",
            '''LEARN TO ANALYZE DETAILS: Get all the facts, all the input. Learn from your mistakes.'''
        ])
        quotes.append([
            "IBD", "10 Secrets to Success", "10 Traits of Successful People, Number seven",
            '''FOCUS YOUR TIME AND MONEY: Don't let other people or things distract you.'''
        ])
        quotes.append([
            "IBD", "10 Secrets to Success", "10 Traits of Successful People, Number eight",
            '''DON'T BE AFRAID TO INNOVATE; BE DIFFERENT: Following the herd is a sure way
to mediocrity.'''
        ])
        quotes.append([
            "IBD", "10 Secrets to Success", "10 Traits of Successful People, Number nine",
            '''DEAL AND COMMUNICATE WITH PEOPLE EFFECTIVELY: No person is an island. Learn to
understand and motivate others.'''
        ])
        quotes.append([
            "IBD", "10 Secrets to Success", "10 Traits of Successful People, Number ten",
            '''BE HONEST AND DEPENDABLE; TAKE RESPONSIBILITY: Otherwise, Nos. 1-9 won't matter.'''
        ])
        quotes.append([
            "Einstein", "On Change", "Albert Einstein, physisist",
            '''Wisdom is not a product of schooling but of the lifelong attempt to acquire it.'''
        ])
        quotes.append([
            "Jordan", "On Basics", "Michael Jordan, basketball player",
            '''Get the fundamentals down and the level of everything you do will rise.'''
        ])
        quotes.append([
            "Borge", "On Joyfulness", "Victor Borge, entertainer",
            '''Laughter is the closest distance between two people.'''
        ])
        quotes.append([
            "Dalio", "On Success", "Ray Dalio, founder Bridgewater assoc",
            '''To do exceptionally well you have to push your limits and that, if you push
your limits, you will crash, and it will hurt a lot. You will think that you have
failed--but that won't be true unless you give up.'''
        ])
        quotes.append([
            "Dalio", "Five Principles for life", "Ray Dalio, founder Bridgewater assoc. Principle one",
            '''Start with a lofty but realistic goal. A concrete and well defined objective
sets the direction of your life.'''
        ])
        quotes.append([
            "Dalio", "Five Principles for life", "Ray Dalio, founder Bridgewater assoc. Principle two",
            '''Fail well and take meticulous notes when you do.'''
        ])
        quotes.append([
            "Dalio", "Five Principles for life", "Ray Dalio, founder Bridgewater assoc. Principle three",
            '''Value truth over ego. Admitting your not always the source of every best idea is
central to success.'''
        ])
        quotes.append([
            "Dalio", "Five Principles for life", "Ray Dalio, founder Bridgewater assoc. Principle four",
            '''Quantify whatever you can. Success isn't an accident.'''
        ])
        quotes.append([
            "Dalio", "Five Principles for life", "Ray Dalio, founder Bridgewater assoc.         Principle five",
            '''Avoid stagnation and evolve.'''
        ])
        quotes.append([
            "George", "On Courage", "David Lloyd George, British statesman",
            '''Don't be afraid to take a big step when one is indicated. You can't cross a
chasm in two small steps.'''
        ])
        quotes.append([
            "Cage", "On Innovation", "John Cage, composer",
            '''I can't understand why people are frightened of new ideas. I'm frightened of
the old ones.'''
        ])
        quotes.append([
            "May", "On Commitment", "Rollo May, psychologist",
            '''The relationship between commitment and doubt is by no means an antagonistic one.
Commitment is healthiest when it is not without doubt but in spite of doubt.'''
        ])
        quotes.append([
            "Sirleaf", "on Goals", "Ellen Johnson Sirleaf, former president of Liberia",
            '''If your dreams do not scare you, they are not big enough.'''
        ])
        quotes.append([
            "Newton", "On Observation", "Sir Isaac Newton, scientist",
            '''If I have ever made any valuable discoveries, it has been owning more to
patient attention than to any other talent.'''
        ])
        quotes.append([
            "Bird", "On Effort", "Larry Bird, basketball player",
            '''I've got a theory that if you give 100% all of the time, somehow things work out
in the end.'''])
        quotes.append([
            "Murray", "On Education", "William Hutchison Murray, author",
            '''Until one is commited, there is hesitancy, the chance to draw back,
ineffectiveness...whatever you can do, or dream you can do, begin it. Boldness
has genius, power and magic in it!'''
        ])
        quotes.append([
            "Hunter", "On Wisdom", "Torii Hunter, baseball player",
            '''Wisdom is healed pain. You don't get wisdom because you just have it. You have
to heal from some pain.'''
        ])
        quotes.append([
            "Eisenhower", "On Leadership", "Dwight D. Eisenhower, U.S. president",
            '''You do not lead by hitting people over the head--that's assault, not leadership.'''
        ])
        quotes.append([
            "Holt", "On Character", "John Holt, educator",
            '''The true test of character is not how much we know how to do , but how we
behave when we don't know what to do.'''
        ])
        quotes.append([
            "Kesey", "On Leadership", "Ken Kesey, novelist",
            '''You don't lead by pointing and telling people some place to go. You lead by
going to that place and making a case.'''
        ])
        quotes.append([
            "Glascow", "On Leadership", "Arnold H. Glascow, humorist",
            '''A good leader takes a little more than his share of the blame, a little less than
his share of the credit.'''
        ])
        quotes.append([
            "Avalokitiesvara", "On Emptiness", "Avalokitesvara, The Bodhisattva",
            '''Gate gate paragate parasamgate bodhi svaha. -- Gone, gone, gone all the way over,
everyone gone to the other shore, enlightenment, svaha!'''
        ])
        quotes.append([
            "Douglas", "On Trading", "Mark Douglas, Author Trading in the Zone",
            '''Those traders that have confidence in their own trades, who trust themseles and
do what needs to be done without hesitation, are the ones who become successful'''
        ])
        quotes.append([
            "Brooks", "On Dreams", "Herb Brooks, hockey coach",
            '''Risk something or forever sit with your dreams.'''
        ])
        quotes.append([
            "Rometty", "On Growth", "Virginia Rometty, IBM CEO",
            '''I learned to always take on things I'd never done before. Growth and comfort
do not coexist.'''
        ])
        quotes.append([
            "Spade", "On Integrity", "Kate Spade, designer",
            '''Live in such a way that if anyone speaks badly of you no one would believe it.'''
        ])
        quotes.append([
            "Brown", "On Goals", "Joel Brown, entrepreneur",
            '''The only thing that stands between you and your dream is the will to try and the belief that it is actually possible.'''
        ])
        quotes.append([
            "Cote", "On Leadership", "David Cote, CEO Honeywell",
            '''To lead you have to address what people really want to know in a simple, transparent way. Just treating people wth respect
makes a big difference.'''
        ])
        quotes.append([
            "Ford", "On Determination", "Gerald Ford, U.S. President",
            '''Never be satisfied with less than your very best effort. If you strive for the top and miss, you'll still beat the pack.'''
        ])
        quotes.append([
            "Kasparov", "On Imagination", "Garry Kasparov, chess champion",
            '''There's on thing only humans can do, and that's dream, so let us dream'''
        ])
        quotes.append([
            "Rickover", "On Observation", "Hyman Rickover, admiral",
            '''It is necessary for us to learn from other's mistakes. You will not live long enough to make tham all yourself.'''
        ])
        quotes.append([
            "Sotomayor", "On Perseverance", "Sonia Sotomayer, associate justice Supreme Court",
            '''No matter how things are for you, ther're harder for other people, and if you
stick with it you can get around the brick walls in your life.'''
        ])
        quotes.append([
            "Ziglar", "On Motivation", "Zig Zigler, sales trainer",
            '''People often say motivation doesn't last. Well neither does bathing--that's why wee recommend it daily.'''
        ])
        quotes.append([
            "Buddha", "On Imact", "Guatama Buddha, sage",
            '''To keep the body in good health is a duty ... otherwise we shall not be able to
keep our mind strong and clear.'''
        ])
        quotes.append([
            "Branson", "On Connecting", "Richard Branson, businessman",
            '''Communication is the most important skill any entrepreneur can possess.'''
        ])
        quotes.append([
            "Degrasse Tyson", "On Knowledge", "Neil deGrasse Tyson, astrophysicist",
            '''There's nothing wrong with cherry-picking the good stuff.'''
        ])
        quotes.append([
            "O'Connonr", "On Diligence", "Sandra Day O'Connor, former Supreme Court Justice",
            '''Do the best you can in every task no matter how unimportant it may seem at
the time. No  one learns more about a problem than the person at the bottom.'''
        ])
        quotes.append([
            "Cook", "On Impact", "Tim Cook, Apple CEO",
            '''You want to be the pebble in the pond that creates the ripple for change.'''
        ])
        quotes.append([
            "Diller", "On Net neutrality", "Barry Diller, American Businessman",
            '''The Internet came together as a miracle, really. Anyone with a wire can
publish, we need to keep it that way.'''
        ])
        quotes.append([
            "Jobs", "On Determination", "Steve Jobs, Apple co-founder",
            '''I'm convinced that about half of what separates the successful entrepreneurs
from the nonsuccessfuls ones is pure perserverance.'''
        ])
        quotes.append([
            "Eisenhower", "On Accountability", "Dwight Eisenhower, 34th U.S. President",
            '''Leadership consists of nothing but taking responsibilit for everything that
goes wrong and giving credit for everything that goes well.'''
        ])
        quotes.append([
            "Sophocles", "On Adversity", "Sophocles, poet",
            '''There is no success without hardship.'''
        ])
        quotes.append([
            "Ali", "On Bouncing Back", "Muhammed Ali, boxer",
            '''Only a man who knows what it is like to be defeated can reach down to the
bottom of his soul and come up with the extra ounce of power it takes to win
when the match is even.'''
        ])
        quotes.append([
            "Roosevelt ", "On Conviction", "Elanor Roosevelt, first lady of the U.S.",
            '''Do what you feel in your heart to be right, for you'll be criticized anyway.'''
        ])
        quotes.append([
            "Lassalle", "On Sitting", "Hugo Lassalle, Jesuit priest",
            '''Its a fact that when you hold your eyes very still, the flow of thought will stop.'''
        ])
        quotes.append([
            "Dalio", "On opinions", "Ray Dalio, founder Bridgewater assoc",
            '''the greatest tragedy of mankind — or one of them — is that people needlessly hold wrong opinions in their minds.'''
        ])
        quotes.append([
            "Mitchell", "On trading plans", "Cory Mitchell, Author for Vantagepointtrading",
            '''Having a plan takes much of the emotion out of trading..you know exactly what o do, how and when. We can't get rid of
our emotions entirely, but the plan helps us control them so they aren't destructive'''
        ])
        quotes.append([
           "Thoreau", "On Thankfulness", "Henry David Thoreau, essayist",
            '''I am grateful for what I am and have. My thanksgiving is perpetual.'''
        ])
        quotes.append([
            "Nelson", "On blessings", "Willie Nelson, Musician",
            '''When I started counting my blessings, my whole life turned around.'''
        ])
        quotes.append([
            "Lutz", "On risk", "Robert Lutz,auto executive",
            '''If you actually 'do things' rather than merely perpetuate the status quo, there is a high probablilty, bordering on
certainty that you will make mistakes'''
        ])
        quotes.append([
            "Crosby", "On collaboration", "David Crosby, Musician",
            '''Competitive effort winds up in war. Collaborative effort winds up in a symphony.'''
        ])
        quotes.append([
            "Nagel", "On Courage", "Jack Nagel, property developer",
            '''One sure guarantee of a mediocre life is a lif lived in fear.'''
        ])
        quotes.append([
            "Emerson", "On contemplation", "Ralph Waldo Emerson, poet",
            '''A man is what he thinks about all day long.'''
        ])
        quotes.append([
            "Jung", "On Authenticity", "C.G.Jung, Psychiatrist",
            '''The privilege of a lifetime is to become who you truly are.'''
        ])
        quotes.append([
            "Grossman ", "On Risk", "Mindy Grossman, CEO of WW International",
            '''Not taking a risk is riskier than taking a risk.'''
        ])

        df = pd.DataFrame(data=quotes, columns=['name', 'on', 'who', 'quote'])
        self.df = df

    def getrandom(self):
        '''
        Get a random quote.
        '''

        num = randint(0, len(self.df)-1)
#         print (len(self.df), num)
        qt = self.df.loc[num]
        ret = "{0}, {1}\n{2}\n\t\t-{3}".format(
            qt['name'], qt['on'], qt['quote'], qt['who'])

        return ret

    def getQuote(self, name):
        qs = self.df[self.df['name'] == name]

        for dummy_i, qt in qs.iterrows():
            print(
                "{0}, {1}\n{2}\n\t\t-{3}\n".format(qt['name'], qt['on'], qt['quote'], qt['who']))

#         for q in qs :
#             print("\n{}".format(q))
#
#         return("Its the end of the world as we know it")

# print("You got to admit its getting better.")


class TradingPlan(object):
    '''
    Nail down those rules for day trading. Swing trading rules will be a seperate object
    '''

    def __init__(self):
        entryRules = []
        exitRules = []
        managementRule = []
        preliminary = []

        # ============================================================
        # ==================== Preliminary Rules =====================
        # ============================================================
        preliminary.append(['With every trade, PROTECT THE CAPITAL.',
                            'This is the first and foremost prime directive..'])


        preliminary.append(['Trade the stock market exclusively.',
                            'It is straight forward and has the most potential.'])

        preliminary.append(['Plan to combine day trading and swing trading. These rules are for day trading.',
                            'In spite of the downside of diversication of my time, I believe I have potential for both.'])

        # ===========================================================
        # ==================== Management Rules =====================
        # ===========================================================
        managementRule.append(['I would like to take a majority of low risk trades.',
                               'This is a plan to build my psychological capital and could change in the future.'])

        managementRule.append(['On any given day, plan trades based on a maximum risk per trade.',
                               'Serves the purpose of mananging the potential psychological baggage.'])

        managementRule.append([['Risk for 2019, months 1-6, will be between $20 and $150.',
                                'Risk for January will be capped at $75, begining with $50 on 1/2/19.'],
                               'Knowing the risk in advance reduces the need to decide making the whole process more enjoyable.'])
        managementRule.append(['Risk per trade will never exceed 2% of my trading capital.',
                               "This is standard practice from sound minds and massive experience."])

        # ============================================================
        # ======================= Entry Rules ========================
        # ============================================================
        entryRules.append(['Identify a stop based on a technical level.',
                           'Anything else is arbitrary.'])

        entryRules.append([['Five minute ORB is restricted to 1/2 position for 1/2019.',
                            'Max $40 risk for the month, beginning with $25 risk on 1/2/19, ).'],
                           'ORBS are big opportunity and big risk.'])

        # ============================================================
        # ======================= Exit Rules =========================
        # ============================================================
        exitRules.append(['With reduced risk, expect reduced profit. Take first partial at .9:1',
                          'Slightly reduced expectation could greatly reduce risk.'])

        exitRules.append(['Do not set a target that skips a technical level.',
                          'A technical level is potential resistance.'])
        exitRules.append([['Do not allow a target to pass without taking a partial',
                           'If a target is hit be sure to take some partial that is 75% or better of target.'],
                          'Greed stands on the other side ready to take your profit away. Give it up. Don\'t think.'])
        exitRules.append(['Do not exceed your max stop loss for the day.',
                          'This is the primary key to consistent trading.'])
        exitRules.append(['After taking a profit, the stop loss moves to break even or better.',
                          'The result is risk is reduced. That is the purpose of scaling out. Accept that profit potential may also be reduced.'])
        self.preliminary = preliminary
        self.entry = entryRules
        self.exit = exitRules
        self.management = managementRule
        self.all = [self.preliminary, self.management, self.entry, self.exit]

    def getRules(self, whichRules, why=False):
        print()
        rules = []
        if whichRules[0].lower().startswith('a'):
            whichRules = ['p', 'm', 'en', 'ex']
        for rule in whichRules:
            if rule.lower().startswith('p'):
                rules.append(('Preliminary Rules', self.preliminary))
            elif rule.lower().startswith('m'):
                rules.append(('Management Rules', self.management))
            elif rule.lower().startswith('en'):
                rules.append(('Entry Rules', self.entry))
            elif rule.lower().startswith('ex'):
                rules.append(('Exit Rules', self.exit))
        for rule in rules:
            print(rule[0])
            for count, rl in enumerate(rule[1]):

                if isinstance(rl[0], list):
                    for count2, rlz in enumerate(rl[0]):
                        if count2 == 0:
                            print(f"{count+1}: {rlz}")
                        else:
                            print(f"     {rlz}")

                else:
                    print(f"{count+1}: {rl[0]}")
                if why:
                    print(f"     {rl[1]}")
                print()


i = Inspire()
q = i.getrandom()
print(q)

tp = TradingPlan()
tp.getRules(['a'])
