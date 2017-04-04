from pprint import *

def read_google(filename):
    data = dict()


    with open(filename, "r") as fin:

        system_desc = next(fin)
        number_of_videos, number_of_endpoints, number_of_requests, number_of_caches, cache_size= system_desc.split(" ")
        number_of_videos = int(number_of_videos)
        number_of_endpoints = int(number_of_endpoints)
        number_of_requests = int(number_of_requests)
        number_of_caches = int(number_of_caches)
        cache_size = int(cache_size)
        video_ed_request = dict()
        video_size_desc = next(fin).strip().split(" ")
        for i in range(len(video_size_desc)):
            video_size_desc[i] = int(video_size_desc[i])
        for i in range(number_of_videos):
            video_ed_request[i] = {}
        ed_cache_list = []

        ### CACHE SECTION

        ep_to_cache_latency = [] 

        ep_to_dc_latency = [] 
        for i in range(number_of_endpoints):


            ep_to_dc_latency.append([])
            ep_to_cache_latency.append([])

            dc_latency, number_of_cache_i = next(fin).strip().split(" ")
            dc_latency = int(dc_latency)
            number_of_cache_i = int(number_of_cache_i)

            ep_to_dc_latency[i] = dc_latency

            for j in range(number_of_caches):
                ep_to_cache_latency[i].append(ep_to_dc_latency[i]+1)

            cache_list = []
            for j in range(number_of_cache_i):
                cache_id, latency = next(fin).strip().split(" ")
                cache_id = int(cache_id)
                cache_list.append(cache_id)
                latency = int(latency)
                ep_to_cache_latency[i][cache_id] = latency

            ed_cache_list.append(cache_list)

        ### REQUEST SECTION
        for i in range(number_of_requests):
            video_id, ed_id, requests = next(fin).strip().split(" ")
            video_id, ed_id, requests = int(video_id), int(ed_id), int(requests)
            # video_ed_request[(video_id,ed_id)] = requests
            video_ed_request[video_id][ed_id] = [requests, ep_to_dc_latency[ed_id]]

        mysize = len(video_ed_request)
        for i in range(mysize):
            if not video_ed_request[i]:
                del video_ed_request[i]



    data["number_of_videos"] = number_of_videos
    data["number_of_endpoints"] = number_of_endpoints
    data["number_of_requests"] = number_of_requests
    data["number_of_caches"] = number_of_caches
    data["cache_size"] = cache_size
    data["video_size_desc"] = video_size_desc
    data["ep_to_dc_latency"] = ep_to_dc_latency
    data["ep_to_cache_latency"] = ep_to_cache_latency # faulty - will list latencies for ep/caches that aren't connected
    data["ed_cache_list"] = ed_cache_list # lists the caches that each endpoint is connected to
    data["video_ed_request"] = video_ed_request # format is as follows: video {endpoint: [requests, min_latency]}

    return data


if __name__=="__main__":
    data = read_google("input/kittens.in")
    # print(data["number_of_requests"])
    # sum = 0
    # for i in data["video_ed_request"]:
    #     sum += int(data["video_ed_request"][i])
    # print("number of individual requests=", sum, " which is different from the number of request descriptions ", data["number_of_requests"])
    print("Number of caches:", data["number_of_caches"])
    print("Number of endpoints:", data["number_of_endpoints"])

