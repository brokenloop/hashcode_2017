from input.read_input import read_google
from pprint import *
import random


def score(solution, data):

    # time taken to stream all videos from datacentre
    time_saved = 0
    total_requests = 0

    # form of request is as follows: (video, endpoint): num_of_requests
    for video in data["video_ed_request"]:
        for endpoint in data["video_ed_request"][video]:

            num_of_requests = data["video_ed_request"][video][endpoint][0]
            dc_latency = data["ep_to_dc_latency"][endpoint]

            # list of caches connected to an endpoint
            connections = data["ed_cache_list"][endpoint]
            # list of latencies of caches with video
            caches = [dc_latency,]

            # find lowest latency cache with video.
            # if ep and cache have no connection, nothing happens
            for cache in connections:
                if solution[cache][video] == 1:
                    caches.append(data["ep_to_cache_latency"][endpoint][cache])

            # check whether the smallest latency among the connected caches is smaller than the currently stored smallest latency
            # if it is, the currently stored smallest latency is updated
            smallest_lat = data["video_ed_request"][video][endpoint][1]
            min_cache = min(caches)
            if min_cache < smallest_lat:
                data["video_ed_request"][video][endpoint][1] = min_cache

            time_saved += ((dc_latency - min_cache) * num_of_requests)
            total_requests += num_of_requests


    return (time_saved * 1000) // total_requests



def score_change(video, cache, data):

    if video not in data["video_ed_request"]:
        return 0

    # time taken to stream all videos from datacentre
    time_saved = 0

    for endpoint in data["video_ed_request"][video]:

        num_of_requests = data["video_ed_request"][video][endpoint][0]

        # list of caches connected to an endpoint
        connections = data["ed_cache_list"][endpoint]


        if cache in connections:
            current_smallest = data["video_ed_request"][video][endpoint][1]
            cache_lat = data["ep_to_cache_latency"][endpoint][cache]
            if cache_lat < current_smallest:
                time_saved += (current_smallest - cache_lat) * num_of_requests

    return time_saved


def update_min_latency(video, cache, data):

    for endpoint in data["video_ed_request"][video]:

        # list of caches connected to an endpoint
        connections = data["ed_cache_list"][endpoint]

        if cache in connections:
            current_smallest = data["video_ed_request"][video][endpoint][1]
            cache_lat = data["ep_to_cache_latency"][endpoint][cache]
            if cache_lat < current_smallest:
                data["video_ed_request"][video][endpoint][1] = cache_lat


def generate_solution(data):
    grid = []
    cache_contents = {}
    capacity = data["cache_size"]

    for i in range(data["number_of_caches"]):
        cache_contents[i] = 0
        row = []
        for j in range(data["number_of_videos"]):
            if (cache_contents[i] + data["video_size_desc"][j] < capacity):
                row.append(random.randint(0, 1))
                cache_contents[i] += data["video_size_desc"][j]
            else:
                row.append(0)
        grid.append(row)

    return grid, cache_contents


def generate_empty(data):
    grid = []
    cache_contents = {}

    for i in range(data["number_of_caches"]):
        cache_contents[i] = 0
        row = []
        for j in range(data["number_of_videos"]):
            row.append(0)
        grid.append(row)

    return grid, cache_contents


def check_validity(solution, data):

    caches = data["number_of_caches"]
    videos = data["number_of_videos"]

    for i in range(caches):
        total = 0
        for j in range(videos):
            if solution[i][j] == 1:
                total += data["video_size_desc"][j]
        if total > data["cache_size"]:
            return False
    else:
        return True

def valid_move(sol, cache, video, cache_contents, data):
    if sol[cache][video] == 1:
        return False
    return (cache_contents[cache] + data["video_size_desc"][video] <= data["cache_size"])


def hill_climb(sol, cache_contents, data):

    move_found = True
    while move_found:
        best_score = 0
        best_move = []
        move_found = False

        for i in range(len(sol)):
            for j in range(len(sol[0])):
                if valid_move(sol, i, j, cache_contents, data):

                    # have to order these backwards because of how the scoring function works
                    newscore = score_change(j, i, data)
                    if newscore > best_score:
                        best_score = newscore
                        best_move = [i, j]
                        move_found = True

        if move_found:
            print("Best move is", best_move, "with score:", best_score)
            cache, video = best_move[0], best_move[1]
            sol[cache][video] = 1
            cache_contents[cache] += data["video_size_desc"][video]

            # need to do this to reset the minimum latency for each request.
            # test which one is faster
            # results: It doesn't make much of a difference. update_min_latency is about 5-10% faster.
            update_min_latency(video, cache, data)
            # score(sol, data)



if __name__=="__main__":

    data = read_google("input/videos_worth_spreading.in")
    # me_at_the_zoo = 516740


    # sample solution given in hashcode brief - works for example.in
    solution = [[0, 0, 1, 0, 0],
                [0, 1, 0, 1, 0],
                [1, 1, 0, 0, 0]]

    print("test")
    newsol, newsol_contents = generate_solution(data)
    print("original score:", score(newsol, data))
    # hill_climb(newsol, newsol_contents, data)
    # print("final score:", score(newsol, data))



