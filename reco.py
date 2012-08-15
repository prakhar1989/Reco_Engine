
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
45
46
47
48
49
50
51
52
53
54
55
56
57
58
59
60
61
62
63
64
65
66
67
68
69
70
71
72
73
74
75
76
77
78
79
80
81
82
83
84
85
86
87
88
89
90
91
92
93
94
95
96
97
98
99
100
101
102
103
104
105
106
107
108
109
110
111
112
113
114
115
116
117
118
119
120
121
122
123
124
125
126
127
128
129
130
131
132
133
134
135
136
137
138
139
140
141
142
143
144
145
146
147
148
149
150
151
152
153
154
155
import sqlite3

class User():
    def __init__(self, id, age, occupation, male):
        self.id = id
        self.male = male
        self.age = age
        self.occupation = occupation
        self.movie_ratings = {}
        self.set_movie_ratings()
        self.pcc_data = {}

    def get_pcc_data(self):
        conn = sqlite3.connect("data.db")
        c = conn.cursor()
        t = (self.id,)
        c.execute("select * from pcc_data where user_id = ?", t)
        data = c.fetchall()
        if not data: return None
        for d in data:
            print d[1]
            #self.pcc_data[d[1]] = d[3]
        return self.pcc_data

    def set_movie_ratings(self):
        """Fills up the movie_ratings dict with movies 
        and ratings by the current user. Call this right
        after making a user"""
        conn = sqlite3.connect("data.db")
        c = conn.cursor()
        t = (self.id,)
        c.execute("select * from data where user_id = ?", t)
        for r in c.fetchall():
            self.movie_ratings[r[1]] = r[2]
        c.close()

    def movies(self):
        """Returns a list of movies that the user has rated"""
        return self.movie_ratings.keys()

    def rating(self, movie_name):
        """Returns the rating given by user to the movie.
        Returns None if no rating is given"""
        if movie_name in self.movie_ratings.keys():
            return self.movie_ratings[movie_name]
        return None
    
    def get_average_rating(self):
        """Returns the average rating by the user"""
        conn = sqlite3.connect("data.db")
        c = conn.cursor()
        t = (self.id, )
        c.execute("select * from user_stats where user_id = ?", t)
        s = c.fetchone()
        c.close
        return (s[1],s[2])

    def filter_neighbours_out(self, threshold = 0.1, n = 20):
        """Filers the top n neighbors for active user
        on basis of PCC given wieght > threshold"""
        list_of_users = []
        conn = sqlite3.connect("data.db")
        c = conn.cursor()
        t = (self.id,)
        c.execute("SELECT * FROM pcc_data where user_id = ?", t)
        for r in c.fetchall():
            m = (r[1],r[2])
            list_of_users.append(m)
        list_of_users = filter(lambda (x,y): y > threshold, list_of_users)
        return sorted(list_of_users, key=lambda list: list[1], reverse=True)[:n]

    def check_MR_exists(self, u, i):   
        """ Returns a list of matching movies with the current 
        user """
        if (u.rating(i) and self.rating(i)): return True
        return False

    def filter_neighbours_out(self,i):
        list_of_users = []
        conn = sqlite3.connect("data.db")
        c = conn.cursor()
        t = (a.id,)
        c.execute("SELECT * FROM pcc_data where user_id = ?", t)
        for r in c.fetchall():
            m = (r[1],r[2])
            list_of_users.append(m)
        list_of_users = filter(lambda (x,y): a.check_MR_exists(make_user_object(x),i) and y>0.1,list_of_users)
        return sorted(list_of_users, key=lambda list: list[1], reverse=True)[:20]

    def predict_rating(self,i):
        ravg,sigmaa = a.get_average_rating()
        sum_num,sum_den = (0,0)
        for tup in a.filter_neighbours_out(i):
            j,w = tup
            u = make_user_object(j)
            sum_num += ((u.rating(i) - u.get_average_rating()[0])/u.get_average_rating()[1]) * w
            sum_den += w
        return ravg + (sigmaa * (sum_num/sum_den))


#### CLASS ENDS ####
def make_user_object(i):
    """ Returns a user object with the id as i"""
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    t = (i, )
    c.execute("SELECT * FROM users where user_id = ?", t)
    u = c.fetchone()
    c.close()
    user = User(id = u[0], male = u[2], age = u[1], occupation = u[3])
    return user


def pearson_correlation_coeff(a, u):
    """ Returns the weight between active user a and neighbor u.
    Uses pearson correlation coefficient to compute the weight"""
    w, sigmaa, sigmau, count = (0, 0, 0, 0)
    for m in a.movies():
        if u.rating(m):
            count += 1
            w += (a.rating(m) - a.get_average_rating()[0]) * (u.rating(m) - u.get_average_rating()[0])
            sigmaa += (a.rating(m) - a.get_average_rating()[0]) ** 2
            sigmau += (u.rating(m) - u.get_average_rating()[0]) ** 2
    if (sigmaa == 0) or (sigmau == 0): return 0
    return w * significance_weight(count)/((sigmaa ** 0.5) * (sigmau ** 0.5))

def significance_weight(count, n = 10):
    """Returns a weighting factor. If number of co-rated
    items > n(default 10) then it returns 1 else returns
    (no. of corated items) / n"""
    if count >= n: return 1
    return float(count) / n

def set_all_pcc(i, j):
    """ Fills the pcc data for the user i to user j
    USE WITH CAUTION """
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    #c.execute('''CREATE TABLE pcc_data (user_id INT, other_user_id INT, pcc REAL) ''')
    for i in range(i, j+1): #tweak this to add data in db. Its done till 6.
         x = make_user_object(i)
         t = (i, )
         c.execute("SELECT * FROM users where not user_id = ?", t)
         users = c.fetchall()
         for u in users:
             if u[0] > i:
                 a = make_user_object(u[0])
                 c.execute("INSERT INTO pcc_data VALUES (?, ?, ?)", 
                          (i, u[0], pearson_correlation_coeff(x, a)))
                 conn.commit()
    c.close()


#USAGE
a = make_user_object(2)
print a.predict_rating(237)

