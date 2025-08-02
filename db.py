import mysql.connector
from mysql.connector import Error
from tkinter import ttk, messagebox

def connect_to_db():
    try:
        connection = mysql.connector.connect(
            host='mysql-ranataher.alwaysdata.net',
            user='ranataher',
            password='AbC564qId',
            database='ranataher_oscars',
        )
        if connection.is_connected():
            return connection
    except Error as e:
        messagebox.showerror("Database Error", f"Error connecting to MySQL: {e}")
        return None
#----------------------------------------------------------------------------------------------------------------------#
def check_credentials(username, password):
    connection = connect_to_db()
    if connection:
        try:
            cursor = connection.cursor()
            query = "SELECT 1 FROM User WHERE username = %s AND Password = %s"
            cursor.execute(query, (username, password))
            user = cursor.fetchone()
            return user
        except Error as e:
            print(f"Database Error: {e}")
            return None
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    return None
#----------------------------------------------------------------------------------------------------------------------#
def user_exists(username):
    connection = connect_to_db()
    if connection:
        try:
            cursor = connection.cursor()
            query = "SELECT * FROM User WHERE username = %s"
            cursor.execute(query, (username,))
            exists = cursor.fetchone() is not None
            return exists
        except Error as e:
            print(f"Database Error: {e}")
            return False
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    return False
#----------------------------------------------------------------------------------------------------------------------#
def insert_user(username, gender, country, email, dob, password):
    connection = connect_to_db()
    if connection:
        try:
            cursor = connection.cursor()
            query = "INSERT INTO User (username, gender, country, email_addr, DOB, Password) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(query, (username, gender, country, email, dob, password))
            connection.commit()
            return True
        except Error as e:
            print(f"Database Error: {e}")
            return False
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    return False
#----------------------------------------------------------------------------------------------------------------------#
def search_staff(search_text):
    connection = connect_to_db()
    results = []
    if connection:
        try:
            cursor = connection.cursor()
            words = search_text.strip().split()
            if len(words) == 1:
                first_name_pattern = f"{words[0]}%"
                last_name_pattern = f"%{words[0]}%"
                query = """
                SELECT P.FName, P.LName
                FROM Person P
                WHERE P.FName LIKE %s OR P.LName LIKE %s
                ORDER BY P.FName, P.LName
                LIMIT 30
                """
                cursor.execute(query, (first_name_pattern, last_name_pattern))
            else:
                first_name = words[0]
                last_name_fragment = ' '.join(words[1:])
                first_name_pattern = f"{first_name}%"
                last_name_pattern = f"%{last_name_fragment}%"
                query = """
                SELECT P.FName, P.LName
                FROM Person P
                WHERE P.FName LIKE %s AND P.LName LIKE %s
                ORDER BY P.FName, P.LName
                LIMIT 15
                """
                cursor.execute(query, (first_name_pattern, last_name_pattern))
            results = cursor.fetchall()
        except Error as e:
            print(f"Error searching staff: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    return results
#----------------------------------------------------------------------------------------------------------------------#
def get_staff_nomination(fname, lname):
    connection = connect_to_db()
    results = {"nominations": [], "total_nominations": 0, "total_oscars": 0}
    try:
        if connection:
            cursor = connection.cursor()
            query = """
            SELECT 
                S.MovieName, S.ReleaseYear, S.iteration, S.category,
                CASE WHEN S.granted = 1 THEN 'Yes' ELSE 'No' END as won,
                COUNT(*) as total_nominations,
                SUM(CASE WHEN S.granted = 1 THEN 1 ELSE 0 END) as total_oscars
            FROM SubNom S
            WHERE S.FName = %s AND S.LName = %s
            ORDER BY S.iteration DESC
            """
            cursor.execute(query, (fname, lname))
            nominations = cursor.fetchall()
            if nominations:
                results["total_nominations"] = nominations[0][5]
                results["total_oscars"] = nominations[0][6]
                results["nominations"] = [row[:5] for row in nominations]
    except Error as e:
        print(f"Error getting staff nomination data: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
    return results
#----------------------------------------------------------------------------------------------------------------------#
def search_movie(movie_name):
    connection = connect_to_db()
    results = []
    if connection:
        try:
            cursor = connection.cursor()
            pattern = f"%{movie_name}%"
            query = """
            SELECT S.MovieName, S.ReleaseYear, S.iteration, S.category, 
                   S.FName, S.LName
            FROM SubNom S
            WHERE S.MovieName LIKE %s
            ORDER BY S.ReleaseYear DESC, S.FName, S.LName
            LIMIT 30
            """
            cursor.execute(query, (pattern,))
            results = cursor.fetchall()
        except Error as e:
            print(f"Error searching movie: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    return results
#----------------------------------------------------------------------------------------------------------------------#
def add_user_nomination(username, movie_name, release_year, iteration, category, fname, lname):
    connection = connect_to_db()
    success = False
    if connection:
        try:
            cursor = connection.cursor()
            query = """
            INSERT INTO UserNom (username, MovieName, ReleaseYear, iteration, category, FName, LName) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            values = (username, movie_name, release_year, iteration, category, fname, lname)
            cursor.execute(query, values)
            connection.commit()
            success = True
        except Error as e:
            print(f"Error adding nomination: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    return success
#----------------------------------------------------------------------------------------------------------------------#
def get_user_nominations(username):
    connection = connect_to_db()
    results = []
    if connection:
        try:
            cursor = connection.cursor()
            query = """
            SELECT MovieName, ReleaseYear, iteration, category, FName, LName
            FROM UserNom
            WHERE username = %s
            """
            cursor.execute(query, (username,))
            results = cursor.fetchall()
        except Exception as e:
            print(f"Error fetching user nominations: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    return results
#----------------------------------------------------------------------------------------------------------------------#
def get_top_nominated_movies(iteration, category):
    connection = connect_to_db()
    results = []
    if connection:
        try:
            cursor = connection.cursor()
            query = """
            SELECT COUNT(*) as Nominations, MovieName, ReleaseYear,iteration, category
            FROM UserNom
            WHERE (%s = '' OR iteration = %s)
              AND (%s = '' OR category = %s)
            GROUP BY MovieName, iteration, category
            ORDER BY Nominations DESC
            """
            cursor.execute(query, (iteration, iteration, category, category))
            results = cursor.fetchall()
        except Exception as e:
            print(f"Error fetching top movies: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    return results
#----------------------------------------------------------------------------------------------------------------------#
def get_all_nominated_categories():
    connection = connect_to_db()
    categories = []
    if connection:
        try:
            cursor = connection.cursor()
            query = "SELECT DISTINCT category FROM UserNom ORDER BY category"
            cursor.execute(query)
            categories = [row[0] for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error fetching categories: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    return categories
#----------------------------------------------------------------------------------------------------------------------#
def get_top_5_birth_countries():
    connection = connect_to_db()
    results = []
    if connection:
        try:
            cursor = connection.cursor()
            query = """
            SELECT P.COB, COUNT(*) as Wins
            FROM SubNom S
            INNER JOIN Person P ON S.FName = P.FName AND S.LName = P.LName
            WHERE S.category = 'Best Leading Actor'
              AND S.granted = 1
            GROUP BY P.COB
            ORDER BY Wins DESC, P.COB
            LIMIT 5
            """
            cursor.execute(query)
            results = [row[0] for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error fetching top birth countries: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    return results
#----------------------------------------------------------------------------------------------------------------------#
def get_countries_and_staff_data(country=None):
    connection = connect_to_db()
    result = {
        "countries": [],
        "staff_data": []
    }
    try:
        if connection:
            cursor = connection.cursor()
            countries_query = "SELECT DISTINCT COB FROM Person WHERE COB IS NOT NULL ORDER BY COB"
            cursor.execute(countries_query)
            result["countries"] = [row[0] for row in cursor.fetchall()]
            if country:
                staff_query = """
                SELECT
                  P.FName,
                  P.LName,
                  GROUP_CONCAT(DISTINCT S.category) AS Categories,
                  COUNT(*) AS TotalNominations,
                  SUM(S.granted) AS OscarsWon
                FROM
                  Person P
                INNER JOIN
                  SubNom S ON P.FName = S.FName AND P.LName = S.LName
                WHERE
                  P.COB = %s
                GROUP BY
                  P.FName, P.LName
                ORDER BY
                  TotalNominations DESC, OscarsWon DESC
                """
                cursor.execute(staff_query, (country,))
                result["staff_data"] = cursor.fetchall()
    except Exception as e:
        print(f"Error fetching countries and staff data: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

    return result
#----------------------------------------------------------------------------------------------------------------------#
def get_dream_team():
    connection = connect_to_db()
    results = []
    if connection:
        try:
            cursor = connection.cursor()
            roles = [
                "Best Directing",
                "Best Leading Actor",
                "Best Leading Actress",
                "Best Supporting Actor",
                "Best Supporting Actress",
                "Best Picture",
                "Best Original Song"
            ]
            for role in roles:
                query = """
                SELECT P.FName, P.LName, COUNT(S.granted) AS OscarsWon
                FROM Person P
                INNER JOIN SubNom S ON P.FName = S.FName AND P.LName = S.LName
                WHERE P.DOB != '0000-00-00'
                AND (P.DeathDate = '0000-00-00')
                AND S.category = %s
                AND S.granted = 1
                GROUP BY P.FName, P.LName
                ORDER BY OscarsWon DESC
                LIMIT 1
                """
                cursor.execute(query, (role,))
                result = cursor.fetchone()
                results.append(result)
        except Exception as e:
            print(f"Error getting dream team: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    return results
#----------------------------------------------------------------------------------------------------------------------#
def get_top_production_companies():
    connection = connect_to_db()
    results = []
    try:
        if connection:
            cursor = connection.cursor()
            query = """
            SELECT p.ProductionCompany, COUNT(*) as OscarsWon
            FROM SubNom s
            INNER JOIN ProdCompany p ON s.MovieName = p.MovieName AND s.ReleaseYear = p.ReleaseYear
            WHERE s.granted = 1 AND ProductionCompany != ''
            GROUP BY p.ProductionCompany
            ORDER BY OscarsWon DESC, p.ProductionCompany
            LIMIT 5
            """
            cursor.execute(query)
            results = cursor.fetchall()
    except Exception as e:
        print(f"Error fetching top production companies: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
    return results
#----------------------------------------------------------------------------------------------------------------------#
def get_non_english_movies():
    connection = connect_to_db()
    results = []
    try:
        if connection:
            cursor = connection.cursor()
            query = """
            SELECT m.MovieName, m.ReleaseYear, s.iteration
            FROM Movie m
            INNER JOIN SubNom s ON m.MovieName = s.MovieName AND m.ReleaseYear = s.ReleaseYear
            WHERE m.Language != 'English' AND m.Language != '' AND m.Language != 'Silent'
              AND s.granted = 1
            GROUP BY m.MovieName, m.ReleaseYear, s.iteration
            ORDER BY m.ReleaseYear, s.iteration;
            """
            cursor.execute(query)
            results = cursor.fetchall()
    except Exception as e:
        print(f"Error fetching non-English Oscar winners: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
    return results
#----------------------------------------------------------------------------------------------------------------------#