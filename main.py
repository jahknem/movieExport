# This python script recursively runs pymediainfo on all media files in a directory. The subdirectories of the directory are named after the movie they contain. For each unique movie, a struct is created, containing a string with the title of the movie and an array. The array is an array of tuples, containing the absolute path to each file and the outputs of pymediainfo for the corresponding file. 
# The resulting struct should look like this: {movie_title: [(path, movie), (path, movie), ...], movie_title: [(path, movie), (path, movie), ...]}. These structs are then appended to an array movies.
# The script then checks each array if a movie exists which has a german audio track. If multiple movies exist, the one with the highest resolution is chosen. If no movie with a german audio track exists, the one with the highest resolution is chosen. 
# For each of these movies the path is then appended to the text file "movies.txt".

import os
import subprocess
import re
import sys
import pymediainfo
import json
from tabulate import tabulate

# This function recursively runs pymediainfo on all media files in a directory. The subdirectories of the directory are named after the movie they contain. For each unique movie, a struct is created, containing a string with the title of the movie and an array. The array is an array of tuples, containing the absolute path to each file and the outputs of pymediainfo for the corresponding file. 
# The resulting struct should look like this: {movie_title: [(path, movie), (path, movie), ...], movie_title: [(path, movie), (path, movie), ...]}. These structs are then appended to an array movies.
def get_movie_paths(directory):
    movies = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(('.mp4', '.mkv', '.avi', '.m4v')):
                path = os.path.join(root, file)
                movie_info = pymediainfo.MediaInfo.parse(path)
                movie_title = root.split('/')[-1]
                movie_struct = {movie_title: [(path, movie_info)]}
                if movies:
                    # Check every struct in movies if it has the same movie_title
                    for movie in movies:
                        if movie_title in movie:
                            # If it does, append the path and movie to the array
                            movie[movie_title].append((path, movie))
                            # Print debug statement showing which movie has been added and how many files it has.
                            print("Added " + movie_title + " with " + str(len(movie[movie_title])) + " files")
                            break
                    else:
                        # If it doesn't, append a new struct to movies
                        movies.append(movie_struct)
                        # Print debug statement showing which movie has been added and how many files it has.
                        print("Added " + movie_title + " with 1 file")
                else:
                    movies.append(movie_struct)
                    # Print debug statement showing which movie has been added and how many files it has.
                    print("Added " + movie_title + " with 1 file")
    return movies

def get_files_with_either_german_audio_track_or_highest_resolution(movies):
    # Check each movie if it has a german audio track. If it does, append it to the array movies_with_german_audio_track_or_highest_res
    movies_with_german_audio_track_or_highest_res = []
    for movie in movies:
        movies_with_german_audio_track = get_files_with_german_audio_track(movie)
        if movies_with_german_audio_track:
            movies_with_german_audio_track_or_highest_res.append(get_file_with_highest_bitrate(movies_with_german_audio_track))
        else:
            movies_with_german_audio_track_or_highest_res.append(get_file_with_highest_bitrate(movie))
    return movies_with_german_audio_track_or_highest_res


# From a struct of a movie, return a struct with only the files which have a german audio track
def get_files_with_german_audio_track(movie):
    movies_with_german_audio_track = []
    for name, file_array in movie.items():
        for path, mediainfo in file_array:
            for track in mediainfo.audio_tracks:
                if track.track_type == "Audio" and track.language == "ger"|"deu"|"de"|"de_DE"|"de-DE"|"german"|"deutsch"|"German"|"Deutsch":
                    movies_with_german_audio_track.append({name, [(path, mediainfo)]})
    return movies_with_german_audio_track

# From a struct of a movie, return a struct with only the file with the highest resolution
def get_file_with_highest_bitrate(movie):
    current_contender = None
    for name, file_array in movie.items():
        for path, mediainfo in file_array:
            for track in mediainfo.video_tracks:
                if current_contender:
                    if track.maximum_bit_rate > current_contender[2]:
                        current_contender = {name, [(path, mediainfo)], track.maximum_bit_rate}
                    else:
                        current_contender = {name, [(path, mediainfo)], track.maximum_bit_rate}

# main function which parsers first argument as root directory
def main():
    directory = sys.argv[1]
    movies = get_movie_paths(directory)
    # Print all movies which have more than one file as a table of names and amount of files
    print("Movies with more than one file:")
    movies_with_multiple_files = []
    for movie in movies:
        for key, value in movie.items():
            if len(value) > 1:
                movies_with_multiple_files.append(movie)
    print (tabulate(movies_with_multiple_files, headers=['Movie', 'Files']))

    filtered_movies = get_files_with_either_german_audio_track_or_highest_resolution(movies)
    # Print filtered movies as a table of names and paths
    print("Filtered movies:")
    print (tabulate(filtered_movies, headers=['Movie', 'Path'], tablefmt="fancy_grid"))


    # Print movies to movies.json
    with open('movies.json', 'w') as f:
        f.write(json.dumps(movies))


if __name__ == "__main__":
    main()