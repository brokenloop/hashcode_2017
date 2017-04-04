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


def score_change(solution, video, cache, cache_contents, data):

    # time taken to stream all videos from datacentre
    time_saved = 0
    total_requests = 0

    # form of request is as follows: (video, endpoint): num_of_requests
    for i in range(data["number_of_endpoints"]):
        key = (str(video), str(i))
        if key in data["video_ed_request"]:
            endpoint = i
            num_of_requests = int(data["video_ed_request"][key])

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

            time_saved += ((dc_latency - min(caches)) * num_of_requests)
            total_requests += num_of_requests

    return (time_saved * 1000) // total_requests



def hill_climb(solution, contents, data):"""
    highest = 0
    for cache in caches:
        for video in videos:
            check validity of change (using contents)
            check score of change
            if score is higher than highest:
                record change
                change score
    """




if __name__=="__main__":

    data = read_google("input/me_at_the_zoo.in")


    # sample solution given in hashcode brief - works for example.in
    solution = [[0, 0, 1, 0, 0],
                [0, 1, 0, 1, 0],
                [1, 1, 0, 0, 0]]

    newsol, newsol_contents = generate_solution(data)
    print(score(newsol, data))


