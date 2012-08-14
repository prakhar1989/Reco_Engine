import sqlite3

class User():
    def __init__(self, id, age, occupation, male):
        self.id = id
        self.male = male
        self.age = age
        self.occupation = occupation
        self.movie_ratings = {}
        self.pcc_dict = {}
        self.set_movie_ratings()

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
        return s[1]

    def get_all_pcc(self):
        """Returns a dict of PCC and corresponding neighbor for user a"""
        conn = sqlite3.connect("data.db")
        c = conn.cursor()
        t = (self.id, )
        c.execute("SELECT * FROM users where not user_id = ?", t)
        users = c.fetchall()
        c.close()
        for u in users:
            a = make_user_object(u[0])
            self.pcc_dict[u[0]] = pearson_correlation_coeff(self, a)



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
    w, sigmaa, sigmau, count = (0, 0, 0, 1)
    for m in a.movies():
        if u.rating(m):
            count += 1
            w += (a.rating(m) - a.get_average_rating()) * (u.rating(m) - u.get_average_rating())
            sigmaa += (a.rating(m) - a.get_average_rating()) ** 2
            sigmau += (u.rating(m) - u.get_average_rating()) ** 2
    if (sigmaa == 0) or (sigmau == 0): return 0
    return w * significance_weight(count)/((sigmaa ** 0.5) * (sigmau ** 0.5))

def significance_weight(count, n = 10):
    """Returns a weighting factor. If number of co-rated
    items > n(default 10) then it returns 1 else returns
    (no. of corated items) / n"""
    if count >= n: return 1
    return float(count) / n

#USAGE
u = make_user_object(1)
a = make_user_object(2)
print pearson_correlation_coeff(a,u) # has to be between 1 and -1
u.get_all_pcc()
