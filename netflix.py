from texttable import Texttable
import sys

'''
The user class is used to keep track of each user by ID.
It contains their average rating, a normalized average rating, and a dictionary
of all of the ratings they have given.

The normalized average is based upon equation 3 from this paper:
https://arxiv.org/ftp/arxiv/papers/1301/1301.7363.pdf
'''
class User:
    def __init__(self):
        self.average_rating = None
        self.ratings = dict({})
        self.norm_avg = None

'''
The movie class is used to keep track of each movie's name, year, average rating,
and all of the users' ratings.
'''
class Movie:
    def __init__(self):
        self.movie_name = None
        self.movie_year = None
        self.average_rating = None
        self.ratings = dict({})

# Global Variables for the collection of users and movies.
USER_DICT = {}
MOVIE_DICT = {}

def train_filter():
    # Take user input for the dataset to train on and the
    training_set = input('Enter the name of the file containing your training data: ')
    movie_titles = input('Enter the name of the file containing the titles and years of the movies: ')

    # Open the training set and pull all of the information into the global dictionaries defined above.
    with open(training_set, 'r') as f:
        lines = f.readlines()
        for line in lines:
            # Parse each value from the line.
            a = line.rstrip('\n').split(',')
            movie_id = a[0]
            user_id = a[1]
            rating = float(a[2])

            # Add each user to USER_DICT, or update the one we've already made.
            if USER_DICT.get(user_id): # User is already in the dictionary, so just update that user.
                USER_DICT[user_id].ratings[movie_id] = rating
                USER_DICT[user_id].average_rating = (USER_DICT[user_id].average_rating + rating) / len(USER_DICT[user_id].ratings)
                USER_DICT[user_id].norm_avg = pow((pow(USER_DICT[user_id].norm_avg, 2) + pow(rating, 2)), 0.5)
            else: # User is not yet in the dictionary, so let's make one.
                USER_DICT[user_id] = User()
                USER_DICT[user_id].average_rating = rating
                USER_DICT[user_id].norm_avg = rating
                USER_DICT[user_id].ratings[movie_id] = rating

            # Add each movie to MOVIE_DICT, or update the one we've already made.
            if MOVIE_DICT.get(movie_id): # Movie is already in the dictionary, so just update the movie.
                MOVIE_DICT[movie_id].ratings[user_id] = rating
                MOVIE_DICT[movie_id].average_rating = (MOVIE_DICT[movie_id].average_rating + rating) / len(MOVIE_DICT[movie_id].ratings)
            else: # Movie is not yet in the dictionary, so let's make one.
                MOVIE_DICT[movie_id] = Movie()
                MOVIE_DICT[movie_id].average_rating = rating
                MOVIE_DICT[movie_id].ratings[user_id] = rating

    f.close()

    # Let's give the movies names and years.
    with open(movie_titles, "r", encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

        for line in lines:
            # Parse each value from the line.
            a = line.rstrip('\n').split(',')
            id = a[0]
            year = a[1]
            name = a[2]

            if id in MOVIE_DICT: # If the movie is in MOVIE_DICT, update it.
                MOVIE_DICT[id].movie_name = name
                MOVIE_DICT[id].movie_year = year

    f.close()

def classify_data():
    testing_set = input('Enter the name of the file containing your testing data: ')
    print("The program will now attempt to predict the ratings contained in the file.")
    print("This may take some time. When this is complete, error will be printed to the console.")

    # Start classifying the data.
    with open(testing_set, 'r') as f:
        lines = f.readlines()
        n = 0 # Keep track of the number of ratings classified.
        mae_sum = 0.0 # Keep track of the sum for the Mean Absolute Error.
        rmse_sum = 0.0 # Keep track of the sum for the Root Mean Squared Error.

        # Use this dictionary to keep track of already calculated weights.
        # This is pretty intense on memory, but it makes the algorithm
        # significantly faster.
        weights = {}

        for line in lines:
            # Parse the movie_id, user_id, and the actual rating.
            a = line.rstrip('\n').split(',')
            movie_id = a[0]
            user_id = a[1]
            rating = float(a[2])

            # Only classify id we already have data on the user.
            if user_id in USER_DICT:
                current_user = USER_DICT[user_id] # User we need to predict for.
                avg_rating = current_user.average_rating # That user's average rating.
                sum = 0.0 # Sum for equation 1.

                for key, value in USER_DICT.items(): # Iterate through USER_DICT.
                    # Only calculate a weight if the new user has given a rating to the movie in question.
                    if (key != user_id and movie_id in value.ratings):
                        weight = 0 # Keep track of the weight.
                        # Check if the weight has already been calculated.
                        if (user_id, key) not in weights and (key, user_id) not in weights:
                            # We have to calculate the weight.
                            for m, rating in value.ratings.items():
                                # For every common movie, update the weight.
                                if m != movie_id and m in current_user.ratings:
                                    weight += (current_user.ratings[m] / current_user.norm_avg) * (rating / value.norm_avg)
                            # Save this weight for later. MEMOIZATION
                            weights[(user_id, key)] = weight
                        else:
                            # The weight has already been calculated. Just pull it.
                            if (user_id, key) in weights:
                                weight = weights[(user_id, key)]
                            elif (key, user_id) in weights:
                                weight = weights[(key, user_id)]
                        # Update sum.
                        sum += weight * (value.ratings[movie_id] - value.average_rating)

                calc_rating = avg_rating + sum # Here's our predicted rating.

                # If the rating is lower than 1, just clamp it to 1.
                if calc_rating < 1.0:
                    calc_rating = 1.0
                # If the rating is greater than 5, just clamp it to 5.
                elif calc_rating > 5.0:
                    calc_rating = 5.0
                # Otherwise, just round it.
                else:
                    calc_rating = round(calc_rating)

                n += 1 # Increment n.

                mae_sum += abs(calc_rating - rating) # Update sum for Mean Absolute Error.
                rmse_sum += pow((calc_rating - rating), 2) # Update sum for Root Mean Squared Error.

        mae = mae_sum / n # Calc MAE
        rmse = pow((rmse_sum / n), 0.5) # Calc RMSE

        # Print them
        print("The Mean Absolute Error is {0}".format(mae))
        print("The Root Mean Squared Error is {0}".format(rmse))

def query():
    user_id = input("Please type in the ID of the user in question: ")

    # Keep asking for a user until the program is given a valid ID.
    while (user_id not in USER_DICT):
        user_id = input("That user ID is not in the training set. Please pick a new one: ")

    # Keep track of the user given as well as the year given.
    user = USER_DICT[user_id]
    year = input("Please type in a year: ")

    a = [] # This will hold all movies and ratings found for the given year and user.

    for movie_id, movie in MOVIE_DICT.items(): # Iterate through each movie.
        # Only pull movies that are of the proper year and that the user has not yet watched.
        if movie.movie_year == year and movie_id not in user.ratings:
            # Calculate a rating for this movie.
            calc_rating = user.average_rating
            for userkey, comp_user in USER_DICT.items(): # Iterate through each user in USER_DICT
                if movie_id in comp_user.ratings:
                    # We found a match, but we need the weight between the two users.
                    weight = 0
                    for m, rating in comp_user.ratings.items():
                        if m != movie_id and m in user.ratings:
                            weight += (user.ratings[m] / user.norm_avg) * (rating / comp_user.norm_avg)

                    calc_rating += weight * (comp_user.ratings[movie_id] - comp_user.average_rating)

            a.append((movie.movie_name, calc_rating)) # Append the movie to a.

    a.sort(key=lambda tup: (-tup[1], tup[0])) # Sort them by rating and then by name.

    # Make a table for the data so it looks nice.
    t = Texttable()
    table_rows = [["Movie Name", "Expected Rating"]]

    for movie in a:
        # If the rating given is less than 1, clamo it to 1.
        if (movie[1] < 1):
            table_rows.append([movie[0], 1.0])
        # If the rating given is greater than 5, clamp it to 5.
        elif movie[1] > 5:
            table_rows.append([movie[0], 5.0])
        # Otherwise, just round.
        else:
            table_rows.append([movie[0], round(movie[1])])

    # Build and print the table.
    t.add_rows(table_rows)
    print(t.draw())

    # See if the user wants to query again.
    nextSelection = input("\nWould you like to query again? (y/n): ")

    # MAke sure their choice is valid.
    while nextSelection != 'y' and nextSelection != 'n':
        print("That was not a valid response. Please try again.")
        nextSelection = input("\nWould you like to query again? (y/n): ")

    # Now either query again or return to the options menu.
    if nextSelection == 'y':
        query()
    else:
        classify()

def classify():
    print("Welcome to the Netflix Collaborative Filter!\n")
    print("Please select an option!\n")

    # Make a table so things are pretty.
    t = Texttable()

    t.add_rows([["Option", "Description"],
               ["1", "Classify the Netflix data from a given text file."],
               ["2", "Query the Training Set with a user and a year to find out which other movies in that year a user might like."],
               ["3", "Exit"]
               ])

    print(t.draw() + "\n")

    selection = input("Selection: ")

    while selection != "1" and selection != "2" and selection != "3" and selection.lower() != "exit":
        print("That is not a valid selection. Please try again.")
        selection = input("Selection: ")


    if selection == "1": # If they chose 1, we need to run classify_data().
        classify_data()
    elif selection == "2": # If they chose 2, startquerying.
        query()
    else:
        sys.exit()

# Main function to make my code more pythonic.
def main():
    train_filter()
    classify()

# Just making this more pythonic by using a main() function.
if __name__ == "__main__":
    main()
