To use netflix.py:

- Run the command "python netflix.py" from the command line.
- When the program displays the prompt "Enter the name of the file containing
  your training data:" type in the name of the file containing your training
  data.
- When the program displays the prompt "Enter the name of the file containing
  the titles and years of the movies:" type in the name of the file containing
  the movie titles/years of the movies.
- After a short wait, you will be presented with a table and the option to
  select 1 of 3 options.
  - Option 1 allows you to feed the program a text file with new data and it
    will attempt to predict ratings.
  - Option 2 allows you to feed in a user ID and a year, and it will produce a
    list of the movies from that year the user has not watched and rank them by
    predicted rating.
  - Option 3 exits.

Some notes about netflix.py:

If trained with TrainingSet.txt, the algorithm is not as accurate as I'd like
it to be (it classifies within about 1.5 of the real rating). This is not as
accurate as I would like it to be, but I'm running out of time to figure out
what is causing the problems.

If trained using a larger set, it is much, much more accurate.

The algorithm is incredibly slow because of the weight calculations. I tried
pre-calculating the weights and then classifying, which was much faster when
classifying, but the amount of memory used was over 10 GB, so I abandoned that.
